"""
Base TTS Engine - Abstract Interface

Interface padrão para todos os motores TTS no Speakerbot.
Garante que novos engines implementem os métodos necessários.

Engines disponíveis:
- XTTSEngine (xtts_engine.py)
- StyleTTS2Engine (stylets2_engine.py)
- KokoroEngine (kokoro_engine.py)
- VITS2Engine (vits2_engine.py)
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseTTSEngine(ABC):
    """
    Interface abstrata para todos os motores TTS.
    
    Todos os engines devem herdar desta classe e implementar
    os métodos abstratos.
    """
    
    def __init__(self, device: str = "cuda", model_name: str = None):
        """
        Inicializar engine.
        
        Args:
            device: "cuda" ou "cpu"
            model_name: Nome do modelo (específico por engine)
        """
        self.device = device
        self.model_name = model_name
        self.loaded = False
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def load_model(self) -> None:
        """
        Carregar modelo do engine.
        
        Deve:
        - Carregar modelo do disco ou download
        - Mover para GPU se disponível
        - Definir self.loaded = True
        
        Raises:
            RuntimeError: Se falhar ao carregar
        """
        pass
    
    @abstractmethod
    def unload_model(self) -> None:
        """
        Descarregar modelo (liberar memória).
        
        Deve:
        - Liberar modelo da GPU
        - Limpar cache
        - Definir self.loaded = False
        """
        pass
    
    @abstractmethod
    def synthesize(
        self,
        text: str,
        language: str = "pt",
        voice: str = "default",
        speed: float = 1.0,
        **kwargs
    ) -> Tuple[bytes, int]:
        """
        Sintetizar texto em áudio.
        
        Args:
            text: Texto a sintetizar
            language: Código do idioma (ex: "pt", "pt-BR", "en")
            voice: Nome ou ID da voz a usar
            speed: Velocidade de fala (0.5 a 2.0)
            **kwargs: Parâmetros específicos do engine
        
        Returns:
            Tuple[bytes, int]: (áudio WAV em bytes, sample_rate)
        
        Raises:
            ValueError: Se texto vazio ou parâmetros inválidos
            RuntimeError: Se síntese falhar
        """
        pass
    
    @abstractmethod
    def get_available_languages(self) -> List[str]:
        """
        Retornar lista de idiomas suportados.
        
        Returns:
            List[str]: Lista de códigos de idioma
                Exemplo: ["pt", "pt-BR", "pt-PT", "en", "es"]
        """
        pass
    
    @abstractmethod
    def get_available_voices(self, language: str = None) -> List[str]:
        """
        Retornar lista de vozes disponíveis.
        
        Args:
            language: Filtrar vozes por idioma (opcional)
        
        Returns:
            List[str]: Lista de nomes/IDs de vozes
                Exemplo: ["default", "female", "male"]
        """
        pass
    
    @abstractmethod
    def clone_voice(
        self,
        voice_name: str,
        reference_audio_paths: List[str],
        language: str = "pt"
    ) -> bool:
        """
        Clonar voz a partir de arquivo(s) de referência.
        
        Args:
            voice_name: Nome para a voz clonada
            reference_audio_paths: Lista de caminhos de áudio (WAV)
            language: Idioma da voz
        
        Returns:
            bool: True se sucesso, False caso contrário
        
        Raises:
            FileNotFoundError: Se arquivo de referência não existe
            ValueError: Se arquivos inválidos
        """
        pass
    
    def get_engine_info(self) -> Dict[str, Any]:
        """
        Retornar informações do engine (metadados).
        
        Returns:
            Dict com informações:
            {
                "name": "xtts-v2",
                "label": "XTTS v2 (Premium)",
                "speed": "medium",  # "slow", "medium", "fast", "very_fast"
                "quality": "excellent",  # "good", "excellent"
                "gpu_vram_mb": 6000,
                "gpu_vram_label": "6GB",
                "languages": 16,
                "supports_cloning": True
            }
        """
        return {
            "name": self.get_engine_name(),
            "label": self.get_engine_label(),
            "speed": self.get_engine_speed(),
            "quality": self.get_engine_quality(),
            "gpu_vram_mb": self.get_gpu_vram_required(),
            "gpu_vram_label": self.get_gpu_vram_label(),
            "languages": len(self.get_available_languages()),
            "supports_cloning": self.supports_voice_cloning()
        }
    
    def get_engine_name(self) -> str:
        """Retornar nome técnico do engine (ex: "xtts-v2")"""
        return self.__class__.__name__.replace("Engine", "").lower()
    
    def get_engine_label(self) -> str:
        """Retornar label amigável do engine (ex: "XTTS v2 (Premium)")"""
        return self.__class__.__name__
    
    def get_engine_speed(self) -> str:
        """Retornar velocidade relativa: 'slow', 'medium', 'fast', 'very_fast'"""
        return "medium"
    
    def get_engine_quality(self) -> str:
        """Retornar qualidade relativa: 'good', 'excellent'"""
        return "excellent"
    
    def get_gpu_vram_required(self) -> int:
        """Retornar VRAM requerida em MB"""
        return 4000  # Default 4GB
    
    def get_gpu_vram_label(self) -> str:
        """Retornar label de VRAM (ex: "2GB")"""
        vram_mb = self.get_gpu_vram_required()
        vram_gb = vram_mb / 1000
        return f"{vram_gb:.0f}GB"
    
    def supports_voice_cloning(self) -> bool:
        """Retornar se engine suporta clonagem de voz"""
        return False
    
    def validate_text(self, text: str) -> bool:
        """
        Validar texto antes de síntese.
        
        Args:
            text: Texto a validar
        
        Returns:
            bool: True se válido, False caso contrário
        """
        if not text or not isinstance(text, str):
            return False
        if len(text.strip()) == 0:
            return False
        return True
    
    def validate_language(self, language: str) -> bool:
        """Validar se idioma é suportado"""
        return language in self.get_available_languages()
    
    def validate_voice(self, voice: str, language: str = None) -> bool:
        """Validar se voz existe"""
        voices = self.get_available_voices(language)
        return voice in voices
    
    def __repr__(self) -> str:
        """Representação string do engine"""
        return f"{self.__class__.__name__}(device={self.device}, loaded={self.loaded})"


class EngineRegistry:
    """
    Registrador de engines disponíveis.
    
    Mantém referência de todos os engines e permite seleção.
    """
    
    _engines: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, engine_class: type) -> None:
        """Registrar novo engine"""
        cls._engines[name] = engine_class
        logger.info(f"Engine registered: {name}")
    
    @classmethod
    def get(cls, name: str) -> Optional[type]:
        """Obter classe do engine por nome"""
        return cls._engines.get(name)
    
    @classmethod
    def get_all(cls) -> Dict[str, type]:
        """Obter todos os engines registrados"""
        return cls._engines.copy()
    
    @classmethod
    def is_available(cls, name: str) -> bool:
        """Verificar se engine está registrado"""
        return name in cls._engines


def register_engine(name: str):
    """
    Decorator para registrar engine automaticamente.
    
    Uso:
    @register_engine("xtts-v2")
    class XTTSEngine(BaseTTSEngine):
        ...
    """
    def decorator(cls):
        EngineRegistry.register(name, cls)
        return cls
    return decorator
