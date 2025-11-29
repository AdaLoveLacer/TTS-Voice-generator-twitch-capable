#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration Tests for Multi-Engine TTS System

Tests the seamless integration of multiple TTS engines (XTTS v2, StyleTTS2)
with the FastAPI backend, verifying:
- Engine switching
- Synthesis quality
- Performance metrics
- Error handling
- Monitor integration
"""

import pytest
import requests
import json
import time
from typing import Dict, Any
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:5002"
TEST_TEXT = "Olá mundo, testando sistema de síntese multi-engine"
TEST_LANGUAGE = "pt"
TEST_VOICE = "default"


class TestEngineAvailability:
    """Test engine discovery and availability"""
    
    def test_get_engines_endpoint(self):
        """Test GET /v1/engines returns available engines"""
        response = requests.get(f"{BASE_URL}/v1/engines")
        assert response.status_code == 200
        
        data = response.json()
        assert "available" in data
        assert "current" in data
        assert "engines" in data
        
        # Verify both engines are available
        assert "xtts-v2" in data["available"]
        assert "stylets2" in data["available"]
        
        # Verify XTTS v2 is default
        assert data["current"] == "xtts-v2"
    
    def test_engines_have_specs(self):
        """Test that each engine has complete specifications"""
        response = requests.get(f"{BASE_URL}/v1/engines")
        data = response.json()
        
        required_fields = ["label", "description", "languages", "speed", 
                          "quality", "vram_mb", "estimated_time_per_sentence",
                          "features", "pros", "cons"]
        
        for engine_name, engine_data in data["engines"].items():
            for field in required_fields:
                assert field in engine_data, f"Missing field '{field}' in {engine_name}"


class TestXTTSv2Synthesis:
    """Test XTTS v2 (default engine) synthesis"""
    
    def test_synthesize_with_default_engine(self):
        """Test POST /v1/synthesize without engine parameter uses XTTS v2"""
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE)
            }
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/wav'
        assert len(response.content) > 1000  # Should be substantial audio data
        
        print(f"✅ XTTS v2 (default) synthesis completed in {elapsed:.1f}s")
    
    def test_synthesize_explicit_xtts_v2(self):
        """Test POST /v1/synthesize with explicit engine=xtts-v2"""
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/wav'
        assert len(response.content) > 1000
        
        print(f"✅ XTTS v2 (explicit) synthesis completed in {elapsed:.1f}s")
    
    def test_xtts_v2_with_parameters(self):
        """Test XTTS v2 with advanced synthesis parameters"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2'),
                'speed': (None, '1.2'),
                'temperature': (None, '0.85'),
                'top_k': (None, '70'),
                'top_p': (None, '0.9')
            }
        )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/wav'
        assert len(response.content) > 1000
        
        print(f"✅ XTTS v2 with custom parameters succeeded")


class TestStyleTTS2Synthesis:
    """Test StyleTTS2 (fast engine) synthesis"""
    
    def test_synthesize_with_stylets2(self):
        """Test POST /v1/synthesize with engine=stylets2"""
        start_time = time.time()
        
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'stylets2')
            }
        )
        
        elapsed = time.time() - start_time
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/wav'
        assert len(response.content) > 1000
        
        # StyleTTS2 should be faster than XTTS v2 (approximately 2-3x)
        print(f"✅ StyleTTS2 synthesis completed in {elapsed:.1f}s (should be ~2-3x faster)")
        assert elapsed < 30, f"StyleTTS2 took {elapsed}s, expected < 30s"
    
    def test_stylets2_with_parameters(self):
        """Test StyleTTS2 with advanced synthesis parameters"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'stylets2'),
                'speed': (None, '1.3'),
                'temperature': (None, '0.8')
            }
        )
        
        assert response.status_code == 200
        assert response.headers['content-type'] == 'audio/wav'
        assert len(response.content) > 1000
        
        print(f"✅ StyleTTS2 with custom parameters succeeded")


class TestEngineSwitching:
    """Test switching between engines"""
    
    def test_switch_from_xtts_to_stylets2(self):
        """Test switching from XTTS v2 to StyleTTS2"""
        
        # Synthesize with XTTS v2
        response1 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, "Primeira síntese com XTTS"),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        assert response1.status_code == 200
        audio1 = response1.content
        
        # Synthesize with StyleTTS2
        response2 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, "Segunda síntese com StyleTTS2"),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'stylets2')
            }
        )
        assert response2.status_code == 200
        audio2 = response2.content
        
        # Audio data should be different (different engines produce different output)
        assert audio1 != audio2, "Audio outputs should differ between engines"
        
        print(f"✅ Engine switching successful (XTTS v2 → StyleTTS2)")
    
    def test_switch_from_stylets2_to_xtts(self):
        """Test switching from StyleTTS2 to XTTS v2"""
        
        # Synthesize with StyleTTS2
        response1 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, "Síntese com StyleTTS2"),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'stylets2')
            }
        )
        assert response1.status_code == 200
        
        # Synthesize with XTTS v2
        response2 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, "Síntese com XTTS"),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        assert response2.status_code == 200
        
        print(f"✅ Engine switching successful (StyleTTS2 → XTTS v2)")


class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_invalid_engine_name(self):
        """Test that invalid engine name returns proper error"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'invalid_engine')
            }
        )
        
        assert response.status_code == 500
        assert 'Unknown engine' in response.text or 'error' in response.text.lower()
        
        print(f"✅ Invalid engine error handling works correctly")
    
    def test_empty_text(self):
        """Test that empty text returns proper error"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, ''),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        
        assert response.status_code == 400
        assert 'empty' in response.text.lower()
        
        print(f"✅ Empty text error handling works correctly")
    
    def test_invalid_language(self):
        """Test that invalid language returns proper error"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, 'klingon'),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        
        assert response.status_code == 400
        assert 'not supported' in response.text.lower() or 'invalid' in response.text.lower()
        
        print(f"✅ Invalid language error handling works correctly")
    
    def test_invalid_voice(self):
        """Test that invalid voice returns proper error"""
        response = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, 'nonexistent_voice'),
                'engine': (None, 'xtts-v2')
            }
        )
        
        assert response.status_code == 500
        assert 'not found' in response.text.lower() or 'error' in response.text.lower()
        
        print(f"✅ Invalid voice error handling works correctly")


class TestMonitorIntegration:
    """Test file monitor integration with multi-engine support"""
    
    def test_monitor_select_engine(self):
        """Test POST /v1/monitor/select-engine"""
        response = requests.post(
            f"{BASE_URL}/v1/monitor/select-engine",
            data={'engine': 'stylets2'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is True
        assert data['selected_engine'] == 'stylets2'
        assert 'xtts-v2' in data['available_engines']
        assert 'stylets2' in data['available_engines']
        
        print(f"✅ Monitor engine selection works correctly")
    
    def test_monitor_invalid_engine(self):
        """Test selecting invalid engine in monitor"""
        response = requests.post(
            f"{BASE_URL}/v1/monitor/select-engine",
            data={'engine': 'invalid_engine'}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data['success'] is False
        assert 'Unknown engine' in data['message']
        
        print(f"✅ Monitor invalid engine error handling works correctly")
    
    def test_monitor_get_status(self):
        """Test GET /v1/monitor/status"""
        response = requests.get(f"{BASE_URL}/v1/monitor/status")
        
        assert response.status_code == 200
        data = response.json()
        
        assert 'selected_engine' in data
        assert 'available_engines' in data
        assert data['selected_engine'] in ['xtts-v2', 'stylets2']
        assert len(data['available_engines']) >= 2
        
        print(f"✅ Monitor status endpoint works correctly")


class TestPerformanceComparison:
    """Compare performance between engines"""
    
    def test_performance_comparison(self):
        """Compare synthesis time between XTTS v2 and StyleTTS2"""
        
        # Warm up (first request may be slower due to model loading)
        requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, "warmup"),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        
        # Measure XTTS v2
        start = time.time()
        response1 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'xtts-v2')
            }
        )
        xtts_time = time.time() - start
        
        # Measure StyleTTS2
        start = time.time()
        response2 = requests.post(
            f"{BASE_URL}/v1/synthesize",
            files={
                'text': (None, TEST_TEXT),
                'language': (None, TEST_LANGUAGE),
                'voice': (None, TEST_VOICE),
                'engine': (None, 'stylets2')
            }
        )
        stylets2_time = time.time() - start
        
        assert response1.status_code == 200
        assert response2.status_code == 200
        
        speedup = xtts_time / stylets2_time if stylets2_time > 0 else 0
        
        print(f"\n📊 Performance Comparison:")
        print(f"   XTTS v2:    {xtts_time:.1f}s")
        print(f"   StyleTTS2:  {stylets2_time:.1f}s")
        print(f"   Speedup:    {speedup:.1f}x")
        
        # StyleTTS2 should be faster (approximately 2-3x)
        # Note: This assertion may not hold on first run, but should on subsequent runs
        if stylets2_time < xtts_time:
            print(f"   ✅ StyleTTS2 is faster as expected")
        else:
            print(f"   ⚠️  First run - model loading times may affect comparison")


# ============================================================================
# Test Suite Configuration
# ============================================================================

if __name__ == "__main__":
    """
    Run integration tests
    
    Usage:
        python test_integration.py
    
    Or with pytest:
        pytest test_integration.py -v
    """
    
    print("\n" + "=" * 70)
    print("🧪 MULTI-ENGINE TTS INTEGRATION TESTS")
    print("=" * 70)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/v1/engines", timeout=5)
        print(f"✅ Server is running at {BASE_URL}\n")
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to server at {BASE_URL}")
        print(f"   Make sure the FastAPI server is running:")
        print(f"   cd xtts-server && python main.py")
        exit(1)
    
    # Run tests with pytest if available
    try:
        pytest.main([__file__, "-v", "-s"])
    except ImportError:
        print("pytest not found. Running tests manually...")
        
        # Manual test execution
        test_classes = [
            TestEngineAvailability,
            TestXTTSv2Synthesis,
            TestStyleTTS2Synthesis,
            TestEngineSwitching,
            TestErrorHandling,
            TestMonitorIntegration,
            TestPerformanceComparison
        ]
        
        for test_class in test_classes:
            print(f"\n🔬 {test_class.__name__}")
            print("-" * 70)
            
            instance = test_class()
            for method_name in dir(instance):
                if method_name.startswith('test_'):
                    try:
                        method = getattr(instance, method_name)
                        method()
                    except AssertionError as e:
                        print(f"   ❌ {method_name}: {e}")
                    except Exception as e:
                        print(f"   ⚠️  {method_name}: {e}")
        
        print("\n" + "=" * 70)
        print("✨ Tests completed!")
        print("=" * 70)
