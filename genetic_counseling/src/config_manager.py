from pathlib import Path
from typing import Any, Dict, Optional
from omegaconf import DictConfig, OmegaConf
import hydra
from hydra import compose, initialize_config_dir
from hydra.core.global_hydra import GlobalHydra


class ConfigManager:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir).absolute()
        self.cfg: Optional[DictConfig] = None
        self._initialize()
    
    def _initialize(self):
        if GlobalHydra.instance().is_initialized():
            GlobalHydra.instance().clear()
        
        initialize_config_dir(
            config_dir=str(self.config_dir),
            version_base=None
        )
        self.cfg = compose(config_name="config")
    
    def get_config(self) -> DictConfig:
        return self.cfg
    
    def update_llm_config(self, model_name: Optional[str] = None, temperature: Optional[float] = None, 
                         max_tokens: Optional[int] = None, top_p: Optional[float] = None):
        if model_name is not None:
            self.cfg.llm.model_name = model_name
        if temperature is not None:
            self.cfg.llm.temperature = temperature
        if max_tokens is not None:
            self.cfg.llm.max_tokens = max_tokens
        if top_p is not None:
            self.cfg.llm.top_p = top_p
    
    def update_system_prompt(self, prompt: str):
        self.cfg.prompt.system_prompt = prompt
    
    def get_llm_config(self) -> Dict[str, Any]:
        return {
            "model_name": self.cfg.llm.model_name,
            "temperature": self.cfg.llm.temperature,
            "max_tokens": self.cfg.llm.max_tokens,
            "top_p": self.cfg.llm.top_p,
            "base_url": self.cfg.llm.ollama_base_url
        }
    
    def get_system_prompt(self) -> str:
        return self.cfg.prompt.system_prompt
    
    def reload_config(self, llm_preset: Optional[str] = None, prompt_preset: Optional[str] = None):
        GlobalHydra.instance().clear()
        
        overrides = []
        if llm_preset:
            overrides.append(f"llm={llm_preset}")
        if prompt_preset:
            overrides.append(f"prompt={prompt_preset}")
        
        initialize_config_dir(
            config_dir=str(self.config_dir),
            version_base=None
        )
        self.cfg = compose(config_name="config", overrides=overrides)
