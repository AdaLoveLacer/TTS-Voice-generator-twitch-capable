#!/usr/bin/env python3
"""
Create default preset voices for XTTS
Generates sample WAV files for default Portuguese, English, Spanish, and French voices
"""

import sys
import os
from pathlib import Path
import numpy as np
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    import torchaudio
    import torch
except ImportError as e:
    print(f"❌ ERRO: Módulos PyTorch não encontrados: {e}")
    sys.exit(1)

try:
    from scipy.io import wavfile
except ImportError:
    print("❌ ERRO: scipy não encontrado!")
    sys.exit(1)

SAMPLE_RATE = 22050
VOICES_DIR = Path(__file__).parent / "voices"
PRESET_DIR = VOICES_DIR / "presets"
EMBEDDINGS_DIR = VOICES_DIR / "embeddings"

def create_sine_wave(duration_sec=3.0, frequency=440, sample_rate=22050):
    """
    Generate a simple sine wave for testing.
    
    Args:
        duration_sec: Duration in seconds
        frequency: Frequency in Hz
        sample_rate: Sample rate in Hz
    
    Returns:
        Tensor of audio samples
    """
    num_samples = int(duration_sec * sample_rate)
    t = torch.linspace(0, duration_sec, num_samples)
    wave = torch.sin(2 * np.pi * frequency * t)
    # Normalize to [-0.95, 0.95] range
    wave = wave * 0.95
    return wave

def create_default_voices():
    """Create default preset voices."""
    
    # Ensure directories exist
    PRESET_DIR.mkdir(parents=True, exist_ok=True)
    EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Define default voices with different frequencies for variation
    voices_config = {
        "default": {
            "name": "Default",
            "language": "pt",
            "description": "Default Portuguese voice",
            "frequency": 220,  # A3 - lower male voice
        },
        "english": {
            "name": "English",
            "language": "en",
            "description": "Default English voice",
            "frequency": 260,  # C4 - mid voice
        },
        "spanish": {
            "name": "Spanish",
            "language": "es",
            "description": "Default Spanish voice",
            "frequency": 330,  # E4 - mid-high voice
        },
        "french": {
            "name": "French",
            "language": "fr",
            "description": "Default French voice",
            "frequency": 440,  # A4 - high voice
        },
    }
    
    preset_metadata = {}
    
    for voice_id, config in voices_config.items():
        print(f"\n📝 Creating voice: {voice_id} ({config['name']})")
        
        # Generate audio
        wave = create_sine_wave(duration_sec=3.0, frequency=config['frequency'], sample_rate=SAMPLE_RATE)
        
        # Add some variation (simple modulation)
        modulation = torch.sin(2 * np.pi * 5 * torch.linspace(0, 3, len(wave)))  # 5Hz modulation
        wave = wave * (0.7 + 0.3 * modulation)
        
        # Save as WAV
        wav_path = PRESET_DIR / f"{voice_id}.wav"
        
        # Convert to numpy and save with scipy
        wave_np = wave.numpy() * 32767  # Convert to int16 range
        wavfile.write(str(wav_path), SAMPLE_RATE, wave_np.astype(np.int16))
        print(f"   ✅ Saved: {wav_path}")
        
        # Create metadata
        metadata = {
            "id": voice_id,
            "name": config["name"],
            "type": "preset",
            "language": config["language"],
            "description": config["description"],
            "created_at": datetime.now().isoformat(),
            "file_size": wav_path.stat().st_size,
        }
        
        preset_metadata[voice_id] = metadata
        print(f"   📊 Metadata: {config['language']} | {metadata['file_size']} bytes")
    
    # Save metadata
    metadata_file = PRESET_DIR / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(preset_metadata, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved metadata: {metadata_file}")
    
    # Print summary
    print(f"\n📊 Summary:")
    print(f"   📂 Preset directory: {PRESET_DIR}")
    print(f"   📂 Embeddings directory: {EMBEDDINGS_DIR}")
    print(f"   🎤 Voices created: {len(preset_metadata)}")
    for voice_id, meta in preset_metadata.items():
        print(f"      - {voice_id}: {meta['language']}")

if __name__ == "__main__":
    try:
        create_default_voices()
        print("\n✨ Default voices created successfully!")
    except Exception as e:
        print(f"\n❌ ERRO ao criar vozes: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
