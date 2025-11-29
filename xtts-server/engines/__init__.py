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
from .stylets2_engine import StyleTTS2Engine

__all__ = [
    "BaseTTSEngine",
    "EngineRegistry",
    "register_engine",
    "XTTSEngine",
    "StyleTTS2Engine",
]
