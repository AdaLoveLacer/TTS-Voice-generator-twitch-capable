"""
Speakerbot Engines Package

Motores TTS disponíveis:
- XTTS v2 (default) - Melhor qualidade
- StyleTTS2 - Rápido + qualidade excelente
- Kokoro - Ultra-rápido
- VITS2 - Leve + rápido
"""

from .base_engine import BaseTTSEngine, EngineRegistry, register_engine
from .xtts_engine import XTTSEngine

# Tentar importar StyleTTS2Engine, mas não falhar se styletts2 não estiver disponível
try:
    from .stylets2_engine import StyleTTS2Engine
except ImportError as e:
    print(f"⚠ StyleTTS2 não disponível: {e}")
    StyleTTS2Engine = None

__all__ = [
    "BaseTTSEngine",
    "EngineRegistry",
    "register_engine",
    "XTTSEngine",
]

if StyleTTS2Engine is not None:
    __all__.append("StyleTTS2Engine")

