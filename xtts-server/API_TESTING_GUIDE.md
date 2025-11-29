# 🧪 API Testing Guide - Multi-Engine TTS

## 1. Verificar Engines Disponíveis

```bash
# cURL
curl -X GET http://localhost:5002/v1/engines

# PowerShell
$response = Invoke-WebRequest -Uri "http://localhost:5002/v1/engines" -Method Get
$response.Content | ConvertFrom-Json | ConvertTo-Json

# Python
import requests
response = requests.get("http://localhost:5002/v1/engines")
print(response.json())
```

### Response Esperado:
```json
{
  "available": ["xtts-v2", "stylets2"],
  "current": "xtts-v2",
  "engines": {
    "xtts-v2": {
      "label": "XTTS v2 (Default)",
      "description": "High-quality multilingual TTS...",
      "languages": 16,
      "speed": "medium",
      "quality": "excellent",
      "vram_mb": 6000,
      "estimated_time_per_sentence": "15-20s",
      "features": ["16 languages support", "Excellent quality", ...],
      "pros": ["Best audio quality", ...],
      "cons": ["Slower synthesis", ...]
    },
    "stylets2": {
      "label": "StyleTTS2 (Fast)",
      "description": "Fast multilingual TTS...",
      "languages": 11,
      "speed": "very-fast",
      "quality": "excellent",
      "vram_mb": 2000,
      "estimated_time_per_sentence": "5-7s",
      ...
    }
  }
}
```

---

## 2. Sintetizar com Engine Padrão (XTTS v2)

```bash
# cURL
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Olá mundo, como você está?" \
  -F "language=pt" \
  -F "voice=default" \
  -F "speed=1.0" \
  -o output_xtts.wav

# PowerShell
$form = @{
    text = "Olá mundo, como você está?"
    language = "pt"
    voice = "default"
    speed = 1.0
}
$response = Invoke-WebRequest -Uri "http://localhost:5002/v1/synthesize" `
  -Method Post -Form $form -OutFile "output_xtts.wav"
```

### Expected Behavior:
- ⏱️ First request: ~20s (loading XTTS v2 engine)
- ⏱️ Subsequent requests: ~15-20s (cached engine)
- 📊 VRAM usage: ~6GB
- 🎵 Audio quality: Excellent

---

## 3. Sintetizar com StyleTTS2 (Fast)

```bash
# cURL
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Olá mundo, como você está?" \
  -F "language=pt" \
  -F "voice=default" \
  -F "engine=stylets2" \
  -F "speed=1.0" \
  -o output_stylets2.wav

# PowerShell
$form = @{
    text = "Olá mundo, como você está?"
    language = "pt"
    voice = "default"
    engine = "stylets2"
    speed = 1.0
}
$response = Invoke-WebRequest -Uri "http://localhost:5002/v1/synthesize" `
  -Method Post -Form $form -OutFile "output_stylets2.wav"

# Python
import requests
files = {
    'text': (None, 'Olá mundo, como você está?'),
    'language': (None, 'pt'),
    'voice': (None, 'default'),
    'engine': (None, 'stylets2'),
    'speed': (None, '1.0')
}
response = requests.post("http://localhost:5002/v1/synthesize", files=files)
with open('output_stylets2.wav', 'wb') as f:
    f.write(response.content)
```

### Expected Behavior:
- ⏱️ First request: ~10-15s (loading StyleTTS2 engine)
- ⏱️ Subsequent requests: ~5-7s (cached engine)
- 📊 VRAM usage: ~2GB
- 🎵 Audio quality: Excellent (near-human)
- ⚡ Speed advantage: 2-3x faster than XTTS v2

---

## 4. Comparação de Performance

```bash
#!/bin/bash
# Script para comparar performance entre engines

echo "=== Testing XTTS v2 ==="
time curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Este é um teste de performance com o motor XTTS v2" \
  -F "language=pt" \
  -F "voice=default" \
  -o test_xtts.wav

echo -e "\n=== Testing StyleTTS2 ==="
time curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Este é um teste de performance com o motor StyleTTS2" \
  -F "language=pt" \
  -F "voice=default" \
  -F "engine=stylets2" \
  -o test_stylets2.wav
```

### Expected Results:
```
XTTS v2:
real    0m20.234s
user    0m0.500s
sys     0m0.300s

StyleTTS2 (primeiro):
real    0m15.123s
user    0m0.400s
sys     0m0.250s

StyleTTS2 (segundo, cached):
real    0m6.789s
user    0m0.200s
sys     0m0.150s
```

---

## 5. Teste com Parâmetros Avançados

```bash
# Síntese rápida com StyleTTS2
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Teste rápido com StyleTTS2" \
  -F "language=pt" \
  -F "voice=default" \
  -F "engine=stylets2" \
  -F "speed=1.3" \
  -F "temperature=0.85" \
  -F "top_k=70" \
  -F "top_p=0.9" \
  -o output_fast.wav

# Síntese natural com XTTS v2
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Teste natural com XTTS v2" \
  -F "language=pt" \
  -F "voice=default" \
  -F "engine=xtts-v2" \
  -F "speed=1.0" \
  -F "temperature=0.75" \
  -F "top_k=50" \
  -F "top_p=0.85" \
  -o output_natural.wav
```

---

## 6. Tratamento de Erros

```bash
# Teste com engine inválido
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Teste" \
  -F "language=pt" \
  -F "voice=default" \
  -F "engine=invalid_engine"

# Expected Response (500 error):
# {"detail": "Synthesis failed: Unknown engine: invalid_engine. Available: ['xtts-v2', 'stylets2']"}

# Teste com idioma não suportado
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=Test" \
  -F "language=klingon" \
  -F "voice=default" \
  -F "engine=stylets2"

# Expected Response (400 error):
# {"detail": "Language 'klingon' not supported"}

# Teste com texto vazio
curl -X POST http://localhost:5002/v1/synthesize \
  -F "text=" \
  -F "language=pt" \
  -F "voice=default"

# Expected Response (400 error):
# {"detail": "Text cannot be empty"}
```

---

## 7. Teste em Python (Simples)

```python
import requests
from pathlib import Path

def test_tts_engine(engine_name, text, output_file):
    """Testa síntese TTS com engine especificado"""
    
    url = "http://localhost:5002/v1/synthesize"
    
    data = {
        'text': (None, text),
        'language': (None, 'pt'),
        'voice': (None, 'default'),
        'engine': (None, engine_name),
        'speed': (None, '1.0')
    }
    
    print(f"🎤 Testando {engine_name}...")
    response = requests.post(url, files=data)
    
    if response.status_code == 200:
        Path(output_file).write_bytes(response.content)
        print(f"✅ Síntese bem-sucedida: {output_file}")
        return True
    else:
        print(f"❌ Erro ({response.status_code}): {response.text}")
        return False

# Teste
if __name__ == "__main__":
    text = "Olá mundo, testando síntese de fala com múltiplos engines"
    
    test_tts_engine("xtts-v2", text, "output_xtts.wav")
    test_tts_engine("stylets2", text, "output_stylets2.wav")
    
    print("\n✨ Testes concluídos!")
```

---

## 8. Teste Completo de Integração

```python
import requests
import json
import time

def integration_test():
    """Teste completo da integração multi-engine"""
    
    base_url = "http://localhost:5002"
    
    # 1. Verificar engines disponíveis
    print("1️⃣ Verificando engines disponíveis...")
    response = requests.get(f"{base_url}/v1/engines")
    engines = response.json()
    print(f"   Available engines: {engines['available']}")
    print(f"   Current engine: {engines['current']}")
    assert len(engines['available']) >= 2, "Ao menos 2 engines esperados"
    
    # 2. Testar síntese com XTTS v2
    print("\n2️⃣ Testando síntese com XTTS v2...")
    start = time.time()
    response = requests.post(
        f"{base_url}/v1/synthesize",
        files={
            'text': (None, 'Teste com XTTS v2'),
            'language': (None, 'pt'),
            'voice': (None, 'default'),
            'engine': (None, 'xtts-v2')
        }
    )
    elapsed = time.time() - start
    assert response.status_code == 200, f"Status code: {response.status_code}"
    print(f"   ✅ Síntese sucesso em {elapsed:.1f}s")
    print(f"   Audio size: {len(response.content)} bytes")
    
    # 3. Testar síntese com StyleTTS2
    print("\n3️⃣ Testando síntese com StyleTTS2...")
    start = time.time()
    response = requests.post(
        f"{base_url}/v1/synthesize",
        files={
            'text': (None, 'Teste com StyleTTS2'),
            'language': (None, 'pt'),
            'voice': (None, 'default'),
            'engine': (None, 'stylets2')
        }
    )
    elapsed = time.time() - start
    assert response.status_code == 200, f"Status code: {response.status_code}"
    print(f"   ✅ Síntese sucesso em {elapsed:.1f}s")
    print(f"   Audio size: {len(response.content)} bytes")
    
    # 4. Testar engine inválido
    print("\n4️⃣ Testando tratamento de erro (engine inválido)...")
    response = requests.post(
        f"{base_url}/v1/synthesize",
        files={
            'text': (None, 'Test'),
            'language': (None, 'pt'),
            'voice': (None, 'default'),
            'engine': (None, 'invalid_engine')
        }
    )
    assert response.status_code == 500, "Esperava erro 500"
    print(f"   ✅ Erro tratado corretamente")
    
    print("\n✨ Todos os testes passaram!")

if __name__ == "__main__":
    integration_test()
```

---

## 🎯 Checklist de Verificação

Para verificar se a integração está funcionando:

- [ ] GET /v1/engines retorna 2 engines disponíveis
- [ ] POST /v1/synthesize com engine=xtts-v2 sintetiza com sucesso
- [ ] POST /v1/synthesize com engine=stylets2 sintetiza com sucesso
- [ ] POST /v1/synthesize sem engine usa default (xtts-v2)
- [ ] POST /v1/synthesize com engine inválido retorna erro 500
- [ ] XTTS v2 leva ~15-20s (primeira execução pode levar mais)
- [ ] StyleTTS2 leva ~5-7s (primeira execução pode levar mais)
- [ ] Engines subsequentes são mais rápidas (caching funciona)
- [ ] Audio files são válidos WAV e reproduzem corretamente
- [ ] Nenhum erro de sintaxe em main.py

---

## 📊 Métricas de Performance Esperadas

| Métrica | XTTS v2 | StyleTTS2 |
|---------|---------|----------|
| **Tempo (primeira)** | ~20-25s | ~10-15s |
| **Tempo (cached)** | ~15-20s | ~5-7s |
| **VRAM** | ~6GB | ~2GB |
| **Qualidade** | Excelente | Excelente |
| **Idiomas** | 16 | 11 (incl. PT-BR) |
| **Velocidade** | Baseline | 2-3x mais rápido |

---

## 🔧 Troubleshooting

### Erro: "Cannot find module 'engines'"
**Solução:** Certifique-se de que está no diretório `xtts-server/`

### Erro: "Unknown engine: stylets2"
**Solução:** StyleTTS2 pode não estar instalado. Verifique:
```bash
pip list | grep styletts2
pip install styletts2==0.1.6
```

### Erro: CUDA out of memory
**Solução:** Isso é esperado na primeira síntese. A engine carrega o modelo na GPU.

### Síntese muito lenta
**Solução:** Primeira execução de cada engine é lenta (carregamento). Prox execuções serão mais rápidas devido ao caching.

---

## 📝 Notas

1. **Lazy Loading:** Engines só são carregadas quando solicitadas
2. **Caching:** Engines são mantidas em memória entre requisições
3. **Backward Compatible:** Requests sem `engine` param usam XTTS v2 (default)
4. **Error Handling:** Erros são tratados gracefully com mensagens claras

---

**Status:** ✅ Pronto para testes  
**Próximo:** Implementar UI frontend para seleção de engine
