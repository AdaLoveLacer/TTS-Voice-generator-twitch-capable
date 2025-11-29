#!/usr/bin/env python3
"""
Speaker Embedding Manager - Manages speaker embeddings with 3-level cache
"""

import os
import pickle
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any
import torch

# ============================================================================
# CONSTANTS
# ============================================================================

EMBEDDINGS_DIR = Path(__file__).parent / "voices" / "embeddings"
EMBEDDING_CACHE_SIZE = 100  # Keep 100 embeddings in memory

# ============================================================================
# SPEAKER EMBEDDING MANAGER CLASS
# ============================================================================

class SpeakerEmbeddingManager:
    """
    Manages speaker embeddings with 3-level cache:
    1. Memory cache (fast, limited size)
    2. Disk cache (pickle files)
    3. GPU computation (compute on demand)
    """
    
    def __init__(self, tts_model):
        """
        Initialize embedding manager.
        
        Args:
            tts_model: TTS model instance with speaker encoder
        """
        self.tts_model = tts_model
        self.embeddings_dir = EMBEDDINGS_DIR
        self.memory_cache: Dict[str, np.ndarray] = {}
        self.cache_order = []  # Track cache insertion order for LRU
        
        # Ensure directory exists
        self.embeddings_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_cache_key(self, voice_id: str) -> str:
        """Get cache key for voice."""
        return f"embedding_{voice_id}"
    
    def _get_disk_cache_path(self, voice_id: str) -> Path:
        """Get disk cache file path for voice."""
        return self.embeddings_dir / f"{voice_id}.pkl"
    
    def get_or_compute_embedding(self, speaker_wav: str, voice_id: str) -> np.ndarray:
        """
        Get speaker embedding, using 3-level cache.
        
        Level 1: Memory cache (fastest)
        Level 2: Disk cache (pickle)
        Level 3: GPU computation (slowest)
        
        Args:
            speaker_wav: Path to speaker WAV file
            voice_id: Voice identifier for caching
        
        Returns:
            Speaker embedding array
        """
        # Level 1: Check memory cache
        cache_key = self._get_cache_key(voice_id)
        if cache_key in self.memory_cache:
            print(f"💾 Embedding cache hit (memory): {voice_id}")
            return self.memory_cache[cache_key]
        
        # Level 2: Check disk cache
        disk_cache_path = self._get_disk_cache_path(voice_id)
        if disk_cache_path.exists():
            try:
                with open(disk_cache_path, 'rb') as f:
                    embedding = pickle.load(f)
                print(f"💾 Embedding cache hit (disk): {voice_id}")
                # Store in memory cache
                self._add_to_memory_cache(cache_key, embedding)
                return embedding
            except Exception as e:
                print(f"⚠️ Failed to load disk cache: {str(e)}")
        
        # Level 3: Compute embedding on GPU
        print(f"🎤 Computing speaker embedding: {voice_id}")
        try:
            embedding = self.compute_embedding(speaker_wav)
            
            # Store in both memory and disk caches
            self._add_to_memory_cache(cache_key, embedding)
            self._save_to_disk_cache(voice_id, embedding)
            
            print(f"✅ Embedding computed and cached: {voice_id}")
            return embedding
        
        except Exception as e:
            print(f"❌ Failed to compute embedding: {str(e)}")
            raise
    
    def compute_embedding(self, speaker_wav: str) -> np.ndarray:
        """
        Compute speaker embedding from WAV file using TTS model.
        
        Args:
            speaker_wav: Path to speaker WAV file
        
        Returns:
            Speaker embedding as numpy array
        """
        try:
            # Use TTS model's speaker encoder to compute embedding
            # The speaker encoder is typically part of the TTS model
            embedding = self.tts_model.speaker_encoder.compute_embedding(speaker_wav)
            
            # Ensure it's a numpy array
            if isinstance(embedding, torch.Tensor):
                embedding = embedding.cpu().numpy()
            
            return embedding.astype(np.float32)
        
        except Exception as e:
            print(f"❌ Embedding computation error: {str(e)}")
            raise
    
    def _add_to_memory_cache(self, cache_key: str, embedding: np.ndarray):
        """
        Add embedding to memory cache with LRU eviction.
        
        Args:
            cache_key: Cache key
            embedding: Speaker embedding
        """
        # Remove if already exists (for LRU update)
        if cache_key in self.cache_order:
            self.cache_order.remove(cache_key)
        
        # Add to cache
        self.memory_cache[cache_key] = embedding
        self.cache_order.append(cache_key)
        
        # Evict oldest if cache is full
        if len(self.memory_cache) > EMBEDDING_CACHE_SIZE:
            oldest_key = self.cache_order.pop(0)
            del self.memory_cache[oldest_key]
            print(f"🗑️  Memory cache evicted: {oldest_key}")
    
    def _save_to_disk_cache(self, voice_id: str, embedding: np.ndarray):
        """
        Save embedding to disk cache.
        
        Args:
            voice_id: Voice identifier
            embedding: Speaker embedding
        """
        try:
            cache_path = self._get_disk_cache_path(voice_id)
            with open(cache_path, 'wb') as f:
                pickle.dump(embedding, f)
            print(f"💾 Embedding saved to disk: {voice_id}")
        except Exception as e:
            print(f"⚠️ Failed to save disk cache: {str(e)}")
    
    def clear_memory_cache(self):
        """Clear memory cache."""
        self.memory_cache.clear()
        self.cache_order.clear()
        print("🗑️  Memory cache cleared")
    
    def clear_disk_cache(self):
        """Clear disk cache."""
        try:
            for cache_file in self.embeddings_dir.glob("*.pkl"):
                cache_file.unlink()
            print("🗑️  Disk cache cleared")
        except Exception as e:
            print(f"⚠️ Failed to clear disk cache: {str(e)}")
    
    def clear_all_cache(self):
        """Clear all caches."""
        self.clear_memory_cache()
        self.clear_disk_cache()
    
    def precompute_embeddings(self, voices: list, voice_manager):
        """
        Precompute embeddings for multiple voices.
        
        Args:
            voices: List of voice metadata dictionaries
            voice_manager: VoiceManager instance
        
        Returns:
            Dictionary with precomputation results
        """
        results = {
            "total": len(voices),
            "computed": 0,
            "cached": 0,
            "failed": 0,
            "details": []
        }
        
        for voice in voices:
            voice_id = voice.get("id")
            try:
                # Check if already cached
                disk_cache_path = self._get_disk_cache_path(voice_id)
                if disk_cache_path.exists():
                    results["cached"] += 1
                    results["details"].append({
                        "voice_id": voice_id,
                        "status": "cached"
                    })
                    continue
                
                # Get voice file and compute embedding
                voice_file = voice_manager.get_voice_file(voice_id)
                if voice_file:
                    embedding = self.get_or_compute_embedding(voice_file, voice_id)
                    results["computed"] += 1
                    results["details"].append({
                        "voice_id": voice_id,
                        "status": "computed"
                    })
                else:
                    results["failed"] += 1
                    results["details"].append({
                        "voice_id": voice_id,
                        "status": "failed",
                        "error": "Voice file not found"
                    })
            
            except Exception as e:
                results["failed"] += 1
                results["details"].append({
                    "voice_id": voice_id,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    def get_cache_statistics(self) -> Dict[str, Any]:
        """Get cache statistics."""
        disk_cache_files = list(self.embeddings_dir.glob("*.pkl"))
        total_disk_size = sum(f.stat().st_size for f in disk_cache_files)
        
        return {
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_max": EMBEDDING_CACHE_SIZE,
            "disk_cache_files": len(disk_cache_files),
            "disk_cache_size_mb": total_disk_size / (1024 * 1024),
            "memory_embeddings": list(self.memory_cache.keys())
        }
    
    def delete_embedding_cache(self, voice_id: str) -> bool:
        """
        Delete embedding cache for a voice.
        
        Args:
            voice_id: Voice identifier
        
        Returns:
            True if deleted, False otherwise
        """
        # Remove from memory cache
        cache_key = self._get_cache_key(voice_id)
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            if cache_key in self.cache_order:
                self.cache_order.remove(cache_key)
        
        # Remove from disk cache
        disk_cache_path = self._get_disk_cache_path(voice_id)
        if disk_cache_path.exists():
            try:
                disk_cache_path.unlink()
                print(f"🗑️  Embedding cache deleted: {voice_id}")
                return True
            except Exception as e:
                print(f"⚠️ Failed to delete embedding cache: {str(e)}")
                return False
        
        return False

# ============================================================================
# MAIN (for testing)
# ============================================================================

if __name__ == "__main__":
    print("Speaker Embedding Manager module loaded")
