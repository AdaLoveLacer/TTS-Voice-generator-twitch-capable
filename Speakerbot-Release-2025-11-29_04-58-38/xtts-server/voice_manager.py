#!/usr/bin/env python3
"""
Voice Manager - Manages voice registration, persistence, and metadata
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

# ============================================================================
# CONSTANTS
# ============================================================================

VOICES_DIR = Path(__file__).parent / "voices"
CUSTOM_VOICES_DIR = VOICES_DIR / "custom"
PRESET_VOICES_DIR = VOICES_DIR / "presets"
EMBEDDINGS_DIR = VOICES_DIR / "embeddings"

MAX_VOICE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_CUSTOM_VOICES = 100

# ============================================================================
# VOICE MANAGER CLASS
# ============================================================================

class VoiceManager:
    """Manages voice registration, storage, and metadata persistence."""
    
    def __init__(self):
        """Initialize voice manager and create necessary directories."""
        self.voices_dir = VOICES_DIR
        self.custom_dir = CUSTOM_VOICES_DIR
        self.preset_dir = PRESET_VOICES_DIR
        self.embeddings_dir = EMBEDDINGS_DIR
        
        # Create directories
        self._ensure_directories()
        
        # Load voices
        self.voices = {}
        self._load_voices()
    
    def _ensure_directories(self):
        """Create necessary directory structure."""
        self.voices_dir.mkdir(parents=True, exist_ok=True)
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        self.preset_dir.mkdir(parents=True, exist_ok=True)
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_voices(self):
        """Load voice metadata from disk."""
        # Load preset voices
        metadata_file = self.preset_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    preset_data = json.load(f)
                    for voice_id, voice_info in preset_data.items():
                        self.voices[voice_id] = voice_info
            except Exception as e:
                print(f"⚠️ Failed to load preset voices: {str(e)}")
        
        # Load custom voices
        metadata_file = self.custom_dir / "metadata.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    custom_data = json.load(f)
                    for voice_id, voice_info in custom_data.items():
                        self.voices[voice_id] = voice_info
            except Exception as e:
                print(f"⚠️ Failed to load custom voices: {str(e)}")
        
        # If no voices loaded, create defaults
        if not self.voices:
            self._create_default_voices()
    
    def _create_default_voices(self):
        """Create default preset voices."""
        default_voices = {
            "default": {
                "id": "default",
                "name": "Default",
                "type": "preset",
                "language": "pt",
                "description": "Default Portuguese voice",
                "created_at": datetime.now().isoformat()
            },
            "english": {
                "id": "english",
                "name": "English",
                "type": "preset",
                "language": "en",
                "description": "Default English voice",
                "created_at": datetime.now().isoformat()
            },
            "spanish": {
                "id": "spanish",
                "name": "Spanish",
                "type": "preset",
                "language": "es",
                "description": "Default Spanish voice",
                "created_at": datetime.now().isoformat()
            },
            "french": {
                "id": "french",
                "name": "French",
                "type": "preset",
                "language": "fr",
                "description": "Default French voice",
                "created_at": datetime.now().isoformat()
            },
        }
        
        # For presets, use voice name as file path
        self.voices = default_voices
        self._save_preset_metadata()
    
    def _save_preset_metadata(self):
        """Save preset voice metadata."""
        preset_voices = {k: v for k, v in self.voices.items() if v.get("type") == "preset"}
        metadata_file = self.preset_dir / "metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(preset_voices, f, indent=2, ensure_ascii=False)
    
    def _save_custom_metadata(self):
        """Save custom voice metadata."""
        custom_voices = {k: v for k, v in self.voices.items() if v.get("type") == "custom"}
        metadata_file = self.custom_dir / "metadata.json"
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(custom_voices, f, indent=2, ensure_ascii=False)
    
    def get_voice_file(self, voice_id: str) -> Optional[str]:
        """
        Get the file path for a voice.
        
        Args:
            voice_id: Voice identifier
        
        Returns:
            Path to voice WAV file or None if not found
        """
        if voice_id not in self.voices:
            return None
        
        voice_info = self.voices[voice_id]
        
        if voice_info.get("type") == "preset":
            # For presets, use voice ID as filename
            voice_file = self.preset_dir / f"{voice_id}.wav"
        else:
            # For custom voices, look for the file
            voice_file = self.custom_dir / f"{voice_id}.wav"
        
        if voice_file.exists():
            return str(voice_file)
        
        return None
    
    def get_voice_metadata(self, voice_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice metadata.
        
        Args:
            voice_id: Voice identifier
        
        Returns:
            Voice metadata dictionary or None if not found
        """
        return self.voices.get(voice_id)
    
    def list_voices(self) -> List[Dict[str, Any]]:
        """
        List all available voices.
        
        Returns:
            List of voice metadata dictionaries
        """
        return list(self.voices.values())
    
    def save_custom_voice(self, name: str, wav_file: str, language: str = "pt") -> str:
        """
        Save a custom voice.
        
        BUG FIX #6: Added MAX_CUSTOM_VOICES limit check
        
        Args:
            name: Voice name
            wav_file: Path to WAV file
            language: Language code
        
        Returns:
            Voice ID
        
        Raises:
            ValueError: If voice name is invalid or limits exceeded
        """
        # Validate voice name (BUG FIX #3)
        if not name or not isinstance(name, str):
            raise ValueError("Invalid voice name")
        
        name = name.strip()
        if len(name) == 0 or len(name) > 50:
            raise ValueError("Voice name must be 1-50 characters")
        
        # Check max custom voices limit (BUG FIX #6)
        custom_count = sum(1 for v in self.voices.values() if v.get("type") == "custom")
        if custom_count >= MAX_CUSTOM_VOICES:
            raise ValueError(f"Maximum of {MAX_CUSTOM_VOICES} custom voices reached")
        
        # Check file size (BUG FIX #5)
        file_size = os.path.getsize(wav_file)
        if file_size > MAX_VOICE_SIZE:
            raise ValueError(f"Voice file exceeds {MAX_VOICE_SIZE / (1024*1024):.0f}MB limit")
        
        # Generate voice ID
        voice_id = str(uuid.uuid4())[:8]
        
        # Copy WAV file
        dest_file = self.custom_dir / f"{voice_id}.wav"
        shutil.copy2(wav_file, dest_file)
        
        # Create metadata
        voice_info = {
            "id": voice_id,
            "name": name,
            "type": "custom",
            "language": language,
            "file_size": file_size,
            "created_at": datetime.now().isoformat()
        }
        
        # Save metadata
        self.voices[voice_id] = voice_info
        self._save_custom_metadata()
        
        print(f"✅ Custom voice saved: {voice_id} ({name})")
        
        return voice_id
    
    def delete_voice(self, voice_id: str) -> bool:
        """
        Delete a voice (preset or custom).
        
        Args:
            voice_id: Voice identifier
        
        Returns:
            True if deleted, False if not found
        """
        if voice_id not in self.voices:
            return False
        
        voice_info = self.voices[voice_id]
        is_preset = voice_info.get("type") == "preset"
        
        # Delete WAV file if exists
        voice_file = self.custom_dir / f"{voice_id}.wav"
        if voice_file.exists():
            voice_file.unlink()
        
        # Also check in presets directory for preset voices
        preset_file = self.preset_dir / f"{voice_id}.wav"
        if preset_file.exists():
            preset_file.unlink()
        
        # Delete embedding cache if exists
        embedding_file = self.embeddings_dir / f"{voice_id}.pkl"
        if embedding_file.exists():
            embedding_file.unlink()
        
        # Remove from metadata
        del self.voices[voice_id]
        
        # Save appropriate metadata file based on voice type
        if is_preset:
            self._save_preset_metadata()
        else:
            self._save_custom_metadata()
        
        print(f"✅ Voice deleted: {voice_id}")
        
        return True
    
    def register_preset_voice(self, voice_id: str, name: str, language: str = "pt"):
        """
        Register a preset voice.
        
        Args:
            voice_id: Voice identifier
            name: Voice name
            language: Language code
        """
        voice_info = {
            "id": voice_id,
            "name": name,
            "type": "preset",
            "language": language,
            "created_at": datetime.now().isoformat()
        }
        
        self.voices[voice_id] = voice_info
        self._save_preset_metadata()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get voice statistics."""
        voices = self.voices.values()
        custom_voices = [v for v in voices if v.get("type") == "custom"]
        preset_voices = [v for v in voices if v.get("type") == "preset"]
        
        total_size = sum(v.get("file_size", 0) for v in custom_voices)
        
        return {
            "total_voices": len(voices),
            "preset_voices": len(preset_voices),
            "custom_voices": len(custom_voices),
            "total_size_mb": total_size / (1024 * 1024),
            "max_custom_voices": MAX_CUSTOM_VOICES,
            "custom_voices_used": len(custom_voices),
            "custom_voices_remaining": MAX_CUSTOM_VOICES - len(custom_voices)
        }

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    manager = VoiceManager()
    print("📊 Voice Statistics:")
    stats = manager.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
