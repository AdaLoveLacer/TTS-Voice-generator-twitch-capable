#!/usr/bin/env python3
"""
Quick test script to verify frontend engine integration
Tests the synthesize endpoint with engine parameter
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_engines_endpoint():
    """Test that /v1/engines endpoint returns available engines"""
    print("\n🧪 Testing /v1/engines endpoint...")
    try:
        response = requests.get(f"{API_URL}/v1/engines")
        data = response.json()
        
        print(f"✅ Response status: {response.status_code}")
        print(f"   Available engines: {list(data.get('engines', {}).keys())}")
        
        if 'xtts-v2' in data.get('engines', {}) and 'stylets2' in data.get('engines', {}):
            print("✅ Both XTTS v2 and StyleTTS2 are available!")
            return True
        else:
            print("❌ Not all engines available")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_synthesize_with_engine(engine: str, text: str = "Olá, mundo!"):
    """Test synthesis with specific engine"""
    print(f"\n🧪 Testing /v1/synthesize with engine: {engine}...")
    try:
        form_data = {
            'text': text,
            'language': 'pt',
            'voice': 'Joana',
            'engine': engine,
            'speed': 1.0,
            'temperature': 0.75,
            'top_k': 50,
            'top_p': 0.85,
            'length_scale': 1.0,
            'gpt_cond_len': 30.0
        }
        
        response = requests.post(
            f"{API_URL}/v1/synthesize",
            data=form_data,
            timeout=60
        )
        
        if response.status_code == 200:
            audio_bytes = response.content
            print(f"✅ Synthesis successful with {engine}")
            print(f"   Audio size: {len(audio_bytes)} bytes")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("🎙️  Frontend Engine Integration Tests")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        print(f"\n✅ Server is running!")
    except:
        print(f"\n❌ Server not running at {API_URL}")
        print("   Please start the server first with: python main.py")
        sys.exit(1)
    
    # Run tests
    results = []
    
    # Test 1: Check engines endpoint
    results.append(("Engines Endpoint", test_engines_endpoint()))
    
    # Test 2: XTTS v2 synthesis
    results.append(("XTTS v2 Synthesis", test_synthesize_with_engine("xtts-v2")))
    
    # Test 3: StyleTTS2 synthesis
    results.append(("StyleTTS2 Synthesis", test_synthesize_with_engine("stylets2")))
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Frontend engine integration is working!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
