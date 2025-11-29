#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de teste: Enviar áudio para OBS
Script para testar a funcionalidade de streaming OBS
"""

import requests
import json
import time
import sys

# Configuração
SERVER_URL = "http://localhost:8877"
LANGUAGE = "pt"
VOICE = "default"

def get_obs_config():
    """Obter configuração de OBS"""
    print("\n📡 Obtendo configuração de OBS...\n")
    try:
        response = requests.get(f"{SERVER_URL}/obs-config")
        if response.status_code == 200:
            config = response.json()
            print("✅ Configuração obtida:\n")
            print(f"  Audio Player URL: {config['audio_player_url']}")
            print(f"  WebSocket URL: {config['websocket_url']}")
            print(f"  Conexões ativas: {config['active_connections']}")
            print(f"  Features: {json.dumps(config['features'], indent=2)}")
            print(f"\n📋 Instruções:\n{config['instructions']['pt']}\n")
            return config
        else:
            print(f"❌ Erro: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def synthesize_and_stream(text):
    """Sintetizar texto e enviar para OBS"""
    print(f"\n🎤 Sintetizando: '{text}'\n")
    try:
        data = {
            "text": text,
            "language": LANGUAGE,
            "voice": VOICE,
            "speed": 1.0,
            "temperature": 0.75,
            "top_k": 50,
            "top_p": 0.85,
            "length_scale": 1.0,
            "gpt_cond_len": 12.0
        }
        
        response = requests.post(
            f"{SERVER_URL}/v1/synthesize",
            data=data,
            timeout=60
        )
        
        if response.status_code == 200:
            print("✅ Áudio sintetizado e enviado para OBS!")
            print(f"   Tamanho: {len(response.content)} bytes")
            print("   🔊 Verifique no OBS se está reproduzindo...")
            return True
        else:
            print(f"❌ Erro na síntese: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def main():
    """Função principal"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║        Speakerbot OBS Audio Streaming - Test Script        ║")
    print("╚════════════════════════════════════════════════════════════╝")
    
    # 1. Verificar configuração
    config = get_obs_config()
    if not config:
        print("❌ Não foi possível conectar ao servidor Speakerbot")
        print(f"   Certifique-se que está rodando em {SERVER_URL}")
        sys.exit(1)
    
    # 2. Testar síntese
    test_texts = [
        "Olá! Bem-vindo ao Speakerbot.",
        "Esse áudio está sendo transmitido em tempo real para o OBS.",
        "Você pode sintetizar qualquer texto e ele aparecerá no seu stream!"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{'='*60}")
        print(f"Teste {i}/{len(test_texts)}")
        print(f"{'='*60}")
        
        if not synthesize_and_stream(text):
            print("⚠️ Falha na síntese")
            continue
        
        time.sleep(3)  # Aguardar antes do próximo
    
    print("\n╔════════════════════════════════════════════════════════════╗")
    print("║                   ✅ Testes Completos!                      ║")
    print("║                                                            ║")
    print("║  Se você ouvi os áudios no OBS, tudo está funcionando! 🎉 ║")
    print("║                                                            ║")
    print("║  Próximos passos:                                         ║")
    print("║  1. Integre com sua aplicação                            ║")
    print("║  2. Configure triggers de síntese                        ║")
    print("║  3. Personalize vozes e parâmetros                       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")

if __name__ == "__main__":
    main()
