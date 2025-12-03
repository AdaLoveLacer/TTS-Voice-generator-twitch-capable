## 🚀 PHASE 4.2 - Test Frontend Engine Switching

**Objetivo:** Validar que o sistema multi-engine funciona corretamente em produção (Phase 4.2)

---

## CHECKLIST DE TESTES - PHASE 4.2

### PRÉ-TESTE: Setup
- [ ] Verificar se StyleTTS2 está instalado em requirements.txt
- [ ] Verificar se o .env tem GPU/CUDA configurado
- [ ] Limpar cache de modelos se necessário

### TESTE 1: Server Startup
- [ ] Executar: `cd xtts-server && python main.py`
- [ ] Verificar log inicial que mostra engines disponíveis
- [ ] Confirmar que nenhum erro ocorre durante startup
- [ ] Verificar: "Available engines: xtts-v2, stylets2"

### TESTE 2: GET /v1/engines Endpoint
- [ ] Abrir: http://localhost:8000/v1/engines
- [ ] Verificar resposta JSON:
  ```json
  {
    "engines": [
      {
        "name": "xtts-v2",
        "status": "loaded" ou "ready",
        "description": "..."
      },
      {
        "name": "stylets2",
        "status": "loaded" ou "ready",
        "description": "..."
      }
    ]
  }
  ```

### TESTE 3: Frontend UI - Engine Selector
- [ ] Abrir: http://localhost:8000
- [ ] Verificar que dropdown "Engine Selector" aparece na aba "Synthesize"
- [ ] Verificar que tem duas opções: "xtts-v2" e "stylets2"
- [ ] Verificar descrição dinâmica abaixo do dropdown
- [ ] Clicar no dropdown e trocar entre engines
- [ ] Verificar que descrição atualiza dinamicamente

### TESTE 4: Synthesis com XTTS v2 (Default)
**Setup:**
- [ ] Dropdown deve estar em "xtts-v2"
- [ ] Preencher formulário normalmente:
  - Voice: selecionar uma voz
  - Language: português
  - Text: "Olá, este é um teste de síntese de voz com XTTS"
  
**Execução:**
- [ ] Clicar "Synthesize"
- [ ] Verificar feedback no console: "Synthesizing with engine: xtts-v2"
- [ ] Esperar processamento (15-20 segundos esperado)
- [ ] Audio deve ser gerado e playable
- [ ] Som deve ser natural e de qualidade alta

**Validação:**
- [ ] Audio plays sem erros
- [ ] Qualidade de voz é boa
- [ ] Sem artefatos audíveis
- [ ] Duração é apropriada

### TESTE 5: Synthesis com StyleTTS2 (Fast)
**Setup:**
- [ ] Trocar dropdown para "stylets2"
- [ ] Verificar descrição atualiza: "Fast TTS engine..."
- [ ] Mesmo formulário anterior:
  - Voice: mesma voz do teste anterior
  - Language: português
  - Text: "Olá, este é um teste de síntese de voz com StyleTTS2"

**Execução:**
- [ ] Clicar "Synthesize"
- [ ] Verificar feedback: "Synthesizing with engine: stylets2"
- [ ] Esperar processamento (5-7 segundos esperado - mais rápido!)
- [ ] Audio deve ser gerado e playable
- [ ] Som deve ser mais rápido/natural que XTTS

**Validação:**
- [ ] Audio plays sem erros
- [ ] Tempo de síntese ~3x mais rápido
- [ ] Qualidade acceptable (pode ser ligeiramente diferente)
- [ ] Sem travamentos ou crashes

### TESTE 6: Comparison XTTS v2 vs StyleTTS2
**Métricas a registrar:**
```
XTTS v2:
- Engine: xtts-v2
- Tempo de síntese: ___ segundos
- Uso de GPU: ___ MB
- Qualidade de voz: (1-10) ___
- Naturalidade: (1-10) ___

StyleTTS2:
- Engine: stylets2
- Tempo de síntese: ___ segundos
- Uso de GPU: ___ MB
- Qualidade de voz: (1-10) ___
- Naturalidade: (1-10) ___
```

**Esperado:**
- [ ] StyleTTS2 é ~3x mais rápido
- [ ] XTTS v2 tem qualidade ligeiramente superior
- [ ] Ambos aceitáveis para produção

### TESTE 7: localStorage Persistence
**Procedure:**
- [ ] Deixar engine em "stylets2"
- [ ] Fazer uma síntese com sucesso
- [ ] Fechar completamente o navegador (Ctrl+W)
- [ ] Reabrir: http://localhost:8000
- [ ] Verificar que dropdown está em "stylets2" (localStorage restaurado)
- [ ] Repetir com "xtts-v2"
- [ ] Verificar que volta para "xtts-v2"

**Validação:**
- [ ] localStorage funciona corretamente
- [ ] Preferência do usuário persiste
- [ ] Engine padrão não é "resetado" ao recarregar

### TESTE 8: Clone Voice com ambos engines
**XTTS v2:**
- [ ] Dropdown: "xtts-v2"
- [ ] Carregar arquivo de áudio (voz para clonar)
- [ ] Clicar "Create Voice Clone"
- [ ] Verificar sucesso
- [ ] Testar nova voz criada em síntese

**StyleTTS2:**
- [ ] Repetir mesmo processo com "stylets2"
- [ ] Comparar qualidade do clone entre engines

### TESTE 9: Monitor-Based Synthesis com Engines
**Setup:**
- [ ] POST /v1/monitor/select-engine com payload:
  ```json
  {"engine": "stylets2"}
  ```
- [ ] Criar arquivo de monitoramento
- [ ] Verificar que synthesis usa "stylets2"

**Validação:**
- [ ] Engine selection persiste para monitor operations
- [ ] Arquivo processado com engine correto

### TESTE 10: Error Handling
**Test invalid engine:**
- [ ] POST /v1/synthesize com engine="invalid"
- [ ] Esperado: HTTP 400 ou 404 com mensagem de erro
- [ ] Server não deve crash

**Test missing engine:**
- [ ] POST /v1/synthesize com engine="" (vazio)
- [ ] Esperado: Usa DEFAULT_ENGINE ("xtts-v2")

**Test null engine:**
- [ ] POST /v1/synthesize sem engine parameter
- [ ] Esperado: Usa DEFAULT_ENGINE ("xtts-v2")

---

## CONSOLE LOGS ESPERADOS

**Ao iniciar server:**
```
[INFO] Initializing TTS engines...
[INFO] Available engines: ['xtts-v2', 'stylets2']
[INFO] Default engine: xtts-v2
[INFO] Server started on port 8000
```

**Ao fazer síntese com XTTS:**
```
[INFO] Synthesis request received: engine=xtts-v2
[INFO] Loading engine: xtts-v2
[INFO] XTTS v2 synthesizing text: "Olá..."
[INFO] Audio generation completed in X.XX seconds
```

**Ao fazer síntese com StyleTTS2:**
```
[INFO] Synthesis request received: engine=stylets2
[INFO] Loading engine: stylets2
[INFO] StyleTTS2 synthesizing text: "Olá..."
[INFO] Audio generation completed in X.XX seconds
```

---

## DEBUGGING - Se algo der errado

### Problema: StyleTTS2 não carrega
**Solução:**
```powershell
# Verificar instalação
pip show styletts2

# Se não tiver:
pip install styletts2

# Tentar importar:
python -c "from StyleTTS2 import tts; print('OK')"
```

### Problema: Erro "Unknown engine: stylets2"
**Possíveis causas:**
- StyleTTS2 not installed
- Import statement error em main.py
- Typo em engine name

**Solução:**
```python
# Verificar em main.py que está:
from engines.xttts_engine import XTTSEngine
from engines.stylets2_engine import StyleTTS2Engine

ENGINES = {
    "xtts-v2": XTTSEngine,
    "stylets2": StyleTTS2Engine,
}
```

### Problema: Frontend não mostra engine selector
**Solução:**
- [ ] Verificar que web_ui.html tem elemento com id="engine-selector"
- [ ] Verificar que CSS não está escondendo elemento
- [ ] Abrir DevTools (F12) → Console, procurar por erros

### Problema: localStorage não persiste
**Solução:**
```javascript
// No console do navegador (F12):
localStorage.getItem('speakerbot_tts_engine')
// Deve retornar: "xtts-v2" ou "stylets2"

// Se vazio, force:
localStorage.setItem('speakerbot_tts_engine', 'xtts-v2')
```

### Problema: Audio não toca
**Causas possíveis:**
- Navegador silenciado
- Problema de codec
- Diretório de saída errado

**Solução:**
- [ ] Verificar que audio file foi criado em /voices/output/
- [ ] Verificar tamanho do arquivo (não pode ser 0 bytes)
- [ ] Tentar abrir arquivo diretamente no player

---

## RESULTADOS ESPERADOS (Sucesso)

✅ **Server startup:** Sem erros, engines carregadas
✅ **GET /v1/engines:** Retorna ambos engines disponíveis
✅ **UI selector:** Dropdown funciona e atualiza descrição
✅ **XTTS v2 synthesis:** Audio gerado em 15-20 segundos
✅ **StyleTTS2 synthesis:** Audio gerado em 5-7 segundos (~3x mais rápido)
✅ **localStorage:** Engine choice persiste após recarregar
✅ **Error handling:** Invalid engines rejeitados com mensagem clara
✅ **Monitor mode:** Engines funcionam também em monitor-based synthesis

---

## MÉTRICAS A REGISTRAR

| Métrica | XTTS v2 | StyleTTS2 | Esperado |
|---------|---------|-----------|----------|
| Tempo de síntese | ___ s | ___ s | XTTS: 15-20s, StyleTTS2: 5-7s |
| Memória GPU | ___ MB | ___ MB | XTTS: ~6GB, StyleTTS2: ~2GB |
| Qualidade de voz | __/10 | __/10 | XTTS: 9-10, StyleTTS2: 7-9 |
| Naturalidade | __/10 | __/10 | Ambos: 8+ |
| Erro rate | ___ % | ___ % | Ambos: < 1% |

---

## PRÓXIMOS PASSOS (se tudo passar)

✅ **Phase 4.2 Complete:** Todos os testes passaram
↓
🟡 **Phase 4.3:** UI Polish
- Adicionar indicador visual de engine selecionado
- Loading states mais claros
- Performance metrics display
↓
📋 **Phase 5:** Final Testing & Docs
- Integration tests automatizados
- Performance benchmarks
- Documentação final

---

## TEMPO ESTIMADO

- **Setup & Pre-teste:** 10 minutos
- **Testes 1-3:** 15 minutos
- **Testes 4-5:** 40 minutos (incluindo tempo de síntese)
- **Testes 6-8:** 30 minutos
- **Testes 9-10:** 20 minutos
- **Debugging (se necessário):** 15-30 minutos

**Total esperado:** 2-3 horas

---

**Status:** Pronto para Phase 4.2
**Última atualização:** Sessão 3 (atual)
**Próximo passo:** Execute os testes acima e registre os resultados
