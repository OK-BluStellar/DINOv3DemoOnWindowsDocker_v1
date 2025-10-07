from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import torch.nn.functional as F
from transformers import AutoImageProcessor, AutoModel
from PIL import Image
import numpy as np
import io
import base64
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_NAME = "facebook/dinov2-base"
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
processor = None
model = None

@app.on_event("startup")
async def load_model():
    global processor, model
    print(f"Loading DINOv2 model: {MODEL_NAME}")
    processor = AutoImageProcessor.from_pretrained(MODEL_NAME)
    model = AutoModel.from_pretrained(MODEL_NAME)
    model = model.to(device)
    model.eval()
    print(f"Model loaded successfully on {device}")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/upload_and_segment")
async def upload_and_segment(
    file: UploadFile = File(...),
    x_min: int = Form(...),
    y_min: int = Form(...),
    x_max: int = Form(...),
    y_max: int = Form(...)
):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        original_width, original_height = image.size
        
        inputs = processor(images=image, return_tensors="pt")
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            outputs = model(**inputs)
        
        patch_features = outputs.last_hidden_state[0, 1:]
        
        patch_size = model.config.patch_size
        num_patches = int(patch_features.shape[0] ** 0.5)
        num_patches_h = num_patches
        num_patches_w = num_patches
        processed_size = num_patches * patch_size
        
        patch_features = patch_features.view(num_patches_h, num_patches_w, -1)
        
        scale_h = processed_size / original_height
        scale_w = processed_size / original_width
        
        scaled_y_min = int(y_min * scale_h)
        scaled_y_max = int(y_max * scale_h)
        scaled_x_min = int(x_min * scale_w)
        scaled_x_max = int(x_max * scale_w)
        
        patch_y_min = max(0, scaled_y_min // patch_size)
        patch_y_max = min(num_patches_h, (scaled_y_max + patch_size - 1) // patch_size)
        patch_x_min = max(0, scaled_x_min // patch_size)
        patch_x_max = min(num_patches_w, (scaled_x_max + patch_size - 1) // patch_size)
        
        reference_patches = patch_features[patch_y_min:patch_y_max, patch_x_min:patch_x_max]
        reference_feature = reference_patches.mean(dim=[0, 1])
        
        patch_features_flat = patch_features.view(-1, patch_features.shape[-1])
        reference_feature = reference_feature.unsqueeze(0)
        
        patch_features_norm = F.normalize(patch_features_flat, p=2, dim=1)
        reference_feature_norm = F.normalize(reference_feature, p=2, dim=1)
        
        similarity = torch.mm(patch_features_norm, reference_feature_norm.t()).squeeze()
        similarity_map = similarity.view(num_patches_h, num_patches_w)
        
        similarity_map_tensor = similarity_map.unsqueeze(0).unsqueeze(0)
        upsampled_map_tensor = F.interpolate(
            similarity_map_tensor,
            size=(original_height, original_width),
            mode='bilinear',
            align_corners=False
        )
        upsampled_map = upsampled_map_tensor.squeeze().cpu().numpy()
        
        upsampled_map = (upsampled_map - upsampled_map.min()) / (upsampled_map.max() - upsampled_map.min() + 1e-8)
        mask_colored = (upsampled_map * 255).astype(np.uint8)
        mask_image = Image.fromarray(mask_colored, mode='L')
        
        buffered = io.BytesIO()
        mask_image.save(buffered, format="PNG")
        mask_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return JSONResponse(content={
            "mask_image": f"data:image/png;base64,{mask_base64}",
            "metadata": {
                "patch_size": patch_size,
                "num_patches_h": num_patches_h,
                "num_patches_w": num_patches_w,
                "original_size": [original_width, original_height],
                "reference_region": {
                    "x_min": x_min,
                    "y_min": y_min,
                    "x_max": x_max,
                    "y_max": y_max
                }
            }
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )
