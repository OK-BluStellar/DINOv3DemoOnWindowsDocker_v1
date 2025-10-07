import { useState, useRef, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Slider } from '@/components/ui/slider'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Upload, Loader2 } from 'lucide-react'
import './App.css'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

interface Rectangle {
  x: number
  y: number
  width: number
  height: number
}

function App() {
  const [uploadedImage, setUploadedImage] = useState<string | null>(null)
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [rectangle, setRectangle] = useState<Rectangle | null>(null)
  const [isDrawing, setIsDrawing] = useState(false)
  const [startPoint, setStartPoint] = useState<{ x: number; y: number } | null>(null)
  const [maskImage, setMaskImage] = useState<string | null>(null)
  const [opacity, setOpacity] = useState([0.6])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const imageRef = useRef<HTMLImageElement>(null)

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setImageFile(file)
      const reader = new FileReader()
      reader.onload = (event) => {
        setUploadedImage(event.target?.result as string)
        setRectangle(null)
        setMaskImage(null)
        setError(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!canvasRef.current || !imageRef.current) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const scaleX = imageRef.current.naturalWidth / rect.width
    const scaleY = imageRef.current.naturalHeight / rect.height
    
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY
    
    setStartPoint({ x, y })
    setIsDrawing(true)
    setRectangle(null)
  }

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDrawing || !startPoint || !canvasRef.current || !imageRef.current) return
    
    const canvas = canvasRef.current
    const rect = canvas.getBoundingClientRect()
    const scaleX = imageRef.current.naturalWidth / rect.width
    const scaleY = imageRef.current.naturalHeight / rect.height
    
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY
    
    const width = x - startPoint.x
    const height = y - startPoint.y
    
    setRectangle({
      x: Math.min(startPoint.x, x),
      y: Math.min(startPoint.y, y),
      width: Math.abs(width),
      height: Math.abs(height)
    })
  }

  const handleMouseUp = () => {
    setIsDrawing(false)
    setStartPoint(null)
  }

  const handleSegment = async () => {
    if (!imageFile || !rectangle || !imageRef.current) return
    
    setIsLoading(true)
    setError(null)
    
    try {
      const formData = new FormData()
      formData.append('file', imageFile)
      formData.append('x_min', Math.floor(rectangle.x).toString())
      formData.append('y_min', Math.floor(rectangle.y).toString())
      formData.append('x_max', Math.floor(rectangle.x + rectangle.width).toString())
      formData.append('y_max', Math.floor(rectangle.y + rectangle.height).toString())
      
      const response = await fetch(`${API_URL}/api/upload_and_segment`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) {
        throw new Error('セグメンテーションに失敗しました')
      }
      
      const data = await response.json()
      setMaskImage(data.mask_image)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    if (!canvasRef.current || !imageRef.current || !uploadedImage) return
    
    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    
    const img = imageRef.current
    canvas.width = img.naturalWidth
    canvas.height = img.naturalHeight
    
    ctx.clearRect(0, 0, canvas.width, canvas.height)
    
    if (maskImage) {
      const maskImg = new Image()
      maskImg.onload = () => {
        ctx.globalAlpha = opacity[0]
        ctx.drawImage(maskImg, 0, 0, canvas.width, canvas.height)
        ctx.globalAlpha = 1.0
        
        if (rectangle) {
          ctx.strokeStyle = '#00ff00'
          ctx.lineWidth = 3
          ctx.strokeRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
        }
      }
      maskImg.src = maskImage
    } else if (rectangle) {
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 3
      ctx.strokeRect(rectangle.x, rectangle.y, rectangle.width, rectangle.height)
    }
  }, [uploadedImage, rectangle, maskImage, opacity])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <Card className="mb-8">
          <CardHeader>
            <CardTitle className="text-3xl font-bold text-center">
              DINOv3 Zero-Shot セグメンテーションデモ
            </CardTitle>
            <CardDescription className="text-center text-base">
              DINOv3の強力な密な特徴量（Dense Features）を使用して、学習なし（Zero-Shot）で画像セグメンテーションを実行します。
              参照領域を選択すると、類似した領域が自動的に検出されます。
            </CardDescription>
          </CardHeader>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>画像とセグメンテーション結果</CardTitle>
            </CardHeader>
            <CardContent>
              {!uploadedImage ? (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
                  <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                  <label htmlFor="image-upload" className="cursor-pointer">
                    <span className="text-blue-600 hover:text-blue-500">
                      画像をアップロード
                    </span>
                    <input
                      id="image-upload"
                      type="file"
                      accept="image/*"
                      onChange={handleImageUpload}
                      className="hidden"
                    />
                  </label>
                </div>
              ) : (
                <div className="relative">
                  <div className="relative inline-block">
                    <img
                      ref={imageRef}
                      src={uploadedImage}
                      alt="Uploaded"
                      className="max-w-full h-auto"
                    />
                    <canvas
                      ref={canvasRef}
                      className="absolute top-0 left-0 w-full h-full cursor-crosshair"
                      onMouseDown={handleMouseDown}
                      onMouseMove={handleMouseMove}
                      onMouseUp={handleMouseUp}
                      onMouseLeave={handleMouseUp}
                    />
                  </div>
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>コントロール</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              {uploadedImage && (
                <>
                  <div>
                    <label className="block text-sm font-medium mb-2">
                      1. 参照領域を選択
                    </label>
                    <p className="text-sm text-gray-600">
                      画像上でドラッグして矩形を描画してください
                    </p>
                  </div>

                  <div>
                    <Button
                      onClick={handleSegment}
                      disabled={!rectangle || isLoading}
                      className="w-full"
                    >
                      {isLoading ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          処理中...
                        </>
                      ) : (
                        '2. セグメンテーション実行'
                      )}
                    </Button>
                  </div>

                  {maskImage && (
                    <div>
                      <label className="block text-sm font-medium mb-2">
                        マスクの透明度: {Math.round(opacity[0] * 100)}%
                      </label>
                      <Slider
                        value={opacity}
                        onValueChange={setOpacity}
                        min={0}
                        max={1}
                        step={0.1}
                        className="w-full"
                      />
                    </div>
                  )}

                  <Button
                    variant="outline"
                    onClick={() => {
                      setUploadedImage(null)
                      setImageFile(null)
                      setRectangle(null)
                      setMaskImage(null)
                      setError(null)
                    }}
                    className="w-full"
                  >
                    リセット
                  </Button>
                </>
              )}

              {error && (
                <Alert variant="destructive">
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
            </CardContent>
          </Card>
        </div>

        <Card className="mt-8">
          <CardHeader>
            <CardTitle>DINOv3について</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-gray-700">
              DINOv3（DINO v2）は、Meta AIが開発した自己教師あり学習による視覚変換モデルです。
              このデモでは、DINOv3が生成する密な特徴量を使用して、参照領域と類似した領域をコサイン類似度で検出します。
              事前に特定のタスクで学習することなく、強力なセグメンテーション機能を提供します。
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
