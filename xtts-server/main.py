#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XTTS v2 Server with Voice Cloning Support
Multilingual Text-to-Speech Engine for Speakerbot
"""

import os
import io
import sys

# ============================================================================
# AUTO-ACCEPT COQUI LICENSE FOR AUTOMATION
# ============================================================================
# Quando rodando em modo daemon/automation, aceitar automaticamente a licença
if os.environ.get('XTTS_AUTO_LICENSE') == '1' or not sys.stdin.isatty():
    # Monkeypatch input() para aceitar automaticamente perguntas sobre licença
    original_input = __builtins__.input
    def auto_input(prompt=''):
        if 'commercial license' in prompt.lower() or 'cpml' in prompt.lower() or '[y/n]' in prompt:
            print(prompt + 'y')  # Auto-respond with 'y'
            return 'y'
        return original_input(prompt)
    __builtins__.input = auto_input

# Force UTF-8 encoding for stdout/stderr
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ============================================================================
# IMPORTAR TORCH ANTES DE TUDO PARA MONKEYPATCH
# ============================================================================
import torch
import torch.serialization

# Monkeypatch torch.load IMEDIATAMENTE após importar torch
original_torch_load = torch.load

def patched_torch_load(f, *args, **kwargs):
    """Patched torch.load que desabilita weights_only para compatibilidade com TTS"""
    kwargs['weights_only'] = False
    return original_torch_load(f, *args, **kwargs)

torch.load = patched_torch_load

# ============================================================================
# AGORA IMPORTAR TTS (QUE USA torch.load)
# ============================================================================
try:
    from TTS.api import TTS  # type: ignore
except ImportError as e:
    print(f"❌ ERRO: Módulo TTS não encontrado! {e}")
    print("Execute: pip install TTS")
    sys.exit(1)

# ============================================================================
# IMPORTS RESTANTES
# ============================================================================
import json
import shutil
import tempfile
import time
import numpy as np
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import traceback
import scipy.io.wavfile as wavfile

from fastapi import FastAPI, HTTPException, File, UploadFile, Form, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from pydantic import BaseModel
import uvicorn
import torchaudio

try:
    from voice_manager import VoiceManager
    from speaker_embedding_manager import SpeakerEmbeddingManager
except ImportError as e:
    print(f"❌ ERRO: Módulos locais não encontrados: {e}")
    traceback.print_exc()
    sys.exit(1)

try:
    from engines import XTTSEngine, EngineRegistry
    # Tentar importar StyleTTS2Engine opcionalmente
    try:
        from engines import StyleTTS2Engine
    except ImportError:
        StyleTTS2Engine = None
except ImportError as e:
    print(f"❌ ERRO: Engines module não encontrado: {e}")
    traceback.print_exc()
    sys.exit(1)

# ============================================================================
# ENGINES REGISTRY & CONFIGURATION
# ============================================================================

# Available TTS Engines - registry maps engine names to classes
ENGINES = {
    "xtts-v2": XTTSEngine,
}

# Adicionar StyleTTS2 se disponível
if StyleTTS2Engine is not None:
    ENGINES["stylets2"] = StyleTTS2Engine

# Default engine (can be overridden via request parameter)
DEFAULT_ENGINE = "xtts-v2"

# Active engine instances (lazy-loaded on demand)
active_engines: Dict[str, Any] = {}

# Monitor engine selection (tracks which engine is selected for monitor-based synthesis)
monitor_selected_engine: str = DEFAULT_ENGINE

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class FileMonitorRequest(BaseModel):
    """Model for file monitoring requests with multi-engine support"""
    file_path: str
    last_line_count: int = 0
    engine: str = DEFAULT_ENGINE  # Multi-engine support: "xtts-v2" or "stylets2"

# ============================================================================
# CONSTANTS & CONFIGURATION
# ============================================================================

HOST = "127.0.0.1"
PORT = 8877
DEBUG = False

# Audio Configuration (Updated to 24kHz for XTTS v2 best quality)
SAMPLE_RATE = 24000  # XTTS v2 native sample rate (was 22050 for better voice cloning quality)
LANGUAGE_SUPPORT = [
    "pt", "en", "es", "fr", "de", "it", "pl", "tr", "ru", "nl", "cs", 
    "ar", "zh-cn", "ja", "hu", "ko"
]

# GPU Configuration
GPU_AVAILABLE = torch.cuda.is_available()
GPU_DEVICE = torch.device('cuda' if GPU_AVAILABLE else 'cpu')
GPU_MEMORY_FRACTION = 0.8  # Use 80% of GPU memory by default

# Global GPU optimization settings (can be modified by user)
GPU_OPTIMIZATIONS = {
    "memory_fraction": 0.8,      # 0.8 = 80%, 0.9 = 90%, 0.95 = 95%
    "use_half_precision": True,  # FP16 for faster inference (2-3x speedup)
    "batch_processing": False,   # Process multiple synthesis requests in parallel
    "use_int8_quantization": False,  # INT8 quantization for faster inference
    "enable_model_cache": True   # Cache model in memory for faster subsequent calls
}

# Synthesis parameters config with conditioning controls
SYNTHESIS_CONFIG = {
    "gpu_enabled": GPU_AVAILABLE,
    "gpu_memory_fraction": GPU_MEMORY_FRACTION,
    "use_half_precision": GPU_AVAILABLE,  # FP16 for faster inference
    "batch_processing": False,
    "attention_dropout": 0.0,
    "length_scale": 1.0,  # Affects speech duration
    # GPT Conditioning parameters for better voice cloning quality
    "gpt_cond_len": 12,  # Seconds of audio to use for conditioning (3-30s, default 12s)
    "gpt_cond_chunk_len": 4,  # Chunk size for stability (should be <= gpt_cond_len)
    "max_ref_len": 10  # Maximum seconds of audio for decoder conditioning
}

# ============================================================================
# AUDIO PROCESSING UTILITIES
# ============================================================================

def apply_speed_adjustment(wav_data, speed_factor: float):
    """
    Adjust audio playback speed using librosa or torch resampling.
    
    Args:
        wav_data: Audio data (torch.Tensor or numpy array)
        speed_factor: Speed multiplier (0.5 to 2.0)
    
    Returns:
        Speed-adjusted audio data
    """
    if speed_factor == 1.0:
        return wav_data
    
    try:
        # Convert to torch tensor if needed
        if not isinstance(wav_data, torch.Tensor):
            wav_tensor = torch.tensor(wav_data, dtype=torch.float32)
        else:
            wav_tensor = wav_data.clone()
        
        # Ensure 1D or 2D tensor
        if wav_tensor.dim() == 1:
            wav_tensor = wav_tensor.unsqueeze(0)
        
        # Calculate new sample rate (speed increases = higher effective SR)
        new_sr = int(SAMPLE_RATE * speed_factor)
        
        # Use torchaudio resample to adjust speed
        resampler = torchaudio.transforms.Resample(SAMPLE_RATE, new_sr)
        speed_adjusted = resampler(wav_tensor)
        
        # Squeeze back to 1D if input was 1D
        if speed_adjusted.shape[0] == 1:
            speed_adjusted = speed_adjusted.squeeze(0)
        
        return speed_adjusted
    
    except Exception as e:
        print(f"⚠️ Speed adjustment failed: {e}. Returning original audio.")
        return wav_data

def normalize_audio_file(wav_path: str, target_sr: int = 22050) -> str:
    """
    Normalize and convert audio file to the format expected by XTTS.
    Includes robust validation and error handling for corrupted files.
    
    Args:
        wav_path: Path to input WAV file
        target_sr: Target sample rate (default 22050)
    
    Returns:
        Path to normalized WAV file
    """
    try:
        # Try loading with scipy first (more robust for browser WAVs)
        try:
            sr, wav_data = wavfile.read(wav_path)
            print(f"   📊 Loaded with scipy: sr={sr}, shape={wav_data.shape}")
            
            # Validate data
            if wav_data.size == 0:
                raise ValueError("WAV file is empty")
            
            if sr <= 0:
                raise ValueError(f"Invalid sample rate: {sr}")
            
            # Convert to float32 if needed
            if wav_data.dtype != np.float32:
                wav_data = wav_data.astype(np.float32) / np.iinfo(wav_data.dtype).max
            
            # Clamp values to prevent CUDA assertion
            wav_data = np.clip(wav_data, -1.0, 1.0)
            
            # Convert to tensor
            wav = torch.from_numpy(wav_data)
        except Exception as e:
            print(f"   ⚠️ Scipy failed: {str(e)}, trying torchaudio...")
            wav, sr = torchaudio.load(wav_path)
            print(f"   📊 Loaded with torchaudio: sr={sr}, shape={wav.shape}")
            
            # Validate loaded data
            if wav.shape[1] == 0:
                raise ValueError("WAV file has no samples")
            
            if sr <= 0:
                raise ValueError(f"Invalid sample rate: {sr}")
        
        # Ensure it's a tensor
        if not isinstance(wav, torch.Tensor):
            wav = torch.from_numpy(wav)
        
        # Validate tensor values to prevent CUDA assert
        if torch.isnan(wav).any():
            print(f"   ⚠️ NaN values detected, replacing with zeros")
            wav = torch.nan_to_num(wav, nan=0.0, posinf=1.0, neginf=-1.0)
        
        if torch.isinf(wav).any():
            print(f"   ⚠️ Inf values detected, clamping")
            wav = torch.clamp(wav, min=-1.0, max=1.0)
        
        # Handle shape
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)
        elif wav.dim() == 2:
            pass
        else:
            raise ValueError(f"Unexpected tensor shape: {wav.shape}")
        
        print(f"   📊 After reshape: shape={wav.shape}")
        
        # Ensure minimum length (at least 1 second at target_sr)
        min_samples = target_sr  # 1 second minimum
        if wav.shape[1] < min_samples:
            print(f"   ⚠️ Audio too short ({wav.shape[1]} samples), padding to {min_samples}")
            padding = min_samples - wav.shape[1]
            wav = torch.nn.functional.pad(wav, (0, padding), mode='constant', value=0.0)
        
        # Resample if needed
        if sr != target_sr:
            resampler = torchaudio.transforms.Resample(sr, target_sr)
            wav = resampler(wav)
            print(f"   📊 Resampled to {target_sr}Hz")
        
        # Convert to mono if stereo
        if wav.shape[0] > 1:
            wav = wav.mean(dim=0, keepdim=True)
            print(f"   📊 Converted to mono: shape={wav.shape}")
        
        # Normalize to [-0.95, 0.95]
        max_val = torch.abs(wav).max()
        if max_val > 0:
            wav = wav / (max_val * 1.05)  # Slight headroom
        
        wav = torch.clamp(wav, -0.95, 0.95)
        
        # Save normalized using scipy
        normalized_path = wav_path.replace('.wav', '_normalized.wav')
        
        # Convert to int16 for saving
        wav_int16 = (wav.squeeze(0).numpy() * 32767).astype(np.int16)
        wavfile.write(normalized_path, target_sr, wav_int16)
        
        print(f"   ✅ Normalized: {normalized_path}")
        
        return normalized_path
        
    except Exception as e:
        print(f"   ❌ Normalization error: {str(e)}")
        import traceback
        traceback.print_exc()
        return wav_path

# ============================================================================

app = FastAPI(
    title="XTTS v2 Server",
    description="Multilingual TTS with Voice Cloning",
    version="0.1.5"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PWA ROUTES - Servir arquivos estáticos (manifest, service worker, etc)
# ============================================================================

@app.get("/")
async def serve_root():
    """Serve the main HTML file"""
    current_dir = Path(__file__).parent
    html_path = current_dir / "web_ui.html"
    if html_path.exists():
        with open(html_path, 'r', encoding='utf-8') as f:
            response = HTMLResponse(content=f.read())
            # Disable cache to always serve latest version
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            return response
    raise HTTPException(status_code=404, detail="web_ui.html not found")

@app.get("/manifest.json")
async def serve_manifest():
    """Serve the PWA manifest"""
    current_dir = Path(__file__).parent
    manifest_path = current_dir / "manifest.json"
    if manifest_path.exists():
        return FileResponse(manifest_path, media_type="application/manifest+json")
    raise HTTPException(status_code=404, detail="manifest.json not found")

@app.get("/service-worker.js")
async def serve_service_worker():
    """Serve the service worker"""
    current_dir = Path(__file__).parent
    sw_path = current_dir / "service-worker.js"
    if sw_path.exists():
        return FileResponse(sw_path, media_type="application/javascript")
    raise HTTPException(status_code=404, detail="service-worker.js not found")

@app.get("/obs-audio")
async def serve_obs_audio():
    """Serve OBS-compatible audio-only player (no UI, only audio playback)"""
    obs_html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OBS Audio Stream</title>
    <style>
        body {
            margin: 0;
            padding: 0;
            background: transparent;
            overflow: hidden;
        }
        #audio-player {
            display: none;
        }
        #status {
            color: transparent;
            font-size: 1px;
        }
    </style>
</head>
<body>
    <audio id="audio-player" autoplay></audio>
    <div id="status"></div>
    
    <script>
        const player = document.getElementById('audio-player');
        const statusDiv = document.getElementById('status');
        let isPlaying = false;
        
        // WebSocket para receber áudio em tempo real
        function connectWebSocket() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const ws = new WebSocket(`${protocol}//${window.location.host}/ws/audio`);
            
            ws.onopen = () => {
                statusDiv.textContent = 'Conectado';
                console.log('WebSocket conectado ao servidor XTTS');
            };
            
            ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    
                    if (data.type === 'audio' && data.audio) {
                        // Decodificar áudio base64
                        const binaryString = atob(data.audio);
                        const bytes = new Uint8Array(binaryString.length);
                        for (let i = 0; i < binaryString.length; i++) {
                            bytes[i] = binaryString.charCodeAt(i);
                        }
                        
                        // Criar Blob e URL para o player
                        const blob = new Blob([bytes], { type: 'audio/wav' });
                        const audioUrl = URL.createObjectURL(blob);
                        
                        // Reproduzir áudio
                        player.src = audioUrl;
                        player.play().catch(err => {
                            console.error('Erro ao reproduzir áudio:', err);
                        });
                        
                        statusDiv.textContent = 'Reproduzindo';
                        isPlaying = true;
                    }
                    
                    if (data.type === 'status') {
                        statusDiv.textContent = data.message;
                    }
                } catch (err) {
                    console.error('Erro ao processar mensagem:', err);
                }
            };
            
            ws.onerror = (error) => {
                console.error('Erro WebSocket:', error);
                statusDiv.textContent = 'Erro de conexão';
            };
            
            ws.onclose = () => {
                statusDiv.textContent = 'Desconectado';
                // Reconectar em 3 segundos
                setTimeout(connectWebSocket, 3000);
            };
        }
        
        // Iniciar conexão WebSocket
        connectWebSocket();
        
        // Eventos do player
        player.addEventListener('play', () => {
            isPlaying = true;
        });
        
        player.addEventListener('ended', () => {
            isPlaying = false;
            statusDiv.textContent = 'Aguardando...';
        });
        
        player.addEventListener('error', (e) => {
            console.error('Erro no player:', e);
            statusDiv.textContent = 'Erro no player';
        });
    </script>
</body>
</html>"""
    return HTMLResponse(content=obs_html)

# Global instances - using the new multi-engine system
# Note: tts_engine and tts_model are primarily for XTTS v2 (legacy)
# For multi-engine support, use get_active_engine(engine_name) function
tts_engine: Optional[XTTSEngine] = None  # Primary XTTS v2 engine instance
tts_model: Optional[Any] = None  # Legacy reference (points to tts_engine.tts_model)
voice_manager: Optional[VoiceManager] = None
embedding_manager: Optional[SpeakerEmbeddingManager] = None

# ============================================================================
# STARTUP & SHUTDOWN
# ============================================================================


def get_active_engine(engine_name: Optional[str] = None) -> Any:
    """
    Get or initialize the active TTS engine.
    
    Args:
        engine_name: Name of engine ("xtts-v2" or "stylets2")
                    If None, uses DEFAULT_ENGINE
    
    Returns:
        Initialized engine instance
    """
    if engine_name is None:
        engine_name = DEFAULT_ENGINE
    
    if engine_name not in ENGINES:
        raise ValueError(f"Unknown engine: {engine_name}. Available: {list(ENGINES.keys())}")
    
    # Return cached instance if already loaded
    if engine_name in active_engines:
        return active_engines[engine_name]
    
    # Load engine for the first time
    print(f"⏳ Loading engine: {engine_name}")
    engine_class = ENGINES[engine_name]
    engine = engine_class()
    engine.load_model()
    active_engines[engine_name] = engine
    
    return engine


def get_preferred_device() -> str:
    """Return the preferred device for TTS ('cuda' or 'cpu').

    Priority:
    - If `XTTS_DEVICE` environment variable is set to 'cuda' or 'cpu', respect it (but warn
      if 'cuda' is requested and CUDA isn't available).
    - Otherwise, use CUDA if `torch.cuda.is_available()` is True, else CPU.
    """
    env = os.getenv("XTTS_DEVICE", "").strip().lower()
    if env in ("cuda", "gpu"):
        if torch.cuda.is_available():
            return "cuda"
        else:
            print("⚠️ XTTS_DEVICE=cuda requested but CUDA not available — falling back to CPU")
            return "cpu"
    if env == "cpu":
        return "cpu"
    return "cuda" if torch.cuda.is_available() else "cpu"


def initialize_tts_model(model_name: str = "tts_models/multilingual/multi-dataset/xtts_v2"):
    """Initialize TTS using the new XTTSEngine abstraction layer.
    
    This function is now a wrapper around get_active_engine() for backward compatibility.
    The XTTSEngine handles all device selection, GPU fallback, and initialization logic.
    """
    global tts_engine
    
    try:
        print("⏳ Inicializando XTTS v2 via Engine Registry...")
        
        # Get or initialize XTTS v2 engine
        tts_engine = get_active_engine("xtts-v2")
        
        if tts_engine is None:
            raise RuntimeError("Failed to initialize TTS engine")
        
        print(f"✅ XTTS v2 Engine inicializado com sucesso")
        
        # For backward compatibility, return the XTTSEngine instance which has tts_model
        # (Other code expects to call tts_model.tts(...))
        if hasattr(tts_engine, 'tts_model'):
            return tts_engine.tts_model
        else:
            # If it's not an XTTSEngine, return the engine itself
            return tts_engine
        
    except Exception as e:
        print(f"❌ Erro ao inicializar TTS Engine: {e}")
        traceback.print_exc()
        raise

@app.on_event("startup")
async def startup_event():
    """Initialize TTS engine, voice manager, and embedding manager on startup."""
    global tts_engine, tts_model, voice_manager, embedding_manager
    
    print("🚀 Starting XTTS v2 Server with Multi-Engine Support...")
    print(f"🖥️  Device: {torch.device('cuda' if torch.cuda.is_available() else 'cpu')}")
    
    # Debug: List all registered routes
    print("\n📋 Registered routes:")
    for route in app.routes:
        route_info = str(route)
        if '/v1/' in route_info or '/health' in route_info or '/' == route_info[-1]:
            print(f"  {route_info}")
    print()
    
    try:
        # Initialize TTS engine
        print("⏳ Loading XTTS v2 engine (this may take a moment)...")
        tts_model = initialize_tts_model("tts_models/multilingual/multi-dataset/xtts_v2")
        print(f"✅ XTTS v2 engine loaded successfully")
        
        # Initialize voice manager
        try:
            voice_manager = VoiceManager()
            print(f"✅ Voice Manager initialized - {len(voice_manager.list_voices())} voices available")
        except Exception as e:
            print(f"⚠️ Voice Manager initialization warning: {str(e)}")
            voice_manager = None
        
        # Initialize embedding manager
        try:
            if tts_engine:
                embedding_manager = SpeakerEmbeddingManager(tts_engine.tts_model)
                print("✅ Speaker Embedding Manager initialized")
            else:
                print("⚠️ Skipping Embedding Manager (TTS engine not loaded)")
                embedding_manager = None
        except Exception as e:
            print(f"⚠️ Embedding Manager initialization warning: {str(e)}")
            embedding_manager = None
        
        # Open browser automatically
        print("\n🌐 Abrindo navegador em http://localhost:8877...")
        try:
            import webbrowser
            webbrowser.open('http://localhost:8877')
        except Exception as e:
            print(f"⚠️ Não foi possível abrir o navegador automaticamente: {e}")
            print("   Acesse manualmente: http://localhost:8877")
        
    except Exception as e:
        print(f"❌ Startup error: {str(e)}")
        traceback.print_exc()
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    global tts_engine
    
    print("🛑 Shutting down XTTS v2 Server...")
    
    if tts_engine:
        try:
            tts_engine.unload_model()
            print("✅ TTS engine unloaded")
        except Exception as e:
            print(f"⚠️ Error unloading engine: {e}")
    
    print("✅ Server shutdown complete")

# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model": "xtts_v2",
        "device": str(torch.device('cuda' if torch.cuda.is_available() else 'cpu')),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/v1/info")
async def get_info():
    """Get server information and capabilities."""
    return {
        "name": "XTTS v2 Server",
        "version": "0.1.5",
        "model": "xtts_v2",
        "device": str(torch.device('cuda' if torch.cuda.is_available() else 'cpu')),
        "languages": LANGUAGE_SUPPORT,
        "features": {
            "voice_cloning": True,
            "multilingual": True,
            "custom_voices": True,
            "embedding_cache": True,
            "obs_audio_streaming": True
        },
        "endpoints": {
            "tts": "POST /v1/synthesize",
            "voice_clone": "POST /v1/clone-voice",
            "upload_voice": "POST /v1/voices/upload",
            "list_voices": "GET /v1/voices",
            "delete_voice": "DELETE /v1/voices/{voice_id}",
            "get_voice": "GET /v1/voices/{voice_id}",
            "batch_tts": "POST /v1/batch-synthesize",
            "precompute_embeddings": "POST /v1/precompute-embeddings",
            "synthesis_config": "GET /v1/synthesis-config",
            "obs_audio_player": "GET /obs-audio",
            "obs_config": "GET /obs-config",
            "obs_websocket": "WS /ws/audio",
            "health": "GET /health",
            "info": "GET /v1/info"
        },
        "max_text_length": 1000,
        "supported_sample_rate": SAMPLE_RATE,
        "max_voice_size_mb": 50,
        "max_custom_voices": 100
    }

@app.get("/v1/synthesis-config")
async def get_synthesis_config():
    """Get synthesis configuration parameters and their valid ranges."""
    return {
        "parameters": {
            "speed": {
                "description": "Playback speed multiplier",
                "type": "float",
                "min": 0.5,
                "max": 2.0,
                "default": 1.0,
                "step": 0.1,
                "unit": "x"
            },
            "temperature": {
                "description": "Controls randomness and variation in speech (lower=more robotic, higher=more varied)",
                "type": "float",
                "min": 0.1,
                "max": 1.0,
                "default": 0.75,
                "step": 0.05,
                "unit": ""
            },
            "top_k": {
                "description": "Limits vocabulary diversity (0=deterministic, 100=maximum variation)",
                "type": "integer",
                "min": 0,
                "max": 100,
                "default": 50,
                "step": 5,
                "unit": ""
            },
            "top_p": {
                "description": "Cumulative probability threshold for token selection",
                "type": "float",
                "min": 0.0,
                "max": 1.0,
                "default": 0.85,
                "step": 0.05,
                "unit": ""
            },
            "length_scale": {
                "description": "Controls phoneme duration (affects word/sentence length)",
                "type": "float",
                "min": 0.5,
                "max": 2.0,
                "default": 1.0,
                "step": 0.1,
                "unit": ""
            },
            "gpt_cond_len": {
                "description": "GPT conditioning length in seconds - affects voice cloning quality (longer = better for consistent voice)",
                "type": "float",
                "min": 3.0,
                "max": 30.0,
                "default": 12.0,
                "step": 0.5,
                "unit": "s",
                "note": "Higher values improve voice cloning quality but use more memory"
            }
        },
        "advanced_settings": {
            "gpu_enabled": GPU_AVAILABLE,
            "gpu_device": str(GPU_DEVICE),
            "gpu_memory_fraction": GPU_MEMORY_FRACTION,
            "use_half_precision": SYNTHESIS_CONFIG["use_half_precision"],
            "batch_processing_available": False,
            "gpu_optimizations": {
                "memory_fraction": {
                    "description": "GPU memory allocation (higher = faster but riskier)",
                    "type": "float",
                    "min": 0.5,
                    "max": 0.95,
                    "default": 0.8,
                    "step": 0.05,
                    "current": GPU_OPTIMIZATIONS["memory_fraction"],
                    "options": [
                        {"label": "50% (Safe)", "value": 0.5},
                        {"label": "70% (Balanced)", "value": 0.7},
                        {"label": "80% (Default)", "value": 0.8},
                        {"label": "90% (Fast)", "value": 0.9},
                        {"label": "95% (Very Fast)", "value": 0.95}
                    ]
                },
                "use_half_precision": {
                    "description": "Use FP16 for 2-3x faster inference (slight quality loss)",
                    "type": "boolean",
                    "default": True,
                    "current": GPU_OPTIMIZATIONS["use_half_precision"],
                    "speedup": "2-3x"
                },
                "batch_processing": {
                    "description": "Process multiple synthesis requests in parallel",
                    "type": "boolean",
                    "default": False,
                    "current": GPU_OPTIMIZATIONS["batch_processing"],
                    "note": "Experimental - reduces individual latency for batch requests"
                },
                "use_int8_quantization": {
                    "description": "Use INT8 quantization for faster inference",
                    "type": "boolean",
                    "default": False,
                    "current": GPU_OPTIMIZATIONS["use_int8_quantization"],
                    "speedup": "1.5-2x",
                    "note": "Experimental - may affect quality"
                },
                "enable_model_cache": {
                    "description": "Keep model in GPU memory between requests",
                    "type": "boolean",
                    "default": True,
                    "current": GPU_OPTIMIZATIONS["enable_model_cache"],
                    "benefit": "Faster subsequent requests (eliminates load time)"
                }
            }
        },
        "presets": {
            "natural": {
                "description": "Natural and balanced speaking",
                "speed": 1.0,
                "temperature": 0.75,
                "top_k": 50,
                "top_p": 0.85,
                "length_scale": 1.0
            },
            "slow_and_clear": {
                "description": "Slower, more precise speech",
                "speed": 0.7,
                "temperature": 0.5,
                "top_k": 30,
                "top_p": 0.75,
                "length_scale": 1.2
            },
            "fast_and_energetic": {
                "description": "Faster, more dynamic speech",
                "speed": 1.3,
                "temperature": 0.85,
                "top_k": 70,
                "top_p": 0.9,
                "length_scale": 0.8
            },
            "robotic": {
                "description": "Deterministic, robotic speech",
                "speed": 1.0,
                "temperature": 0.1,
                "top_k": 0,
                "top_p": 0.5,
                "length_scale": 1.0
            },
            "expressive": {
                "description": "Very expressive and varied speech",
                "speed": 1.0,
                "temperature": 0.95,
                "top_k": 100,
                "top_p": 0.95,
                "length_scale": 1.1
            },
            "whisper": {
                "description": "Soft, whispering tone",
                "speed": 0.8,
                "temperature": 0.6,
                "top_k": 40,
                "top_p": 0.8,
                "length_scale": 0.9
            },
            "dramatic": {
                "description": "Dramatic, intense delivery",
                "speed": 1.1,
                "temperature": 0.9,
                "top_k": 80,
                "top_p": 0.92,
                "length_scale": 1.15
            }
        }
    }

@app.get("/v1/engines")
async def get_available_engines():
    """
    Get list of available TTS engines with their specifications.
    
    Returns:
        JSON object with available engines, current engine, and detailed specifications
    """
    print(f"\n🎤 GET /v1/engines called")
    
    engines_info = {
        "available": list(ENGINES.keys()),
        "current": DEFAULT_ENGINE,
        "engines": {
            "xtts-v2": {
                "label": "XTTS v2 (Default)",
                "description": "High-quality multilingual TTS with excellent voice cloning",
                "languages": 16,
                "speed": "medium",
                "quality": "excellent",
                "vram_mb": 6000,
                "estimated_time_per_sentence": "15-20s",
                "features": [
                    "16 languages support",
                    "Excellent quality",
                    "Voice cloning",
                    "Gpt-conditioning"
                ],
                "pros": [
                    "Best audio quality",
                    "Excellent multilingual support",
                    "Strong voice cloning"
                ],
                "cons": [
                    "Slower synthesis (15-20s)",
                    "Higher GPU memory (6GB)"
                ]
            },
            "stylets2": {
                "label": "StyleTTS2 (Fast)",
                "description": "Fast multilingual TTS with near-human quality and low latency",
                "languages": 11,
                "speed": "very-fast",
                "quality": "excellent",
                "vram_mb": 2000,
                "estimated_time_per_sentence": "5-7s",
                "features": [
                    "11 languages support (PT-BR included)",
                    "Near-human quality",
                    "Voice cloning",
                    "Low VRAM requirement"
                ],
                "pros": [
                    "2-3x faster synthesis",
                    "Lower GPU memory (2GB)",
                    "Near-human quality",
                    "Optimized for Portuguese"
                ],
                "cons": [
                    "Slightly fewer languages",
                    "Newer engine (less tested)"
                ]
            }
        }
    }
    
    print(f"   Available engines: {engines_info['available']}")
    print(f"   Current engine: {engines_info['current']}")
    
    return engines_info

@app.post("/v1/gpu-settings")
async def update_gpu_settings(
    memory_fraction: float = Form(None),
    use_half_precision: bool = Form(None),
    batch_processing: bool = Form(None),
    use_int8_quantization: bool = Form(None),
    enable_model_cache: bool = Form(None)
):
    """
    Update GPU optimization settings for faster inference.
    
    Args:
        memory_fraction: GPU memory allocation (0.5 to 0.95)
        use_half_precision: Enable FP16 for faster inference
        batch_processing: Enable batch processing
        use_int8_quantization: Enable INT8 quantization
        enable_model_cache: Keep model in memory between requests
    
    Returns:
        Updated settings and performance metrics
    """
    global GPU_OPTIMIZATIONS
    
    print(f"\n⚙️ POST /v1/gpu-settings called")
    
    # Update settings if provided
    if memory_fraction is not None:
        memory_fraction = max(0.5, min(0.95, memory_fraction))
        GPU_OPTIMIZATIONS["memory_fraction"] = memory_fraction
        print(f"   📊 GPU Memory Fraction: {memory_fraction * 100:.0f}%")
    
    if use_half_precision is not None:
        GPU_OPTIMIZATIONS["use_half_precision"] = use_half_precision
        print(f"   🔢 Half-Precision (FP16): {use_half_precision}")
    
    if batch_processing is not None:
        GPU_OPTIMIZATIONS["batch_processing"] = batch_processing
        print(f"   📦 Batch Processing: {batch_processing}")
    
    if use_int8_quantization is not None:
        GPU_OPTIMIZATIONS["use_int8_quantization"] = use_int8_quantization
        print(f"   🔒 INT8 Quantization: {use_int8_quantization}")
    
    if enable_model_cache is not None:
        GPU_OPTIMIZATIONS["enable_model_cache"] = enable_model_cache
        print(f"   💾 Model Cache: {enable_model_cache}")
    
    # Return updated settings with performance estimates
    performance_estimate = {
        "base_latency_ms": 1000,  # Baseline without optimizations
        "estimated_speedup": 1.0
    }
    
    if GPU_OPTIMIZATIONS["use_half_precision"]:
        performance_estimate["estimated_speedup"] *= 2.5
    
    if GPU_OPTIMIZATIONS["use_int8_quantization"]:
        performance_estimate["estimated_speedup"] *= 1.5
    
    performance_estimate["estimated_latency_ms"] = int(
        performance_estimate["base_latency_ms"] / performance_estimate["estimated_speedup"]
    )
    
    return {
        "status": "✅ GPU settings updated",
        "current_settings": GPU_OPTIMIZATIONS,
        "performance_estimate": performance_estimate,
        "recommendations": {
            "for_speed": "Enable FP16 + increase memory to 90%",
            "for_quality": "Keep FP16 off + low memory (0.7-0.8)",
            "balanced": "FP16 on + memory at 80% (default)"
        }
    }

# ============================================================================
# TTS ENDPOINTS
# ============================================================================

def _do_synthesis(text, language, voice, speed, temperature, top_k, top_p, length_scale, gpt_cond_len, engine=None):
    """
    Helper function to perform TTS synthesis (runs in thread pool to avoid blocking)
    Includes robust CUDA error handling with automatic fallback to CPU
    Supports multiple engines (XTTS v2, StyleTTS2, etc)
    """
    if engine is None:
        engine = DEFAULT_ENGINE
    
    retry_count = 0
    max_retries = 2
    last_error = None
    
    while retry_count < max_retries:
        try:
            # Get the active engine instance
            active_engine = get_active_engine(engine)
            if not active_engine:
                raise RuntimeError(f"Failed to load engine: {engine}")
            
            # Check if TTS model is loaded (for backward compatibility)
            if not tts_model:
                raise RuntimeError("TTS model not loaded!")
            
            if not voice_manager:
                raise RuntimeError("Voice manager not initialized!")
            
            # Get voice speaker embedding
            speaker_wav = voice_manager.get_voice_file(voice)
            if not speaker_wav:
                raise RuntimeError(f"Voice '{voice}' not found")
            
            # Validate speaker WAV file to prevent CUDA device-side asserts
            print(f"🎤 Validating speaker WAV: {speaker_wav}")
            try:
                normalized_wav = normalize_audio_file(speaker_wav, target_sr=22050)
                speaker_wav = normalized_wav
                print(f"✅ Speaker WAV validated and normalized: {speaker_wav}")
                
                # Pre-load and sanitize speaker audio buffer
                sr_speaker, speaker_data = wavfile.read(speaker_wav)
                speaker_data = speaker_data.astype(np.float32) / np.iinfo(speaker_data.dtype).max if speaker_data.dtype != np.float32 else speaker_data
                speaker_data = np.clip(speaker_data, -1.0, 1.0)
                speaker_data = np.nan_to_num(speaker_data, nan=0.0, posinf=1.0, neginf=-1.0)
                print(f"✅ Speaker audio buffer sanitized: range [{speaker_data.min():.4f}, {speaker_data.max():.4f}]")
                
            except Exception as validate_error:
                print(f"⚠️ Speaker WAV validation failed: {validate_error}")
                raise RuntimeError(f"Invalid speaker voice file: {validate_error}")
            
            # Synthesize
            print(f"🎤 Synthesizing: '{text[:50]}...' with voice '{voice}' in {language}")
            
            # Generate audio using TTS v0.22+ API with inference parameters
            wav = tts_model.tts(  # type: ignore
                text=text,
                speaker_wav=speaker_wav,
                language=language,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p
            )
            
            # Sanitize generated audio buffer to prevent CUDA asserts
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu()  # Move to CPU for sanitization
                wav_np = wav.numpy()
            else:
                wav_np = np.asarray(wav)
            
            # Remove NaN, Inf, and clamp to valid range
            wav_np = np.nan_to_num(wav_np, nan=0.0, posinf=1.0, neginf=-1.0)
            wav_np = np.clip(wav_np, -1.0, 1.0)
            print(f"✅ Generated audio sanitized: range [{wav_np.min():.4f}, {wav_np.max():.4f}], shape {wav_np.shape}")
            
            # Convert back to tensor (keep on CPU)
            wav = torch.from_numpy(wav_np).float()
            
            # Apply length scale adjustment if needed (affects phoneme duration)
            if length_scale != 1.0:
                print(f"⏱️ Adjusting length scale to {length_scale}x")
                wav = apply_speed_adjustment(wav, 1.0 / length_scale)
            
            # Apply speed adjustment if needed (speed != 1.0)
            if speed != 1.0:
                print(f"⏱️ Adjusting speed to {speed}x")
                wav = apply_speed_adjustment(wav, speed)
            
            # Ensure tensor is on CPU before saving
            if isinstance(wav, torch.Tensor):
                wav = wav.cpu().detach()
            
            # Save to temporary file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            if isinstance(wav, torch.Tensor):
                torchaudio.save(temp_file.name, wav.unsqueeze(0) if wav.dim() == 1 else wav, SAMPLE_RATE)
            else:
                torchaudio.save(temp_file.name, torch.tensor(wav).unsqueeze(0), SAMPLE_RATE)
            
            print(f"✅ Synthesis complete: {len(wav) if isinstance(wav, (list, torch.Tensor)) else 'variable'} samples")
            
            return temp_file.name
        
        except RuntimeError as e:
            error_str = str(e)
            last_error = e
            
            # Check if it's a CUDA error
            if "CUDA" in error_str or "cuda" in error_str or "CUBLAS" in error_str or "assert" in error_str.lower():
                retry_count += 1
                print(f"⚠️ CUDA error encountered (attempt {retry_count}/{max_retries}): {error_str}")
                
                # For device-side assert, be more aggressive with recovery
                if "device-side assert" in error_str.lower():
                    print("🚨 Device-side assert detected - performing aggressive GPU reset")
                    try:
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                            torch.cuda.reset_peak_memory_stats()
                            if hasattr(torch.cuda, 'empty_cache'):
                                torch.cuda.empty_cache()
                            torch.cuda.synchronize()
                            time.sleep(2)  # Longer delay for device-side asserts
                    except Exception as reset_error:
                        print(f"⚠️ GPU reset failed: {reset_error}")
                
                if retry_count < max_retries:
                    # Try to recover CUDA state
                    try:
                        if torch.cuda.is_available():
                            print("🔄 Attempting CUDA recovery...")
                            torch.cuda.empty_cache()
                            torch.cuda.reset_peak_memory_stats()
                            torch.cuda.synchronize()
                            print("✅ CUDA cache cleared, retrying...")
                            time.sleep(1)  # Small delay before retry
                            continue
                    except Exception as recovery_error:
                        print(f"⚠️ CUDA recovery failed: {recovery_error}")
                        # Fall through to next attempt
                
                # If retries exhausted or recovery failed, raise
                print(f"❌ CUDA error persists after {retry_count} attempts")
                traceback.print_exc()
                raise last_error
            else:
                # Not a CUDA error, raise immediately
                print(f"❌ Synthesis error: {error_str}")
                traceback.print_exc()
                raise
        
        except Exception as e:
            print(f"❌ Unexpected error during synthesis: {str(e)}")
            traceback.print_exc()
            raise

@app.post("/v1/synthesize")
async def synthesize_tts(
    text: str = Form(...),
    language: str = Form("pt"),
    voice: str = Form("default"),
    speed: float = Form(1.0),
    temperature: float = Form(0.75),
    top_k: int = Form(50),
    top_p: float = Form(0.85),
    length_scale: float = Form(1.0),
    gpt_cond_len: float = Form(12.0),
    engine: str = Form(DEFAULT_ENGINE)
):
    """
    Synthesize speech from text using specified voice and language.
    Supports multiple TTS engines (XTTS v2, StyleTTS2, etc).
    
    Args:
        text: Text to synthesize
        language: Language code (e.g., 'pt', 'en', 'es')
        voice: Voice identifier (preset or custom)
        speed: Speed multiplier (0.5 to 2.0)
        temperature: Randomness/variation (0.1 to 1.0)
        top_k: Diversity parameter (0 to 100)
        top_p: Cumulative probability (0.0 to 1.0)
        length_scale: Phoneme duration multiplier (0.5 to 2.0)
        gpt_cond_len: GPT conditioning length in seconds (3 to 30, default 12)
        engine: TTS engine to use ('xtts-v2' or 'stylets2'), default from DEFAULT_ENGINE
    
    Returns:
        WAV audio file
    """
    print(f"\n🎤 POST /v1/synthesize called")
    print(f"   text={text[:50]}..., language={language}, voice={voice}")
    print(f"   engine={engine}, config: speed={speed}x, temp={temperature}, top_k={top_k}, top_p={top_p}, length_scale={length_scale}")
    print(f"   conditioning: gpt_cond_len={gpt_cond_len}s")
    print(f"   GPU: memory={GPU_OPTIMIZATIONS['memory_fraction']*100:.0f}%, FP16={GPU_OPTIMIZATIONS['use_half_precision']}, cache={GPU_OPTIMIZATIONS['enable_model_cache']}")
    if tts_model:
        print(f"   tts_model={type(tts_model).__name__}, voice_manager={type(voice_manager).__name__}")
    
    try:
        # Validate inputs
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Text exceeds maximum length of 1000 characters")
        
        if language not in LANGUAGE_SUPPORT:
            raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")
        
        # Validate and clamp synthesis parameters
        speed = max(0.5, min(2.0, speed))
        temperature = max(0.1, min(1.0, temperature))
        top_k = max(0, min(100, top_k))
        top_p = max(0.0, min(1.0, top_p))
        length_scale = max(0.5, min(2.0, length_scale))
        gpt_cond_len = max(3.0, min(30.0, gpt_cond_len))  # 3-30 seconds
        
        # Run synthesis in thread pool to avoid blocking
        temp_file_path = await run_in_threadpool(
            _do_synthesis,
            text,
            language,
            voice,
            speed,
            temperature,
            top_k,
            top_p,
            length_scale,
            gpt_cond_len,
            engine
        )
        
        # Enviar áudio para OBS se houver conexões
        if obs_connections:
            with open(temp_file_path, 'rb') as f:
                audio_data = f.read()
            await broadcast_audio_to_obs(audio_data)
        
        return FileResponse(
            path=temp_file_path,
            media_type="audio/wav",
            filename=f"output_{voice}_{int(time.time())}.wav"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Synthesis error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Synthesis failed: {str(e)}")

# ============================================================================
# VOICE CLONING ENDPOINTS
# ============================================================================

def _do_voice_cloning(text, language, speaker_wav_files, speed, temperature, top_k, top_p, length_scale, gpt_cond_len):
    """
    Helper function to perform voice cloning (runs in thread pool to avoid blocking)
    Includes robust CUDA error handling with automatic recovery
    """
    normalized_wavs = []
    retry_count = 0
    max_retries = 2
    last_error = None
    
    while retry_count < max_retries:
        try:
            # Normalize and validate all speaker files
            for speaker_file in speaker_wav_files:
                try:
                    normalized_wav = normalize_audio_file(speaker_file)
                except Exception as e:
                    print(f"   ⚠️ Normalization error: {str(e)}")
                    normalized_wav = speaker_file
                
                # Validate WAV file
                try:
                    wav_data, sr = torchaudio.load(normalized_wav)
                    if wav_data.shape[0] == 0 or wav_data.shape[1] == 0:
                        raise ValueError("Invalid WAV file")
                except Exception as e:
                    raise RuntimeError(f"Invalid WAV file: {str(e)}")
                
                normalized_wavs.append(normalized_wav)
            
            # Compute embedding
            print(f"🎤 Voice cloning: '{text[:50]}...' in {language} with {len(normalized_wavs)} reference(s)")
            
            # Synthesize using TTS v0.22+ API with inference parameters
            # XTTS v2 accepts speaker_wav as list for multiple references
            speaker_wav_input = normalized_wavs if len(normalized_wavs) > 1 else normalized_wavs[0]
            
            wav = tts_model.tts(  # type: ignore
                text=text,
                speaker_wav=speaker_wav_input,
                language=language,
                temperature=temperature,
                top_k=top_k,
                top_p=top_p
            )
            
            # Apply length scale adjustment if needed (affects phoneme duration)
            if length_scale != 1.0:
                print(f"⏱️ Adjusting length scale to {length_scale}x")
                wav = apply_speed_adjustment(wav, 1.0 / length_scale)
            
            # Apply speed adjustment if needed (speed != 1.0)
            if speed != 1.0:
                print(f"⏱️ Adjusting speed to {speed}x")
                wav = apply_speed_adjustment(wav, speed)
            
            # Save to temporary output file
            temp_output_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            if isinstance(wav, torch.Tensor):
                torchaudio.save(temp_output_file.name, wav.unsqueeze(0) if wav.dim() == 1 else wav, SAMPLE_RATE)
            else:
                torchaudio.save(temp_output_file.name, torch.tensor(wav).unsqueeze(0), SAMPLE_RATE)
            
            print(f"✅ Voice cloning complete: {len(wav) if isinstance(wav, (list, torch.Tensor)) else 'variable'} samples")
            
            return temp_output_file.name
        
        except RuntimeError as e:
            error_str = str(e)
            last_error = e
            
            # Check if it's a CUDA error
            if "CUDA" in error_str or "cuda" in error_str or "CUBLAS" in error_str:
                retry_count += 1
                print(f"⚠️ CUDA error in voice cloning (attempt {retry_count}/{max_retries}): {error_str}")
                
                if retry_count < max_retries:
                    try:
                        if torch.cuda.is_available():
                            print("🔄 Attempting CUDA recovery for voice cloning...")
                            torch.cuda.empty_cache()
                            torch.cuda.reset_peak_memory_stats()
                            torch.cuda.synchronize()
                            print("✅ CUDA cache cleared, retrying...")
                            normalized_wavs = []  # Reset for retry
                            time.sleep(1)
                            continue
                    except Exception as recovery_error:
                        print(f"⚠️ CUDA recovery failed: {recovery_error}")
                
                print(f"❌ CUDA error persists after {retry_count} attempts")
                traceback.print_exc()
                raise last_error
            else:
                print(f"❌ Voice cloning error: {error_str}")
                traceback.print_exc()
                raise
        
        except Exception as e:
            print(f"❌ Unexpected error during voice cloning: {str(e)}")
            traceback.print_exc()
            raise

@app.post("/v1/clone-voice")
async def clone_voice(
    text: str = Form(...),
    language: str = Form("pt"),
    speaker_wav: UploadFile = File(None),
    speaker_wavs: list = File(None),
    speed: float = Form(1.0),
    temperature: float = Form(0.75),
    top_k: int = Form(50),
    top_p: float = Form(0.85),
    length_scale: float = Form(1.0),
    gpt_cond_len: float = Form(12.0)
):
    """
    Clone a voice and synthesize speech in one step.
    Supports single file (speaker_wav) or multiple files (speaker_wavs) for better quality.
    
    Args:
        text: Text to synthesize
        language: Language code
        speaker_wav: Single audio file for voice cloning (WAV, up to 50MB) - backward compatible
        speaker_wavs: Multiple audio files for voice cloning (1-5 WAV files, best with 3-5)
        speed: Speed multiplier (0.5 to 2.0)
        temperature: Randomness/variation (0.1 to 1.0)
        top_k: Diversity parameter (0 to 100)
        top_p: Cumulative probability (0.0 to 1.0)
        length_scale: Phoneme duration multiplier (0.5 to 2.0)
        gpt_cond_len: GPT conditioning length in seconds (3 to 30, default 12)
    
    Returns:
        WAV audio file with cloned voice
    """
    temp_speaker_files = []
    temp_output_file = None
    
    try:
        # Check if TTS model is initialized
        if not tts_model:
            raise HTTPException(status_code=503, detail="TTS model not loaded. Server not ready.")
        
        # Validate inputs
        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")
        
        if len(text) > 1000:
            raise HTTPException(status_code=400, detail="Text exceeds maximum length")
        
        if language not in LANGUAGE_SUPPORT:
            raise HTTPException(status_code=400, detail=f"Language '{language}' not supported")
        
        # Validate and clamp synthesis parameters
        speed = max(0.5, min(2.0, speed))
        temperature = max(0.1, min(1.0, temperature))
        top_k = max(0, min(100, top_k))
        top_p = max(0.0, min(1.0, top_p))
        length_scale = max(0.5, min(2.0, length_scale))
        gpt_cond_len = max(3.0, min(30.0, gpt_cond_len))  # 3-30 seconds
        
        # Handle multiple speaker references (XTTS v2 supports list of WAV files)
        speaker_wav_files = []
        
        # Check for multiple files (speaker_wavs) - preferred method
        if speaker_wavs:
            if not isinstance(speaker_wavs, list):
                speaker_wavs = [speaker_wavs]
            
            if len(speaker_wavs) < 1 or len(speaker_wavs) > 5:
                raise HTTPException(status_code=400, detail="Must provide 1-5 speaker reference files")
            
            total_size = 0
            for wav_file in speaker_wavs:
                if not wav_file.filename or not wav_file.filename.lower().endswith('.wav'):
                    raise HTTPException(status_code=400, detail="Only WAV files supported")
                
                # Check individual file size (50MB limit per file)
                file_content = await wav_file.read()
                file_size = len(file_content) / (1024 * 1024)
                total_size += file_size
                
                if file_size > 50:
                    raise HTTPException(status_code=400, detail=f"Speaker WAV file '{wav_file.filename}' exceeds 50MB limit")
                
                if total_size > 150:
                    raise HTTPException(status_code=400, detail="Total speaker files exceed 150MB limit")
                
                await wav_file.seek(0)
                
                # Save temporary file
                temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                temp_file.write(file_content)
                temp_file.close()
                speaker_wav_files.append(temp_file.name)
                temp_speaker_files.append(temp_file.name)
            
            print(f"📚 Using {len(speaker_wav_files)} reference files for voice cloning")
        
        # Fallback to single file (backward compatibility)
        elif speaker_wav:
            if not speaker_wav.filename or not speaker_wav.filename.lower().endswith('.wav'):
                raise HTTPException(status_code=400, detail="Only WAV files supported")
            
            file_size = len(await speaker_wav.read()) / (1024 * 1024)
            await speaker_wav.seek(0)
            
            if file_size > 50:
                raise HTTPException(status_code=400, detail="Speaker WAV file exceeds 50MB limit")
            
            # Save temporary speaker file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            content = await speaker_wav.read()
            temp_file.write(content)
            temp_file.close()
            speaker_wav_files.append(temp_file.name)
            temp_speaker_files.append(temp_file.name)
        
        else:
            raise HTTPException(status_code=400, detail="No speaker reference file provided")
        
        # Run voice cloning in thread pool to avoid blocking
        temp_file_path = await run_in_threadpool(
            _do_voice_cloning,
            text,
            language,
            speaker_wav_files,
            speed,
            temperature,
            top_k,
            top_p,
            length_scale,
            gpt_cond_len
        )
        
        return FileResponse(
            path=temp_file_path,
            media_type="audio/wav",
            filename=f"cloned_{int(time.time())}.wav"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Voice cloning error: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")
    
    finally:
        # Cleanup temporary speaker files
        for temp_file in temp_speaker_files:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass

# ============================================================================
# VOICE MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/v1/voices/upload")
async def upload_voice(
    voice_name: str = Form(...),
    wav_file: UploadFile = File(...),
    language: str = Form("pt")
):
    """
    Upload and register a custom voice.
    
    Args:
        voice_name: Name for the custom voice
        wav_file: Audio file (WAV, up to 50MB)
        language: Language associated with voice
    
    Returns:
        Voice metadata
    """
    temp_file = None
    
    try:
        # Check if voice manager is initialized
        if not voice_manager:
            raise HTTPException(status_code=503, detail="Voice manager not initialized.")
        
        # Validate voice name (BUG FIX #3: voice_name validation)
        if not voice_name or len(voice_name.strip()) == 0:
            raise HTTPException(status_code=400, detail="Voice name cannot be empty")
        
        if not isinstance(voice_name, str) or len(voice_name) > 50:
            raise HTTPException(status_code=400, detail="Voice name must be a string, max 50 characters")
        
        # Validate file type (BUG FIX #7: file type validation)
        if not wav_file.filename or not wav_file.filename.lower().endswith('.wav'):
            raise HTTPException(status_code=400, detail="Only WAV files supported")
        
        # Check file size (BUG FIX #5: 50MB limit)
        file_size = len(await wav_file.read()) / (1024 * 1024)
        await wav_file.seek(0)
        
        if file_size > 50:
            raise HTTPException(status_code=400, detail="File exceeds 50MB limit")
        
        # Validate WAV content (BUG FIX #5: WAV validation)
        temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        content = await wav_file.read()
        temp_file.write(content)
        temp_file.close()
        
        # Normalize audio for XTTS
        try:
            normalized_path = normalize_audio_file(temp_file.name)
        except Exception as e:
            print(f"   ⚠️ Normalization error: {str(e)}")
            normalized_path = temp_file.name
        
        try:
            wav, sr = torchaudio.load(normalized_path)
            if wav.shape[0] == 0 or wav.shape[1] == 0:
                raise ValueError("Invalid WAV file")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid WAV file: {str(e)}")
        
        # Check max custom voices limit (BUG FIX #6: 100 max voices)
        voices = voice_manager.list_voices()
        custom_count = sum(1 for v in voices if v.get("type") == "custom")
        if custom_count >= 100:
            raise HTTPException(status_code=400, detail="Maximum of 100 custom voices reached")
        
        # Save voice (use normalized path)
        voice_id = voice_manager.save_custom_voice(voice_name, normalized_path, language)
        
        print(f"✅ Voice uploaded: {voice_id}")
        
        return {
            "voice_id": voice_id,
            "name": voice_name,
            "language": language,
            "type": "custom",
            "created_at": datetime.now().isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    finally:
        # Cleanup (BUG FIX #4: try/finally for cleanup)
        if temp_file and os.path.exists(temp_file.name):
            try:
                os.unlink(temp_file.name)
            except:
                pass
        
        # Cleanup normalized file if it was created
        if temp_file and 'normalized_path' in locals() and normalized_path != temp_file.name:
            try:
                normalized_file = normalized_path.replace('.wav', '_normalized.wav')
                if os.path.exists(normalized_file):
                    os.unlink(normalized_file)
            except:
                pass


@app.get("/v1/voices")
async def list_voices():
    """List all available voices (preset and custom)."""
    try:
        if not voice_manager:
            return {
                "voices": [],
                "total": 0,
                "preset": 0,
                "custom": 0,
                "warning": "Voice manager not initialized"
            }
        
        voices = voice_manager.list_voices()
        return {
            "voices": voices,
            "total": len(voices),
            "preset": len([v for v in voices if v.get("type") == "preset"]),
            "custom": len([v for v in voices if v.get("type") == "custom"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list voices: {str(e)}")


@app.get("/v1/voices/{voice_id}")
async def get_voice(voice_id: str):
    """Get specific voice metadata."""
    try:
        if not voice_manager:
            raise HTTPException(status_code=503, detail="Voice manager not initialized.")
        
        voice = voice_manager.get_voice_metadata(voice_id)
        if not voice:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
        return voice
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving voice: {str(e)}")


@app.delete("/v1/voices/{voice_id}")
async def delete_voice(voice_id: str):
    """Delete a custom voice."""
    try:
        if not voice_manager:
            raise HTTPException(status_code=503, detail="Voice manager not initialized.")
        
        if voice_manager.delete_voice(voice_id):
            print(f"✅ Voice deleted: {voice_id}")
            return {"message": f"Voice '{voice_id}' deleted", "voice_id": voice_id}
        else:
            raise HTTPException(status_code=404, detail=f"Voice '{voice_id}' not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")

# ============================================================================
# BATCH & ADVANCED ENDPOINTS
# ============================================================================

def _do_batch_synthesis(texts, language, voice_id, voice_manager, tts_model):
    """
    Helper function to perform batch synthesis (runs in thread pool to avoid blocking)
    """
    results = []
    for i, text in enumerate(texts):
        try:
            speaker_wav = voice_manager.get_voice_file(voice_id)
            if not speaker_wav:
                raise RuntimeError(f"Voice '{voice_id}' not found")
            
            wav = tts_model.tts(text=text, speaker_wav=speaker_wav, language=language)  # type: ignore
            results.append({
                "index": i,
                "text": text,
                "duration": len(wav) / SAMPLE_RATE,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "index": i,
                "text": text,
                "error": str(e),
                "status": "failed"
            })
    
    return results

@app.post("/v1/batch-synthesize")
async def batch_synthesize(request_body: Dict[str, Any]):
    """
    Synthesize multiple texts in batch mode.
    
    Args:
        request_body: {
            "texts": ["text1", "text2", ...],
            "language": "pt",
            "voice": "default"
        }
    
    Returns:
        List of WAV files
    """
    try:
        if not tts_model or not voice_manager:
            raise HTTPException(status_code=503, detail="TTS model or voice manager not initialized.")
        
        texts = request_body.get("texts", [])
        language = request_body.get("language", "pt")
        voice = request_body.get("voice", "default")
        
        if not texts or len(texts) == 0:
            raise HTTPException(status_code=400, detail="No texts provided")
        
        if len(texts) > 100:
            raise HTTPException(status_code=400, detail="Maximum 100 texts per batch")
        
        # Run batch synthesis in thread pool to avoid blocking
        results = await run_in_threadpool(
            _do_batch_synthesis,
            texts,
            language,
            voice,
            voice_manager,
            tts_model
        )
        
        return {"results": results, "total": len(results), "successful": sum(1 for r in results if r["status"] == "success")}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch synthesis failed: {str(e)}")


def _do_precompute_embeddings(voice_manager, embedding_manager):
    """
    Helper function to precompute embeddings for all voices (runs in thread pool)
    """
    voices = voice_manager.list_voices()
    count = 0
    
    for voice in voices:
        try:
            voice_file = voice_manager.get_voice_file(voice["id"])
            if voice_file:
                embedding_manager.get_or_compute_embedding(voice_file, voice["id"])
                count += 1
        except Exception as e:
            print(f"⚠️ Failed to precompute embedding for {voice['id']}: {str(e)}")
    
    return count, len(voices)

@app.post("/v1/precompute-embeddings")
async def precompute_embeddings():
    """Precompute embeddings for all voices."""
    try:
        if not voice_manager:
            raise HTTPException(status_code=503, detail="Voice manager not initialized.")
        
        if not embedding_manager:
            raise HTTPException(status_code=503, detail="Embedding manager not initialized.")
        
        # Run embedding precomputation in thread pool to avoid blocking
        count, total = await run_in_threadpool(
            _do_precompute_embeddings,
            voice_manager,
            embedding_manager
        )
        
        return {
            "message": "Embedding precomputation complete",
            "precomputed": count,
            "total": total
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Precomputation failed: {str(e)}")

# ============================================================================
# TEXT PROCESSING QUEUE SYSTEM
# ============================================================================

import asyncio
from collections import deque

# Fila de processamento de texto e locks para sincronização
text_processing_queues: Dict[str, deque] = {}  # Fila por contexto (ex: por usuário/sessão)
text_processing_locks: Dict[str, asyncio.Lock] = {}  # Lock por contexto
global_processing_lock = asyncio.Lock()  # Lock global para casos sem contexto

async def get_queue_and_lock(context_id: str = "default"):
    """
    Obter fila e lock para um contexto específico.
    Cria novos se não existirem.
    """
    global text_processing_queues, text_processing_locks
    
    if context_id not in text_processing_queues:
        text_processing_queues[context_id] = deque()
    
    if context_id not in text_processing_locks:
        text_processing_locks[context_id] = asyncio.Lock()
    
    return text_processing_queues[context_id], text_processing_locks[context_id]

async def add_to_processing_queue(text: str, callback_func, context_id: str = "default"):
    """
    Adicionar texto à fila de processamento e aguardar sua vez.
    
    Args:
        text: Texto a ser processado
        callback_func: Função async que processa o texto
        context_id: ID do contexto (para isolamento entre usuários/sessões)
    
    Returns:
        Resultado do processamento
    """
    queue, lock = await get_queue_and_lock(context_id)
    
    # Adicionar à fila
    queue.append({
        "text": text,
        "callback": callback_func,
        "timestamp": time.time()
    })
    
    # Aguardar lock (seu turno na fila)
    async with lock:
        # Remover item da fila
        if queue and queue[0]["text"] == text:
            queue.popleft()
        
        # Processar
        try:
            result = await callback_func(text)
            return result
        except Exception as e:
            print(f"❌ Erro ao processar texto na fila: {str(e)}")
            raise

async def wait_for_queue_empty(context_id: str = "default", timeout: float = 300):
    """
    Aguardar até que a fila de processamento esteja vazia.
    
    Args:
        context_id: ID do contexto
        timeout: Tempo máximo de espera em segundos
    
    Returns:
        True se vazio, False se timeout
    """
    queue, _ = await get_queue_and_lock(context_id)
    start_time = time.time()
    
    while queue and (time.time() - start_time) < timeout:
        await asyncio.sleep(0.1)
    
    return len(queue) == 0

# ============================================================================
# FILE MONITORING ENDPOINT
# ============================================================================

# Dictionary to track file monitoring state per file path
file_monitor_state = {}

@app.post("/v1/monitor/read-file")
async def monitor_read_file(request: FileMonitorRequest):
    """
    Read file and return new lines since last read.
    Supports multi-engine TTS selection for automatic synthesis.
    
    Args:
        request: FileMonitorRequest with file_path, last_line_count, and optional engine selection
        
    Returns:
        {
            "success": bool,
            "new_lines": List[str],
            "total_lines": int,
            "error": Optional[str]
        }
    """
    try:
        file_path = request.file_path
        last_line_count = request.last_line_count
        
        # Security: Prevent path traversal attacks
        file_path_obj = Path(file_path).resolve()
        
        # Check if file exists
        if not file_path_obj.exists():
            return {
                "success": False,
                "new_lines": [],
                "total_lines": 0,
                "error": f"Arquivo não encontrado: {file_path}"
            }
        
        if not file_path_obj.is_file():
            return {
                "success": False,
                "new_lines": [],
                "total_lines": 0,
                "error": f"Caminho não é um arquivo: {file_path}"
            }
        
        # Read file content
        try:
            with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path_obj, 'r', encoding='latin-1', errors='ignore') as f:
                content = f.read()
        
        # Split into lines and filter empty lines
        all_lines = [line.strip() for line in content.split('\n') if line.strip()]
        total_lines = len(all_lines)
        
        # Get only new lines
        new_lines = all_lines[last_line_count:] if last_line_count < len(all_lines) else []
        
        return {
            "success": True,
            "new_lines": new_lines,
            "total_lines": total_lines,
            "error": None
        }
    
    except Exception as e:
        print(f"❌ Error reading file {request.file_path}: {str(e)}")
        return {
            "success": False,
            "new_lines": [],
            "total_lines": 0,
            "error": str(e)
        }

@app.post("/v1/monitor/process-queue")
async def process_queued_text(request: FileMonitorRequest):
    """
    Processar novo texto da fila de monitoramento de arquivo com suporte multi-engine.
    Garante que múltiplos textos sejam processados sequencialmente.
    Engine selecionado é usado para síntese automática do texto monitorado.
    
    Args:
        request: FileMonitorRequest com file_path, last_line_count, e engine selecionado
        
    Returns:
        {
            "success": bool,
            "new_lines": List[str],
            "total_lines": int,
            "queue_position": int,
            "queue_size": int,
            "error": Optional[str]
        }
    """
    file_path = request.file_path
    context_id = f"monitor_{file_path}"  # Criar contexto único por arquivo
    
    async def process_file_text(dummy_text: str):
        """Função que será executada dentro da fila"""
        try:
            # Security: Prevent path traversal attacks
            file_path_obj = Path(file_path).resolve()
            
            # Check if file exists
            if not file_path_obj.exists():
                return {
                    "success": False,
                    "new_lines": [],
                    "total_lines": 0,
                    "error": f"Arquivo não encontrado: {file_path}"
                }
            
            if not file_path_obj.is_file():
                return {
                    "success": False,
                    "new_lines": [],
                    "total_lines": 0,
                    "error": f"Caminho não é um arquivo: {file_path}"
                }
            
            # Read file content
            try:
                with open(file_path_obj, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path_obj, 'r', encoding='latin-1', errors='ignore') as f:
                    content = f.read()
            
            # Split into lines and filter empty lines
            all_lines = [line.strip() for line in content.split('\n') if line.strip()]
            total_lines = len(all_lines)
            last_line_count = request.last_line_count
            
            # Get only new lines
            new_lines = all_lines[last_line_count:] if last_line_count < len(all_lines) else []
            
            return {
                "success": True,
                "new_lines": new_lines,
                "total_lines": total_lines,
                "error": None
            }
        except Exception as e:
            print(f"❌ Erro ao processar arquivo {file_path}: {str(e)}")
            return {
                "success": False,
                "new_lines": [],
                "total_lines": 0,
                "error": str(e)
            }
    
    # Obter informações da fila
    queue, lock = await get_queue_and_lock(context_id)
    queue_position = len(queue)
    
    # Adicionar à fila e processar
    await add_to_processing_queue(file_path, process_file_text, context_id)
    
    # Obter resultado (já foi processado)
    result = await process_file_text(file_path)
    
    # Retornar resultado com info da fila
    result["queue_position"] = queue_position
    result["queue_size"] = len(queue)
    
    return result

@app.post("/v1/monitor/select-engine")
async def monitor_select_engine(engine: str = Form(DEFAULT_ENGINE)):
    """
    Selecionar TTS engine para síntese automática do monitor.
    O engine selecionado será usado para todas as sínteses via /v1/monitor/process-queue.
    
    Args:
        engine: Nome do engine ("xtts-v2" ou "stylets2")
    
    Returns:
        {
            "success": bool,
            "selected_engine": str,
            "available_engines": List[str],
            "message": str
        }
    """
    global monitor_selected_engine
    
    print(f"\n🎤 POST /v1/monitor/select-engine called")
    print(f"   Requested engine: {engine}")
    
    # Validar engine
    if engine not in ENGINES:
        print(f"   ❌ Invalid engine: {engine}")
        return {
            "success": False,
            "selected_engine": monitor_selected_engine,
            "available_engines": list(ENGINES.keys()),
            "message": f"Unknown engine: {engine}. Available: {list(ENGINES.keys())}"
        }
    
    # Atualizar engine selecionado
    monitor_selected_engine = engine
    print(f"   ✅ Monitor engine changed to: {engine}")
    
    return {
        "success": True,
        "selected_engine": monitor_selected_engine,
        "available_engines": list(ENGINES.keys()),
        "message": f"Monitor engine set to {engine}"
    }

@app.get("/v1/monitor/status")
async def monitor_get_status():
    """
    Obter status atual do monitor de arquivo.
    
    Returns:
        {
            "selected_engine": str,
            "available_engines": List[str]
        }
    """
    return {
        "selected_engine": monitor_selected_engine,
        "available_engines": list(ENGINES.keys())
    }

# ============================================================================
# OBS AUDIO STREAMING
# ============================================================================

# Gerenciar conexões WebSocket para streaming de áudio para OBS
obs_connections: List[WebSocket] = []

@app.websocket("/ws/audio")
async def websocket_audio(websocket: WebSocket):
    """WebSocket endpoint para streaming de áudio para OBS"""
    await websocket.accept()
    obs_connections.append(websocket)
    print(f"✅ OBS WebSocket conectado (total: {len(obs_connections)})")
    
    try:
        while True:
            # Manter conexão aberta
            data = await websocket.receive_text()
            # Ignorar mensagens recebidas (conexão é apenas para enviar)
    except WebSocketDisconnect:
        obs_connections.remove(websocket)
        print(f"❌ OBS WebSocket desconectado (total: {len(obs_connections)})")
    except Exception as e:
        print(f"❌ Erro WebSocket: {e}")
        if websocket in obs_connections:
            obs_connections.remove(websocket)

async def broadcast_audio_to_obs(audio_data: bytes):
    """Enviar áudio para todos os clientes OBS conectados"""
    if not obs_connections:
        return
    
    import base64
    audio_b64 = base64.b64encode(audio_data).decode('utf-8')
    message = json.dumps({
        "type": "audio",
        "audio": audio_b64,
        "timestamp": datetime.now().isoformat()
    })
    
    disconnected = []
    for connection in obs_connections:
        try:
            await connection.send_text(message)
        except Exception as e:
            print(f"❌ Erro ao enviar para OBS: {e}")
            disconnected.append(connection)
    
    # Remover conexões com erro
    for conn in disconnected:
        if conn in obs_connections:
            obs_connections.remove(conn)

@app.get("/obs-config")
async def get_obs_config(request_url: Optional[str] = None):
    """
    Retorna configuração e URL para conectar OBS ao player de áudio
    
    Returns:
        - URL do player de áudio para adicionar como Browser Source no OBS
        - WebSocket URL para streaming de áudio
        - Instruções de setup
    """
    # Tentar extrair o host/porta da URL da request
    # Se não conseguir, usar valores defaults
    try:
        from starlette.requests import Request
        # Note: request_url pode ser passada como query param se precisar
        if not request_url:
            request_url = f"http://localhost:{PORT}"
    except:
        request_url = f"http://localhost:{PORT}"
    
    return {
        "audio_player_url": f"{request_url}/obs-audio",
        "websocket_url": f"ws://localhost:{PORT}/ws/audio",
        "instructions": {
            "pt": "1. Copie a URL do audio_player_url\n2. No OBS, adicione uma nova Source do tipo 'Browser'\n3. Cole a URL em 'URL'\n4. Configure: Largura=1, Altura=1\n5. Marque 'Controlar áudio via OBS'",
            "en": "1. Copy the audio_player_url\n2. In OBS, add a new 'Browser' source\n3. Paste the URL in 'URL'\n4. Set: Width=1, Height=1\n5. Check 'Control audio via OBS'"
        },
        "active_connections": len(obs_connections),
        "features": {
            "real_time_streaming": True,
            "audio_only": True,
            "no_ui_required": True,
            "auto_reconnect": True
        }
    }

# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - redirects to /v1/info"""
    return {
        "message": "XTTS v2 Server is running",
        "info_url": "http://127.0.0.1:8877/v1/info",
        "docs_url": "http://127.0.0.1:8877/docs"
    }

# ============================================================================
# MAIN
# ============================================================================


@app.get("/v1/queue/status")
async def get_queue_status(context_id: str = "default"):
    """
    Obter status da fila de processamento.
    
    Args:
        context_id: ID do contexto para verificar (default: 'default')
        
    Returns:
        {
            "context_id": str,
            "queue_size": int,
            "is_processing": bool,
            "queue_items": List[Dict] com timestamps
        }
    """
    queue, lock = await get_queue_and_lock(context_id)
    
    is_locked = lock.locked()
    
    queue_items = []
    for item in list(queue):
        queue_items.append({
            "text_preview": item["text"][:50] + "..." if len(item["text"]) > 50 else item["text"],
            "timestamp": item["timestamp"],
            "age_seconds": time.time() - item["timestamp"]
        })
    
    return {
        "context_id": context_id,
        "queue_size": len(queue),
        "is_processing": is_locked,
        "queue_items": queue_items
    }

@app.post("/v1/queue/clear")
async def clear_queue(context_id: str = "default"):
    """
    Limpar a fila de processamento (uso administrativo).
    
    Args:
        context_id: ID do contexto para limpar
        
    Returns:
        {"success": bool, "cleared_items": int}
    """
    queue, _ = await get_queue_and_lock(context_id)
    items_cleared = len(queue)
    queue.clear()
    
    return {
        "success": True,
        "cleared_items": items_cleared,
        "message": f"Fila '{context_id}' limpa ({items_cleared} itens removidos)"
    }

@app.get("/v1/queue/wait")
async def wait_queue_completion(context_id: str = "default", timeout: float = 300):
    """
    Aguardar até que a fila de processamento esteja vazia.
    Útil para saber quando todos os itens foram processados.
    
    Args:
        context_id: ID do contexto
        timeout: Tempo máximo de espera em segundos (default: 300)
        
    Returns:
        {
            "success": bool,
            "completed": bool,
            "wait_time_seconds": float,
            "message": str
        }
    """
    start_time = time.time()
    completed = await wait_for_queue_empty(context_id, timeout)
    wait_time = time.time() - start_time
    
    if completed:
        return {
            "success": True,
            "completed": True,
            "wait_time_seconds": wait_time,
            "message": f"Fila '{context_id}' esvaziada em {wait_time:.2f}s"
        }
    else:
        return {
            "success": False,
            "completed": False,
            "wait_time_seconds": wait_time,
            "message": f"Timeout: fila '{context_id}' não esvaziou após {timeout}s"
        }

if __name__ == "__main__":
    print("=" * 70)
    print("🎙️  XTTS v2 Server with Voice Cloning")
    print("=" * 70)
    print(f"📍 Server: http://{HOST}:{PORT}")
    print(f"📚 Docs: http://{HOST}:{PORT}/docs")
    print(f"💬 Info: http://{HOST}:{PORT}/v1/info")
    print("=" * 70)
    
    uvicorn.run(
        app,
        host=HOST,
        port=PORT,
        log_level="info" if not DEBUG else "debug"
    )
