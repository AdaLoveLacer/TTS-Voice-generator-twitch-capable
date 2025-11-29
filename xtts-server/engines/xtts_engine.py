"""
XTTS v2 Engine - Text-to-Speech Implementation

Engine que utiliza XTTS v2 (Coqui) para síntese multilíngue.
Suporta clonagem de voz, voice processing, e otimizações de GPU.

Características:
- Multilingual: 16 idiomas incluindo PT-BR e PT-PT
- Voice Cloning: Clonagem com 1-5 arquivos de referência
- GPU Optimized: CUDA support com fallback para CPU
- Robust: Validação de áudio, error handling, recovery
"""

import os
import io
import sys
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

# Configure torch before importing TTS
try:
    # Monkeypatch torch.load para compatibilidade com TTS models
    original_torch_load = torch.load
    
    def patched_torch_load(f, *args, **kwargs):
        """Patched torch.load que desabilita weights_only para compatibilidade com TTS"""
        kwargs['weights_only'] = False
        return original_torch_load(f, *args, **kwargs)
    
    torch.load = patched_torch_load
    
    from TTS.api import TTS  # type: ignore
    import torchaudio
    
except ImportError as e:
    print(f"❌ ERRO: Dependências TTS não encontradas: {e}")
    sys.exit(1)

from engines.base_engine import BaseTTSEngine, register_engine


# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

# Cache paths - tudo dentro do projeto
PROJECT_ROOT = Path(__file__).parent.parent
CACHE_DIR = PROJECT_ROOT / ".tts-cache"
XTTS_CACHE_DIR = CACHE_DIR / "xtts"
MODELS_CACHE_DIR = CACHE_DIR / "models"

# Criar diretórios de cache
CACHE_DIR.mkdir(exist_ok=True, parents=True)
XTTS_CACHE_DIR.mkdir(exist_ok=True, parents=True)
MODELS_CACHE_DIR.mkdir(exist_ok=True, parents=True)

# Configurar variáveis de ambiente para cache local
os.environ['TTS_HOME'] = str(XTTS_CACHE_DIR)
os.environ['HF_HOME'] = str(MODELS_CACHE_DIR)
os.environ['TRANSFORMERS_CACHE'] = str(MODELS_CACHE_DIR)
os.environ['TORCH_HOME'] = str(CACHE_DIR / "torch")

# Audio Configuration
SAMPLE_RATE = 24000  # XTTS v2 native sample rate
SYNTHESIS_CONFIG = {
    "gpu_enabled": torch.cuda.is_available(),
    "gpu_memory_fraction": 0.8,
    "use_half_precision": torch.cuda.is_available(),
    "batch_processing": False,
    "gpt_cond_len": 12,  # Segundos de áudio para conditioning (3-30s)
    "gpt_cond_chunk_len": 4,
    "max_ref_len": 10
}

LANGUAGE_SUPPORT = [
    "pt",      # Portuguese
    "pt-BR",   # Brazilian Portuguese
    "pt-PT",   # Portuguese (Portugal)
    "en",      # English
    "es",      # Spanish
    "fr",      # French
    "de",      # German
    "it",      # Italian
    "pl",      # Polish
    "tr",      # Turkish
    "ru",      # Russian
    "nl",      # Dutch
    "cs",      # Czech
    "ar",      # Arabic
    "zh-cn",   # Simplified Chinese
    "ja",      # Japanese
    "hu",      # Hungarian
    "ko"       # Korean
]


# ============================================================================
# AUDIO PROCESSING UTILITIES
# ============================================================================

def normalize_audio_file(wav_path: str, target_sr: int = 22050) -> str:
    """
    Normalizar e converter arquivo de áudio para formato esperado pelo XTTS.
    Inclui validação robusta e tratamento de erros para arquivos corrompidos.
    
    Args:
        wav_path: Caminho do arquivo WAV de entrada
        target_sr: Sample rate de destino (default 22050)
    
    Returns:
        Caminho do arquivo WAV normalizado
    """
    try:
        # Tentar carregar com scipy (mais robusto para WAVs de navegador)
        try:
            sr, wav_data = wavfile.read(wav_path)
            print(f"   📊 Carregado com scipy: sr={sr}, shape={wav_data.shape}")
            
            if wav_data.size == 0:
                raise ValueError("Arquivo WAV vazio")
            
            if sr <= 0:
                raise ValueError(f"Sample rate inválido: {sr}")
            
            # Converter para float32 se necessário
            if wav_data.dtype != np.float32:
                wav_data = wav_data.astype(np.float32) / np.iinfo(wav_data.dtype).max
            
            # Clamp para evitar CUDA assertion
            wav_data = np.clip(wav_data, -1.0, 1.0)
            
            wav = torch.from_numpy(wav_data)
            
        except Exception as e:
            print(f"   ⚠️ Scipy falhou: {str(e)}, tentando torchaudio...")
            wav, sr = torchaudio.load(wav_path)
            print(f"   📊 Carregado com torchaudio: sr={sr}, shape={wav.shape}")
            
            if wav.shape[1] == 0:
                raise ValueError("Arquivo WAV sem amostras")
            
            if sr <= 0:
                raise ValueError(f"Sample rate inválido: {sr}")
        
        # Garantir que é tensor
        if not isinstance(wav, torch.Tensor):
            wav = torch.from_numpy(wav)
        
        # Validar valores para evitar CUDA assert
        if torch.isnan(wav).any():
            print(f"   ⚠️ Valores NaN detectados, substituindo por zeros")
            wav = torch.nan_to_num(wav, nan=0.0, posinf=1.0, neginf=-1.0)
        
        if torch.isinf(wav).any():
            print(f"   ⚠️ Valores Inf detectados, clamando")
            wav = torch.clamp(wav, min=-1.0, max=1.0)
        
        # Handle shape
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        elif wav.dim() == 2:
            pass
        else:
            raise ValueError(f"Shape inesperado: {wav.shape}")
        
        print(f"   📊 Após reshape: shape={wav.shape}")
        
        # Garantir comprimento mínimo (pelo menos 1 segundo)
        min_samples = target_sr
        if wav.shape[1] < min_samples:
            print(f"   ⚠️ Áudio muito curto ({wav.shape[1]} samples), padding para {min_samples}")
            padding = min_samples - wav.shape[1]
            wav = torch.nn.functional.pad(wav, (0, padding), mode='constant', value=0.0)
        
        # Resample se necessário
        if sr != target_sr:
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            wav = resampler(wav)
            print(f"   📊 Reamostrado para {target_sr}Hz")
        
        # Converter para mono se estéreo
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
            print(f"   📊 Convertido para mono: shape={wav.shape}")
        
        # Normalizar para [-0.95, 0.95]
        max_val = torch.abs(wav).max()
        if max_val > 0:
            wav = wav / (max_val * 1.05)
        
        wav = torch.clamp(wav, -0.95, 0.95)
        
        # Salvar normalizado usando scipy
        normalized_path = wav_path.replace('.wav', '_normalized.wav')
        wav_int16 = (wav.squeeze(0).numpy() * 32767).astype(np.int16)
        wavfile.write(normalized_path, target_sr, wav_int16)
        
        print(f"   ✅ Normalizado: {normalized_path}")
        
        return normalized_path
        
    except Exception as e:
        print(f"   ❌ Erro de normalização: {str(e)}")
        traceback.print_exc()
        return wav_path


def apply_speed_adjustment(wav_data, speed_factor: float):
    """
    Ajustar velocidade de reprodução de áudio.
    
    Args:
        wav_data: Dados de áudio (torch.Tensor ou numpy array)
        speed_factor: Multiplicador de velocidade (0.5 a 2.0)
    
    Returns:
        Áudio com velocidade ajustada
    """
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
        
        if speed_adjusted.shape[0] == 1:
            speed_adjusted = speed_adjusted.squeeze(0)
        
        return speed_adjusted
    
    except Exception as e:
        print(f"⚠️ Ajuste de velocidade falhou: {e}. Retornando áudio original.")
        return wav_data


# ============================================================================
# XTTS ENGINE CLASS
# ============================================================================

@register_engine("xtts-v2")
class XTTSEngine(BaseTTSEngine):
    """
    XTTS v2 Engine para síntese multilíngue com clonagem de voz.
    
    Suporta:
    - 16 idiomas
    - Clonagem de voz
    - GPU optimization (CUDA)
    - Voice processing robusço
    """
    
    def __init__(self, device: str = None):
        """
        Inicializar XTTS Engine.
        
        Args:
            device: "cuda" ou "cpu" (auto-detect se None)
        """
        if device is None:
            device = "cuda" if torch.cuda.is_available() else "cpu"
        
        super().__init__(device=device, model_name="xtts_v2")
        self.tts_model = None
    
    def load_model(self) -> None:
        """Carregar modelo XTTS v2."""
        if self.loaded:
            return
        
        try:
            print(f"⏳ Carregando modelo XTTS v2 ({self.device})...")
            
            use_gpu = (self.device == "cuda")
            
            self.tts_model = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                gpu=use_gpu,
                progress_bar=True
            )
            
            print(f"✅ XTTS v2 carregado com sucesso")
            self.loaded = True
            
        except Exception as e:
            print(f"❌ Erro ao carregar XTTS v2: {e}")
            traceback.print_exc()
            raise
    
    def unload_model(self) -> None:
        """Descarregar modelo e liberar memória."""
        if not self.loaded:
            return
        
        try:
            if self.tts_model:
                del self.tts_model
                self.tts_model = None
            
            if self.device == "cuda":
                torch.cuda.empty_cache()
            
            self.loaded = False
            print("✅ Modelo XTTS v2 descarregado")
            
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
        """
        Sintetizar texto em áudio com XTTS v2.
        
        Args:
            text: Texto a sintetizar
            language: Código do idioma
            voice: Nome da voz (ou path para arquivo WAV de clonagem)
            speed: Velocidade de fala (0.5 a 2.0)
            **kwargs: Parâmetros adicionais
        
        Returns:
            (audio_bytes, sample_rate)
        """
        if not self.loaded:
            raise RuntimeError("Modelo não carregado. Chamar load_model() primeiro.")
        
        if not self.validate_text(text):
            raise ValueError("Texto inválido ou vazio")
        
        if not self.validate_language(language):
            raise ValueError(f"Idioma não suportado: {language}")
        
        try:
            # Normalizar idioma para XTTS
            lang_code = self._normalize_language(language)
            
            # Determinar tipo de voz
            speaker_wav = None
            if voice != "default" and voice is not None:
                # Tentar carregar como arquivo de clonagem
                if os.path.exists(voice):
                    speaker_wav = normalize_audio_file(voice, target_sr=22050)
            
            print(f"🎙️ Sintetizando ({lang_code}): '{text[:50]}...'")
            
            # Sintetizar
            wav = self.tts_model.tts(
                text=text,
                language=lang_code,
                speaker_wav=speaker_wav,
                progress_bar=False,
                length_penalty=SYNTHESIS_CONFIG["gpt_cond_len"]
            )
            
            # Converter para numpy se necessário
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().numpy()
            
            # Aplicar ajuste de velocidade
            if speed != 1.0:
                wav = apply_speed_adjustment(wav, speed)
                if isinstance(wav, torch.Tensor):
                    wav = wav.numpy()
            
            # Normalizar
            max_val = np.abs(wav).max()
            if max_val > 0:
                wav = wav / (max_val * 1.05)
            wav = np.clip(wav, -0.95, 0.95)
            
            # Converter para WAV bytes
            wav_int16 = (wav * 32767).astype(np.int16)
            
            # Salvar em bytes (WAV em memória)
            import io
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
        return ["default"]  # XTTS v2 usa speaker_wav para vozes customizadas
    
    def clone_voice(
        self,
        voice_name: str,
        reference_audio_paths: List[str],
        language: str = "pt"
    ) -> bool:
        """
        Clonar voz a partir de arquivo(s) de referência.
        
        Para XTTS v2, a clonagem é feita passando o arquivo WAV
        na síntese, então apenas validamos os arquivos aqui.
        """
        try:
            print(f"🎙️ Validando arquivos para clonagem de voz: {voice_name}")
            
            for audio_path in reference_audio_paths:
                if not os.path.exists(audio_path):
                    raise FileNotFoundError(f"Arquivo não encontrado: {audio_path}")
                
                # Tentar normalizar para validar
                normalize_audio_file(audio_path)
            
            print(f"✅ Voz '{voice_name}' pronta para clonagem")
            return True
            
        except Exception as e:
            print(f"❌ Erro na clonagem: {e}")
            return False
    
    def _normalize_language(self, lang_code: str) -> str:
        """Normalizar código de idioma para formato XTTS."""
        # XTTS usa "pt" para português genérico
        if lang_code.startswith("pt"):
            return "pt"
        return lang_code
    
    def get_engine_name(self) -> str:
        """Retornar nome técnico."""
        return "xtts-v2"
    
    def get_engine_label(self) -> str:
        """Retornar label amigável."""
        return "XTTS v2 (Premium)"
    
    def get_engine_speed(self) -> str:
        """Retornar velocidade relativa."""
        return "medium"
    
    def get_engine_quality(self) -> str:
        """Retornar qualidade relativa."""
        return "excellent"
    
    def get_gpu_vram_required(self) -> int:
        """Retornar VRAM requerida em MB."""
        return 6000  # 6GB
    
    def supports_voice_cloning(self) -> bool:
        """XTTS suporta clonagem de voz."""
        return True


# ============================================================================
# FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================

def get_xtts_engine() -> XTTSEngine:
    """Helper para obter instância do XTTS Engine."""
    engine = XTTSEngine()
    engine.load_model()
    return engine


__all__ = [
    "XTTSEngine",
    "SAMPLE_RATE",
    "LANGUAGE_SUPPORT",
    "CACHE_DIR",
    "normalize_audio_file",
    "apply_speed_adjustment",
    "get_xtts_engine",
]
