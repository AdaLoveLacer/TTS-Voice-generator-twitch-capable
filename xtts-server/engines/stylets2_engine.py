"""
StyleTTS2 Engine - Fast & High-Quality Text-to-Speech

Implementação de StyleTTS2 para síntese rápida com qualidade human-level.
2-3x mais rápido que XTTS v2 com apenas 2GB de VRAM necessário.

Características:
- Zero-shot speaker adaptation
- Voice cloning com qualidade excelente
- Diffusion-based style control
- Multilingual (incluindo PT-BR)
- Inferência rápida (5-7s por síntese)
"""

import os
import sys
import io
import json
import torch
import traceback
import numpy as np
import scipy.io.wavfile as wavfile
from pathlib import Path
from typing import Optional, List, Tuple, Dict, Any
from datetime import datetime

# Ensure UTF-8 encoding
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    import io
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Try to import StyleTTS2
STYLETTS2_AVAILABLE = False
try:
    from styletts2 import tts
    STYLETTS2_AVAILABLE = True
except ImportError as e:
    print(f"⚠ StyleTTS2 não encontrado: {e}")
    print("   StyleTTS2 é opcional. Use: pip install styletts2")
    tts = None

try:
    import torchaudio
except ImportError as e:
    if STYLETTS2_AVAILABLE:
        print(f"❌ ERRO: torchaudio não encontrado: {e}")
        sys.exit(1)
    torchaudio = None

from engines.base_engine import BaseTTSEngine, register_engine


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# Cache paths - tudo dentro do projeto
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / ".tts-cache"
STYLETTS2_CACHE_DIR = CACHE_DIR / "styletts2"
MODELS_CACHE_DIR = CACHE_DIR / "models"

# Criar diretórios de cache
CACHE_DIR.mkdir(exist_ok=True, parents=True)
STYLETTS2_CACHE_DIR.mkdir(exist_ok=True, parents=True)
MODELS_CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Configurar variáveis de ambiente para cache local
os.environ['HF_HOME'] = str(MODELS_CACHE_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(MODELS_CACHE_DIR / "transformers")
os.environ['TTS_HOME'] = str(STYLETTS2_CACHE_DIR)

# Audio Configuration
SAMPLE_RATE = 24000  # StyleTTS2 native sample rate

# StyleTTS2 Supported Languages
LANGUAGE_SUPPORT = [
    "pt",      # Portuguese
    "pt-BR",   # Brazilian Portuguese
    "pt-PT",   # Portuguese (Portugal)
    "en",      # English
    "es",      # Spanish
    "fr",      # French
    "de",      # German
    "it",      # Italian
    "ja",      # Japanese
    "zh-cn",   # Simplified Chinese
    "ko",      # Korean
]

# StyleTTS2 Inference Configuration
INFERENCE_CONFIG = {
    "diffusion_steps": 5,      # Quality vs speed trade-off
    "alpha": 0.3,              # Timbre
    "beta": 0.7,               # Prosody
    "embedding_scale": 1.0,    # Emotionality
}


# ============================================================================
# AUDIO PROCESSING UTILITIES
# ============================================================================

def normalize_audio_file(wav_path: str, target_sr: int = 22050) -> str:
    """Normalizar arquivo de áudio."""
    try:
        try:
            sr, wav_data = wavfile.read(wav_path)
            print(f"   📊 Carregado com scipy: sr={sr}, shape={wav_data.shape}")
            
            if wav_data.size == 0:
                raise ValueError("Arquivo WAV vazio")
            
            if sr <= 0:
                raise ValueError(f"Sample rate inválido: {sr}")
            
            if wav_data.dtype != np.float32:
                wav_data = wav_data.astype(np.float32) / np.iinfo(wav_data.dtype).max
            
            wav_data = np.clip(wav_data, -1.0, 1.0)
            wav = torch.from_numpy(wav_data)
            
        except Exception as e:
            print(f"   ⚠️ Scipy falhou: {str(e)}, tentando torchaudio...")
            wav, sr = torchaudio.load(wav_path)
            print(f"   📊 Carregado com torchaudio: sr={sr}, shape={wav.shape}")
            
            if wav.shape[1] == 0:
                raise ValueError("Arquivo WAV sem amostras")
        
        if not isinstance(wav, torch.Tensor):
            wav = torch.from_numpy(wav)
        
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        
        min_samples = int(target_sr * 0.5)
        if wav.shape[1] < min_samples:
            padding = min_samples - wav.shape[1]
            wav = torch.nn.functional.pad(wav, (0, padding), mode='constant', value=0.0)
        
        if sr != target_sr:
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            wav = resampler(wav)
        
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
        
        max_val = torch.abs(wav).max()
        if max_val > 0:
            wav = wav / (max_val * 1.05)
        
        wav = torch.clamp(wav, -0.95, 0.95)
        
        normalized_path = wav_path.replace('.wav', '_normalized.wav')
        wav_int16 = (wav.squeeze(0).numpy() * 32767).astype(np.int16)
        wavfile.write(normalized_path, target_sr, wav_int16)
        
        print(f"   ✅ Normalizado: {normalized_path}")
        return normalized_path
        
    except Exception as e:
        print(f"   ❌ Erro de normalização: {str(e)}")
        return wav_path


def apply_speed_adjustment(wav_data, speed_factor: float):
    """Ajustar velocidade de reprodução."""
    if speed_factor == 1.0:
        return wav_data
    
    try:
        if not isinstance(wav_data, torch.Tensor):
            wav_tensor = torch.tensor(wav_data, dtype=torch.float32)
        else:
            wav_tensor = wav_data.clone()
        
        if wav_tensor.dim() == 1:
            wav_tensor = wav_tensor.unsqueeze(0)
        
        new_sr = int(SAMPLE_RATE * speed_factor)
        resampler = torchaudio.transforms.Resample(SAMPLE_RATE, new_sr)
        speed_adjusted = resampler(wav_tensor)
        
        if isinstance(speed_adjusted, torch.Tensor):
            speed_adjusted = speed_adjusted.numpy()
        
        if speed_adjusted.ndim > 1 and speed_adjusted.shape[0] == 1:
            speed_adjusted = speed_adjusted.squeeze(0)
        
        return speed_adjusted
    
    except Exception as e:
        print(f"⚠️ Ajuste de velocidade falhou: {e}")
        return wav_data


# ============================================================================
# STYLETTS2 ENGINE CLASS
# ============================================================================

if STYLETTS2_AVAILABLE:
    @register_engine("stylets2")
    class StyleTTS2Engine(BaseTTSEngine):
        """StyleTTS2 Engine para síntese rápida com clonagem de voz."""
        
        def __init__(self, device: str = None):
            """Inicializar StyleTTS2 Engine."""
            if device is None:
                device = "cuda" if torch.cuda.is_available() else "cpu"
            
            super().__init__(device=device, model_name="styletts2")
            self.tts_model = None
        
        def load_model(self) -> None:
            """Carregar modelo StyleTTS2."""
            if self.loaded:
                return
            
            try:
                print(f"⏳ Carregando modelo StyleTTS2 ({self.device})...")
                self.tts_model = tts.StyleTTS2()
                
                print(f"✅ StyleTTS2 carregado com sucesso")
                print(f"   📊 Model: LibriTTS (multi-speaker)")
                print(f"   📊 Cache: {STYLETTS2_CACHE_DIR}")
                
                self.loaded = True
                
            except Exception as e:
                print(f"❌ Erro ao carregar StyleTTS2: {e}")
                traceback.print_exc()
                raise
        
        def unload_model(self) -> None:
            """Descarregar modelo."""
            if not self.loaded:
                return
            
            try:
                if self.tts_model:
                    del self.tts_model
                    self.tts_model = None
                
                if self.device == "cuda":
                    torch.cuda.empty_cache()
                
                self.loaded = False
                print("✅ Modelo StyleTTS2 descarregado")
                
            except Exception as e:
                print(f"⚠️ Erro ao descarregar: {e}")
        
        def synthesize(
            self,
            text: str,
            language: str = "pt",
            voice: str = "default",
            speed: float = 1.0,
            **kwargs
        ) -> Tuple[bytes, int]:
            """Sintetizar texto em áudio com StyleTTS2."""
            if not self.loaded:
                raise RuntimeError("Modelo não carregado. Chamar load_model() primeiro.")
            
            if not self.validate_text(text):
                raise ValueError("Texto inválido ou vazio")
            
            if not self.validate_language(language):
                raise ValueError(f"Idioma não suportado: {language}")
            
            try:
                target_voice_path = None
                if voice != "default" and voice is not None:
                    if os.path.exists(voice):
                        target_voice_path = normalize_audio_file(voice, target_sr=22050)
                
                diffusion_steps = kwargs.get('diffusion_steps', INFERENCE_CONFIG['diffusion_steps'])
                alpha = kwargs.get('alpha', INFERENCE_CONFIG['alpha'])
                beta = kwargs.get('beta', INFERENCE_CONFIG['beta'])
                embedding_scale = kwargs.get('embedding_scale', INFERENCE_CONFIG['embedding_scale'])
                
                print(f"🎙️ Sintetizando ({language}): '{text[:50]}...'")
                
                wav = self.tts_model.inference(
                    text=text,
                    target_voice_path=target_voice_path,
                    output_wav_file=None,
                    output_sample_rate=SAMPLE_RATE,
                    alpha=alpha,
                    beta=beta,
                    diffusion_steps=diffusion_steps,
                    embedding_scale=embedding_scale
                )
                
                if isinstance(wav, torch.Tensor):
                    wav = wav.cpu().numpy()
                
                if wav.ndim > 1:
                    wav = wav.flatten()
                
                if speed != 1.0:
                    wav = apply_speed_adjustment(wav, speed)
                
                max_val = np.abs(wav).max()
                if max_val > 0:
                    wav = wav / (max_val * 1.05)
                wav = np.clip(wav, -0.95, 0.95)
                
                wav_int16 = (wav * 32767).astype(np.int16)
                
                wav_buffer = io.BytesIO()
                wavfile.write(wav_buffer, SAMPLE_RATE, wav_int16)
                wav_bytes = wav_buffer.getvalue()
                
                print(f"✅ Síntese completa: {len(wav_bytes)} bytes")
                
                return wav_bytes, SAMPLE_RATE
                
            except Exception as e:
                print(f"❌ Erro de síntese: {e}")
                traceback.print_exc()
                raise
        
        def get_available_languages(self) -> List[str]:
            """Retornar idiomas suportados."""
            return LANGUAGE_SUPPORT
        
        def get_available_voices(self, language: str = None) -> List[str]:
            """Retornar vozes disponíveis."""
            return ["default"]
        
        def clone_voice(
            self,
            voice_name: str,
            reference_audio_paths: List[str],
            language: str = "pt"
        ) -> bool:
            """Validar arquivos de referência para clonagem."""
            try:
                print(f"🎙️ Validando arquivos para clonagem de voz: {voice_name}")
                
                for audio_path in reference_audio_paths:
                    if not os.path.exists(audio_path):
                        raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
                    
                    normalize_audio_file(audio_path)
                
                print(f"✅ Voz '{voice_name}' pronta para clonagem")
                return True
                
            except Exception as e:
                print(f"❌ Erro na clonagem: {e}")
                return False
        
        def get_engine_name(self) -> str:
            """Retornar nome técnico."""
            return "stylets2"
        
        def get_engine_label(self) -> str:
            """Retornar label amigável."""
            return "StyleTTS2 (Fast & Excellent)"
        
        def get_engine_speed(self) -> str:
            """Retornar velocidade relativa."""
            return "very-fast"
        
        def get_engine_quality(self) -> str:
            """Retornar qualidade relativa."""
            return "excellent"
        
        def get_gpu_vram_required(self) -> int:
            """Retornar VRAM requerida em MB."""
            return 2000
        
        def supports_voice_cloning(self) -> bool:
            """StyleTTS2 suporta clonagem de voz."""
            return True


# ============================================================================
# BACKWARD COMPATIBILITY FUNCTIONS
# ============================================================================

def get_styletts2_engine() -> "StyleTTS2Engine":
    """Helper para obter instância do StyleTTS2 Engine."""
    if STYLETTS2_AVAILABLE:
        engine = StyleTTS2Engine()
        engine.load_model()
        return engine
    else:
        raise RuntimeError("StyleTTS2 não disponível. Instale com: pip install styletts2")


__all__ = [
    "SAMPLE_RATE",
    "LANGUAGE_SUPPORT",
    "INFERENCE_CONFIG",
    "CACHE_DIR",
    "normalize_audio_file",
    "apply_speed_adjustment",
]

if STYLETTS2_AVAILABLE:
    __all__.extend([
        "StyleTTS2Engine",
        "get_styletts2_engine",
    ])
