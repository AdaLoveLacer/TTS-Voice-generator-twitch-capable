# ✅ Todo List - StyleTTS2 Implementation (Fase 1)

**Status**: 📋 Pronto para Iniciar  
**Prioridade**: 🥇 Primeira (Próxima)  
**Tempo Estimado**: 6-9 horas  
**Data de Início**: 29 de Novembro de 2025

---

## 🎯 Objetivo

Implementar StyleTTS2 como engine alternativo ao XTTS v2, com:
- ✅ Suporte completo a PT-BR
- ✅ 2-3x mais rápido que XTTS v2
- ✅ Menor consumo de GPU (2GB)
- ✅ Alternância via UI sem downtime
- ✅ Monitor de arquivo integrado

---

## 📋 Fase 1: Backend Setup

### 1. Criar Estrutura de Engines
- [ ] **1.1** Criar pasta `/xtts-server/engines/`
- [ ] **1.2** Criar `engines/__init__.py` (vazio)
- [ ] **1.3** Criar `engines/base_engine.py` (interface abstrata)
  - [ ] Classe `BaseTTSEngine` com ABC
  - [ ] Métodos abstratos: `load_model()`, `synthesize()`, `get_languages()`, `get_voices()`
  - [ ] Tipo de retorno padronizado
- [ ] **1.4** Refatorar `main.py` atual para `engines/xtts_engine.py`
  - [ ] Extrair classe `XTTSEngine` herdando de `BaseTTSEngine`
  - [ ] Manter compatibilidade com código existente
  - [ ] Testar que XTTS continua funcionando

**Estimado**: 1-1.5 horas

---

### 2. Implementar StyleTTS2 Engine
- [ ] **2.1** Instalar StyleTTS2
  ```bash
  pip install styletts2
  ```
- [ ] **2.2** Criar `engines/stylets2_engine.py`
  - [ ] Classe `StyleTTS2Engine` herdando de `BaseTTSEngine`
  - [ ] Implementar `load_model()`
    - [ ] Carregar modelo PT-BR
    - [ ] Gerenciar GPU/CPU
    - [ ] Cache de modelos
  - [ ] Implementar `synthesize(text, language, voice, **kwargs)`
    - [ ] Conversão de texto para áudio
    - [ ] Suporte a PT-BR e PT-PT
    - [ ] Handling de erros
  - [ ] Implementar `get_available_languages()`
    - [ ] Retornar `["pt", "pt-BR", "pt-PT", "en", ...]`
  - [ ] Implementar `get_available_voices()`
    - [ ] Vozes pré-configuradas PT-BR
- [ ] **2.3** Criar arquivo `config/stylets2_config.json`
  ```json
  {
    "model_name": "styletts2-default",
    "device": "cuda",
    "default_language": "pt",
    "supported_languages": ["pt", "pt-BR", "pt-PT", "en", "es", "fr"],
    "voices": {
      "default": "pt_br_default",
      "female": "pt_br_female",
      "male": "pt_br_male"
    }
  }
  ```
- [ ] **2.4** Testes básicos de StyleTTS2
  - [ ] Teste de carregamento de modelo
  - [ ] Teste de síntese PT-BR (texto simples)
  - [ ] Teste de síntese PT-PT
  - [ ] Verificar velocidade vs XTTS

**Estimado**: 2-2.5 horas

---

### 3. Integração ao main.py
- [ ] **3.1** Criar registrador de engines
  ```python
  AVAILABLE_ENGINES = {
      "xtts-v2": XTTSEngine,
      "stylets2": StyleTTS2Engine,
  }
  ```
- [ ] **3.2** Refatorar rota `/v1/synthesize`
  - [ ] Adicionar parâmetro `engine` (default: "xtts-v2")
  - [ ] Selecionar engine baseado no parâmetro
  - [ ] Manter compatibilidade com requisições antigas
- [ ] **3.3** Criar nova rota `/v1/engines`
  - [ ] Retornar lista de engines disponíveis
  - [ ] Metadados de cada engine
  ```json
  {
    "engines": [
      {
        "name": "xtts-v2",
        "label": "XTTS v2 (Premium)",
        "speed": "medium",
        "quality": "excellent",
        "gpu_vram": "6GB",
        "languages": 16
      },
      {
        "name": "stylets2",
        "label": "StyleTTS2 (Rápido)",
        "speed": "fast",
        "quality": "excellent",
        "gpu_vram": "2GB",
        "languages": 10
      }
    ]
  }
  ```
- [ ] **3.4** Adicionar suporte a monitor com múltiplos engines
  - [ ] Rota `/v1/monitor/start` com parâmetro `engine`
  - [ ] Rota `/v1/monitor/stop`
- [ ] **3.5** Testes de integração
  - [ ] Teste de alternância XTTS → StyleTTS2
  - [ ] Teste de múltiplas requisições
  - [ ] Teste de erro handling

**Estimado**: 1.5-2 horas

---

### 4. Arquivos de Instalação
- [ ] **4.1** Criar `requirements-stylets2.txt`
  ```
  styletts2==0.x.x
  torch>=2.0
  torchaudio>=2.0
  ```
- [ ] **4.2** Criar `install-stylets2.bat` (Windows)
  ```batch
  @echo off
  pip install -r requirements-stylets2.txt
  echo StyleTTS2 installed!
  ```
- [ ] **4.3** Criar `install-stylets2.sh` (Linux/macOS)
  ```bash
  #!/bin/bash
  pip install -r requirements-stylets2.txt
  echo "StyleTTS2 installed!"
  ```
- [ ] **4.4** Atualizar `requirements.txt` (dependências comuns)

**Estimado**: 0.5 horas

---

## 📺 Fase 2: Frontend Implementation

### 5. Criar Estrutura de Abas
- [ ] **5.1** Adicionar CSS para abas de engines
  - [ ] Estilo `.engine-tabs`
  - [ ] Estilo `.tab-button`
  - [ ] Estilo `.engine-content`
  - [ ] Estilo `.active` para aba ativa
- [ ] **5.2** Criar HTML para abas
  ```html
  <div class="engine-selector">
    <div class="engine-tabs">
      <button class="tab-button active" 
              onclick="switchEngine('xtts-v2', event)">
        <span class="label">XTTS v2</span>
        <span class="badge">Premium</span>
      </button>
      <button class="tab-button" 
              onclick="switchEngine('stylets2', event)">
        <span class="label">StyleTTS2</span>
        <span class="badge">Rápido</span>
      </button>
    </div>
  </div>
  ```
- [ ] **5.3** Adicionar indicador do engine ativo
  - [ ] Mostrar qual engine está sendo usado
  - [ ] Mostrar velocidade esperada
  - [ ] Mostrar uso de GPU

**Estimado**: 1 hora

---

### 6. Duplicar Conteúdo para StyleTTS2
- [ ] **6.1** Copiar seção XTTS v2 para StyleTTS2
- [ ] **6.2** Adaptar IDs e funções para StyleTTS2
  - [ ] `stylets2-text-input` (vs `text-input`)
  - [ ] `stylets2-language-select` (vs `language-select`)
  - [ ] Callbacks separados para cada engine
- [ ] **6.3** Adicionar informações do engine
  - [ ] Velocidade esperada
  - [ ] Uso de GPU
  - [ ] Idiomas suportados
- [ ] **6.4** Garantir layout idêntico
  - [ ] Mesmos campos
  - [ ] Mesma organização
  - [ ] Mesmos botões

**Estimado**: 1-1.5 horas

---

### 7. Implementar Alternância de Engines
- [ ] **7.1** Criar função `switchEngine(engineName, event)`
  ```javascript
  let currentEngine = "xtts-v2";
  
  function switchEngine(engineName, event) {
    // Desativar aba anterior
    document.querySelectorAll(".tab-button").forEach(btn => 
      btn.classList.remove("active")
    );
    document.querySelectorAll(".engine-content").forEach(div => 
      div.classList.remove("active")
    );
    
    // Ativar nova aba
    event.target.closest(".tab-button").classList.add("active");
    document.getElementById(engineName).classList.add("active");
    currentEngine = engineName;
    
    // Atualizar info do engine
    updateEngineInfo(engineName);
    
    console.log(`Switched to engine: ${engineName}`);
  }
  ```
- [ ] **7.2** Implementar `updateEngineInfo(engineName)`
  - [ ] Fazer fetch para `/v1/engines`
  - [ ] Atualizar UI com metadados do engine
  - [ ] Mostrar velocidade, GPU, idiomas
- [ ] **7.3** Atualizar função de síntese
  ```javascript
  async function synthesize() {
    const text = document.getElementById(`${currentEngine}-text-input`).value;
    const language = document.getElementById(`${currentEngine}-language`).value;
    const response = await fetch("/v1/synthesize", {
      method: "POST",
      body: JSON.stringify({
        text: text,
        language: language,
        engine: currentEngine  // Novo parâmetro
      })
    });
    // Processar resposta...
  }
  ```
- [ ] **7.4** Testes de UI
  - [ ] Teste de alternância visual
  - [ ] Teste de síntese em cada engine
  - [ ] Teste de erro handling

**Estimado**: 1.5-2 horas

---

### 8. Integrar Monitor de Arquivo
- [ ] **8.1** Adicionar selector de engine no monitor
  ```html
  <div class="monitor-engine-selector">
    <label>Engine para Monitor:</label>
    <select id="monitor-engine">
      <option value="xtts-v2">XTTS v2</option>
      <option value="stylets2">StyleTTS2</option>
    </select>
  </div>
  ```
- [ ] **8.2** Atualizar função `startFileMonitoring()`
  - [ ] Adicionar parâmetro `engine`
  - [ ] Enviar para backend: `/v1/monitor/start`
- [ ] **8.3** Atualizar Service Worker
  - [ ] Receber `engine` parameter
  - [ ] Passar para requisições de síntese
- [ ] **8.4** Manter funcionalidade de fila
  - [ ] Fila continua funcionando
  - [ ] Mesmo engine para todo o monitor
  - [ ] Opção de mudar engine entre monitorações

**Estimado**: 1-1.5 horas

---

## 🧪 Fase 3: Testes & Validação

### 9. Testes Unitários
- [ ] **9.1** Teste de StyleTTS2Engine
  ```python
  def test_stylets2_load():
      engine = StyleTTS2Engine()
      assert engine.loaded == True
  
  def test_stylets2_synthesize_pt_br():
      engine = StyleTTS2Engine()
      audio, sr = engine.synthesize("Olá mundo", language="pt-BR")
      assert len(audio) > 0
      assert sr == 24000
  ```
- [ ] **9.2** Teste de alternância de engines
- [ ] **9.3** Teste de monitor com múltiplos engines
- [ ] **9.4** Teste de erro handling

**Estimado**: 1-1.5 horas

---

### 10. Testes Funcionais
- [ ] **10.1** Teste manual: Síntese com StyleTTS2
  - [ ] Texto simples PT-BR
  - [ ] Texto comprido
  - [ ] Caracteres especiais
- [ ] **10.2** Teste de velocidade
  - [ ] Comparar tempo: XTTS vs StyleTTS2
  - [ ] Registrar em log
- [ ] **10.3** Teste de qualidade de áudio
  - [ ] Ouvir saída em PT-BR
  - [ ] Comparar com XTTS v2
  - [ ] Verificar prosódia
- [ ] **10.4** Teste de alternância
  - [ ] Alternar XTTS → StyleTTS2
  - [ ] Alternar StyleTTS2 → XTTS
  - [ ] Nenhum erro
- [ ] **10.5** Teste de monitor
  - [ ] Monitorar com StyleTTS2
  - [ ] Fila funciona
  - [ ] Trocar engine durante monitor

**Estimado**: 1-1.5 horas

---

### 11. Otimizações & Bugfixes
- [ ] **11.1** Otimizar carregamento de modelos
  - [ ] Cache de modelos em disco
  - [ ] Lazy loading
- [ ] **11.2** Otimizar alternância
  - [ ] Unload do engine anterior?
  - [ ] Memory management
- [ ] **11.3** Fixes encontrados em testes
  - [ ] Problemas com alternância
  - [ ] Problemas com fila
  - [ ] Performance issues

**Estimado**: 0.5-1 hora

---

## 📚 Fase 4: Documentação

### 12. Documentação
- [ ] **12.1** Criar `docs/setup/STYLETS2_INSTALL.md`
  - [ ] Instruções de instalação
  - [ ] Requisitos de GPU
  - [ ] Troubleshooting
- [ ] **12.2** Criar `docs/API_MULTI_ENGINE.md`
  - [ ] Documentação de rotas
  - [ ] Exemplos de requisições
  - [ ] Responses
- [ ] **12.3** Atualizar `docs/INDEX.md`
  - [ ] Adicionar links para nova documentação
- [ ] **12.4** Atualizar `CHANGELOG.md`
  - [ ] Adicionar entry para StyleTTS2

**Estimado**: 0.5-1 hora

---

## 📊 Summary de Tarefas

| Fase | Descrição | Tarefas | Horas | Status |
|------|-----------|---------|-------|--------|
| 1 | Backend Setup | 4 | 5-6h | 📋 |
| 2 | Frontend | 4 | 4-6h | 📋 |
| 3 | Testes | 3 | 2-4h | 📋 |
| 4 | Documentação | 4 | 1-2h | 📋 |
| **TOTAL** | - | **15** | **12-18h** | **📋** |

---

## 🎯 Milestones

### Milestone 1: Backend Funcional (Horas 1-6)
- [ ] Estrutura de engines criada
- [ ] StyleTTS2Engine implementado
- [ ] Integrado ao main.py
- [ ] Testes básicos passando

### Milestone 2: Frontend Integrado (Horas 7-12)
- [ ] Abas funcionando
- [ ] Alternância sem erros
- [ ] Monitor integrado
- [ ] UI responsiva

### Milestone 3: Produção Pronto (Horas 13-18)
- [ ] Testes completos
- [ ] Documentação pronta
- [ ] Otimizações aplicadas
- [ ] Changelog atualizado

---

## 🚀 Começando

### Próximos Passos Imediatos

1. **Clonar este todo list**
2. **Marcar tarefas conforme completa**
3. **Iniciar com Fase 1 (Backend Setup)**
4. **Commitar frequentemente**

### Comando para Iniciar

```bash
cd g:\VSCODE\Speakerbot-local-voice\xtts-server
mkdir engines
touch engines/__init__.py
# Começar com 1.3: Criar base_engine.py
```

---

**Status Atual**: 🟡 Aguardando Início  
**Última Atualização**: 29 de Novembro de 2025  
**Responsável**: [Você]

---

Deseja iniciar a implementação? Marcar primeira tarefa como "em progresso"? ➡️ Comece com **1.1: Criar pasta engines/**
