# 🎯 Roadmap de Implementação - Multi-Engine TTS

**Data**: 29 de Novembro de 2025  
**Status**: 📋 Planejamento  
**Objetivo**: Adicionar StyleTTS2, Kokoro e VITS2 como engines alternativos ao XTTS v2

---

## 📊 Resumo Executivo

Implementar 3 engines TTS avançados e rápidos com suporte nativo a português, permitindo alternância na UI sem impedir funcionamento do XTTS v2.

| Engine | Velocidade | Qualidade PT | GPU | Prioridade | Status |
|--------|-----------|-------------|-----|-----------|--------|
| **XTTS v2** | Média | Excelente | 6GB | Atual | ✅ Ativo |
| **StyleTTS2** | Rápida (2-3x) | Excelente | 2GB | 🥇 1º | 📋 Planejado |
| **Kokoro** | Muito Rápida | Excelente | 1GB | 🥈 2º | 📋 Planejado |
| **VITS2** | Muito Rápida | Bom | 1GB | 🥉 3º | 📋 Planejado |

---

## 🎯 Fase 1: StyleTTS2 (1º Lugar)

### 📌 Características
- **Velocidade**: 2-3x mais rápido que XTTS v2
- **Qualidade**: Excelente em PT-BR e PT-PT
- **GPU**: Apenas 2GB (vs 6GB do XTTS)
- **Clonagem**: Suporta voice cloning com prosódia
- **Idiomas**: 10+ incluindo português

### ✅ Checklist de Implementação

#### Backend (FastAPI)
- [ ] Instalar StyleTTS2 (`pip install styletts2`)
- [ ] Criar `/engines/stylets2_engine.py`
  - [ ] Classe `StyleTTS2Engine` com métodos padrão
  - [ ] Suporte a PT-BR e PT-PT
  - [ ] Cache de modelos
  - [ ] Gerenciamento de GPU
- [ ] Criar arquivo de configuração `/config/stylets2_config.json`
- [ ] Integrar ao `main.py`
  - [ ] Adicionar rota `/v1/synthesize/stylets2`
  - [ ] Adicionar ao selector de engines
  - [ ] Suporte a múltiplas requisições
- [ ] Implementar voice cloning para StyleTTS2
- [ ] Testes básicos

#### Frontend (HTML/JS)
- [ ] Criar nova aba "StyleTTS2" na UI
- [ ] Copiar layout da aba XTTS v2
- [ ] Adicionar selector de engine
  - [ ] Dropdown: "XTTS v2" vs "StyleTTS2"
  - [ ] Mostrar diferenças (velocidade, GPU)
- [ ] Integração com monitor de arquivo
  - [ ] Opção de escolher engine para "Monitor"
  - [ ] Mesmo funcionamento que XTTS v2
- [ ] Botão de toggle entre engines
- [ ] Indicador visual do engine ativo

#### Configuração
- [ ] Arquivo `requirements-stylets2.txt`
- [ ] Script `install-stylets2.sh` (Linux/macOS)
- [ ] Script `install-stylets2.bat` (Windows)
- [ ] Documentação de instalação

#### Testes
- [ ] Teste de síntese básica PT-BR
- [ ] Teste de velocidade vs XTTS
- [ ] Teste de clonagem de voz
- [ ] Teste de monitor de arquivo
- [ ] Teste de alternância de engines

### 📁 Estrutura de Pastas
```
xtts-server/
├── engines/
│   ├── __init__.py
│   ├── base_engine.py      (interface comum)
│   ├── xtts_engine.py      (refatorado)
│   └── stylets2_engine.py  (novo)
├── config/
│   ├── xtts_config.json
│   └── stylets2_config.json (novo)
└── requirements-stylets2.txt (novo)
```

### ⏱️ Tempo Estimado
- Backend: 3-4 horas
- Frontend: 2-3 horas
- Testes: 1-2 horas
- **Total: 6-9 horas**

---

## 🎯 Fase 2: Kokoro (2º Lugar)

### 📌 Características
- **Velocidade**: Muito rápida (~0.5s por síntese)
- **Qualidade**: Excelente em PT-BR
- **GPU**: Apenas 1GB
- **Tamanho**: ~50MB (muito leve)
- **Idiomas**: 30+ incluindo português

### ✅ Checklist de Implementação

#### Backend
- [ ] Instalar Kokoro (`pip install kokoro-onnx`)
- [ ] Criar `/engines/kokoro_engine.py`
- [ ] Integrar ao `main.py`
- [ ] Criar arquivo de configuração

#### Frontend
- [ ] Adicionar aba "Kokoro"
- [ ] Integrar ao selector de engines
- [ ] Monitor de arquivo com Kokoro

#### Testes
- [ ] Teste de velocidade (~0.5s)
- [ ] Teste de qualidade PT-BR
- [ ] Teste de alternância

### ⏱️ Tempo Estimado
- Backend: 2-3 horas
- Frontend: 1-2 horas
- Testes: 1 hora
- **Total: 4-6 horas**

---

## 🎯 Fase 3: VITS2 (3º Lugar)

### 📌 Características
- **Velocidade**: Muito rápida (real-time)
- **Qualidade**: Bom (um pouco mais "sintético")
- **GPU**: 1GB
- **Customização**: Suporta fine-tuning para PT-BR
- **Idiomas**: Variável por modelo

### ✅ Checklist de Implementação

#### Backend
- [ ] Instalar VITS2 (`pip install vits`)
- [ ] Criar `/engines/vits2_engine.py`
- [ ] Integrar ao `main.py`
- [ ] Suporte a modelos PT-BR customizados

#### Frontend
- [ ] Adicionar aba "VITS2"
- [ ] Integrar ao selector
- [ ] Monitor de arquivo

#### Testes
- [ ] Teste de velocidade
- [ ] Teste de qualidade
- [ ] Teste de alternância

### ⏱️ Tempo Estimado
- Backend: 2-3 horas
- Frontend: 1-2 horas
- Testes: 1 hora
- **Total: 4-6 horas**

---

## 🏗️ Arquitetura de Multi-Engine

### Interface Abstrata (Base Class)

```python
# engines/base_engine.py

from abc import ABC, abstractmethod
from typing import Optional, Dict, List

class BaseTTSEngine(ABC):
    """Interface padrão para todos os engines TTS"""
    
    def __init__(self, device: str = "cuda"):
        self.device = device
        self.loaded = False
    
    @abstractmethod
    def load_model(self) -> None:
        """Carregar modelo"""
        pass
    
    @abstractmethod
    def synthesize(
        self,
        text: str,
        language: str = "pt",
        voice: str = "default",
        **kwargs
    ) -> tuple[bytes, int]:
        """Sintetizar áudio
        
        Returns:
            (audio_bytes, sample_rate)
        """
        pass
    
    @abstractmethod
    def get_available_languages(self) -> List[str]:
        """Retornar idiomas suportados"""
        pass
    
    @abstractmethod
    def get_available_voices(self) -> List[str]:
        """Retornar vozes disponíveis"""
        pass
```

### Registrador de Engines

```python
# main.py

from engines.xtts_engine import XTTSEngine
from engines.stylets2_engine import StyleTTS2Engine
# from engines.kokoro_engine import KokoroEngine
# from engines.vits2_engine import VITS2Engine

AVAILABLE_ENGINES = {
    "xtts-v2": XTTSEngine,
    "stylets2": StyleTTS2Engine,
    # "kokoro": KokoroEngine,
    # "vits2": VITS2Engine,
}

@app.post("/v1/synthesize")
async def synthesize(
    text: str,
    engine: str = "xtts-v2",
    language: str = "pt",
    voice: str = "default",
    speed: float = 1.0
):
    """Sintetizar com engine selecionado"""
    if engine not in AVAILABLE_ENGINES:
        raise HTTPException(status_code=400, detail=f"Engine {engine} not available")
    
    tts = AVAILABLE_ENGINES[engine]()
    audio_bytes, sr = await tts.synthesize(text, language, voice)
    return {"audio": audio_bytes, "sample_rate": sr}
```

---

## 🖥️ Interface Web - Multi-Engine

### Nova Estrutura de Abas

```html
<div class="engine-tabs">
  <button class="tab-button active" onclick="switchEngine('xtts-v2')">
    XTTS v2 (Premium)
  </button>
  <button class="tab-button" onclick="switchEngine('stylets2')">
    StyleTTS2 (Rápido)
  </button>
  <button class="tab-button" onclick="switchEngine('kokoro')">
    Kokoro (Ultra-Rápido)
  </button>
  <button class="tab-button" onclick="switchEngine('vits2')">
    VITS2 (Leve)
  </button>
</div>

<div id="xtts-v2" class="engine-content active">
  <!-- Conteúdo XTTS v2 -->
</div>

<div id="stylets2" class="engine-content">
  <!-- Conteúdo StyleTTS2 -->
</div>

<!-- ... outros engines ... -->
```

### JavaScript para Alternância

```javascript
let currentEngine = "xtts-v2";

function switchEngine(engineName) {
  // Esconder conteúdo anterior
  document.getElementById(currentEngine).classList.remove("active");
  document.querySelector(`[onclick="switchEngine('${currentEngine}')"]`)
    .classList.remove("active");
  
  // Mostrar novo conteúdo
  currentEngine = engineName;
  document.getElementById(engineName).classList.add("active");
  document.querySelector(`[onclick="switchEngine('${engineName}')"]`)
    .classList.add("active");
  
  // Atualizar configurações
  updateEngineSettings(engineName);
  
  // Log
  console.log(`Switched to engine: ${engineName}`);
}

function synthesizeWithCurrentEngine(text, language) {
  const payload = {
    text: text,
    language: language,
    engine: currentEngine,
    voice: document.getElementById("voice-select").value
  };
  
  fetch("/v1/synthesize", {
    method: "POST",
    body: JSON.stringify(payload),
    headers: { "Content-Type": "application/json" }
  })
  .then(response => response.json())
  .then(data => playAudio(data.audio, data.sample_rate));
}
```

---

## 📡 Integração com Monitor de Arquivo

### Funcionalidade Proposta

```python
@app.post("/v1/monitor/start")
async def start_file_monitoring(
    file_path: str,
    engine: str = "xtts-v2",  # Novo parâmetro
    language: str = "pt",
    voice: str = "default"
):
    """Iniciar monitor com engine específico"""
    monitor_config = {
        "file_path": file_path,
        "engine": engine,
        "language": language,
        "voice": voice
    }
    # Implementação...
```

### UI para Monitor Multi-Engine

```html
<div class="monitor-section">
  <h2>Monitor de Arquivo</h2>
  
  <select id="monitor-engine">
    <option value="xtts-v2">XTTS v2 (Premium)</option>
    <option value="stylets2">StyleTTS2 (Rápido)</option>
    <option value="kokoro">Kokoro (Ultra-Rápido)</option>
    <option value="vits2">VITS2 (Leve)</option>
  </select>
  
  <input type="file" id="monitor-file" accept=".txt">
  <button onclick="startMonitor()">Iniciar Monitor</button>
</div>
```

---

## 📊 Comparação de Performance Esperada

### Tempo de Síntese (texto de ~30 segundos em PT-BR)

| Engine | Tempo | GPU | CPU | RAM |
|--------|-------|-----|-----|-----|
| XTTS v2 | ~15-20s | 6GB | Médio | 8GB |
| StyleTTS2 | ~5-7s | 2GB | Baixo | 4GB |
| Kokoro | ~0.5s | 1GB | Muito Baixo | 2GB |
| VITS2 | ~2-3s | 1GB | Baixo | 2GB |

---

## 🚀 Prioridades de Implementação

### Immediate (Semana 1)
1. **StyleTTS2** - Melhor custo-benefício
   - Interface abstrata
   - Backend StyleTTS2
   - Frontend com abas
   - Testes básicos

### Short-term (Semana 2-3)
2. **Kokoro** - Alternativa ultra-rápida
3. **VITS2** - Alternativa leve

### Long-term
- Benchmarks automáticos
- Auto-selection por preferência
- Integração com OBS para cada engine
- Dashboard de uso (qual engine mais usado)

---

## 📝 Documentação a Criar

- [ ] `/docs/MULTI_ENGINE_GUIDE.md` - Como usar múltiplos engines
- [ ] `/docs/api/STYLETS2_API.md` - Documentação StyleTTS2
- [ ] `/docs/api/KOKORO_API.md` - Documentação Kokoro
- [ ] `/docs/api/VITS2_API.md` - Documentação VITS2
- [ ] `/docs/setup/STYLETS2_INSTALL.md` - Instalação
- [ ] Update `CHANGELOG.md`

---

## ✅ Testes Propostos

```bash
# Teste de carga multi-engine
pytest tests/test_multi_engine.py

# Teste de alternância
pytest tests/test_engine_switching.py

# Teste de monitor com cada engine
pytest tests/test_monitor_multi_engine.py

# Benchmark de performance
python scripts/benchmark_engines.py
```

---

## 🎯 Critério de Sucesso

- ✅ StyleTTS2 funcional e integrado
- ✅ UI permite alternância sem erros
- ✅ Monitor funciona com qualquer engine
- ✅ Velocidade: StyleTTS2 > XTTS v2 em português
- ✅ Qualidade: StyleTTS2 ≈ XTTS v2 em português
- ✅ Zero downtime ao alternar engines
- ✅ Documentação completa

---

**Próximo Passo**: Iniciar implementação de StyleTTS2 (Fase 1)

Criar todo-list para desenvolvimento? ➡️ [VER IMPLEMENTAÇÃO](./STYLETS2_IMPLEMENTATION_PLAN.md)
