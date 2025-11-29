## 🎙️ Guia de Teste - Phase 4.1: Frontend Engine Selector

### ✅ Checklist de Funcionalidades

#### 1. **Engine Selector Visual**
- [ ] Abrir `web_ui.html` no navegador
- [ ] Na aba "Síntese", procurar pelo label "🎤 Motor TTS:"
- [ ] Verificar se há dropdown com 2 opções:
  - [ ] ⭐ XTTS v2 (Padrão - Alta Qualidade)
  - [ ] ⚡ StyleTTS2 (Rápido - 2-3x Mais Veloz)

#### 2. **Descrição Dinâmica**
- [ ] Selecionar "XTTS v2" e verificar descrição:
  - "⭐ XTTS v2: Máxima qualidade de voz, suporta 16 idiomas..."
- [ ] Selecionar "StyleTTS2" e verificar descrição:
  - "⚡ StyleTTS2: Síntese 2-3x mais rápida, qualidade próxima ao humano..."
- [ ] Verificar que descrição muda dinamicamente

#### 3. **Status Indicator**
- [ ] Verificar se existe div `#engine-status` com display block
- [ ] Verificar que mostra status do engine selecionado
- [ ] Exemplos esperados:
  - "⭐ XTTS v2 (Alta Qualidade)"
  - "⚡ StyleTTS2 (Rápido)"

#### 4. **localStorage Persistence**
- [ ] Com browser DevTools (F12):
  - [ ] Ir para aba "Application" > "Local Storage"
  - [ ] Procurar por chave: `speakerbot_tts_engine`
  - [ ] Verificar valor após mudar seleção
- [ ] Fechar e reabrir página
- [ ] Verificar que seleção anterior foi restaurada

#### 5. **Synthesize Function**
- [ ] Na aba "Síntese":
  - [ ] Selecionar engine (XTTS v2 ou StyleTTS2)
  - [ ] Digitar texto em português
  - [ ] Clicar em "Sintetizar"
  - [ ] Verificar mensagem de status: "Sintetizando com [engine]..."
  - [ ] Ouvir áudio gerado
  
**Esperado:**
- Síntese com XTTS v2 mais lenta (~15-20s) mas qualidade superior
- Síntese com StyleTTS2 mais rápida (~5-7s) mas qualidade comparável

#### 6. **Clone Voice Function**
- [ ] Na aba "Clonar Voz":
  - [ ] Selecionar engine (notará que usa a mesma seleção da síntese)
  - [ ] Fazer upload de arquivo(s) WAV
  - [ ] Digitar texto
  - [ ] Clicar em "Clonar Voz e Sintetizar"
  - [ ] Verificar mensagem: "Clonando voz com [engine]..."

#### 7. **Browser Console (F12)**
Verificar que há mensagens de log:
```
✅ Engine selection restored from localStorage: xtts-v2
```

Após mudar engine:
```
✅ Engine selection saved to localStorage: stylets2
```

### 🔧 Testes Manuais com cURL

#### Teste 1: Verificar Engines Disponíveis
```bash
curl http://localhost:8000/v1/engines
```

**Resposta esperada:**
```json
{
  "engines": {
    "xtts-v2": {...},
    "stylets2": {...}
  }
}
```

#### Teste 2: Síntese com XTTS v2
```bash
curl -X POST http://localhost:8000/v1/synthesize \
  -F "text=Olá, mundo!" \
  -F "language=pt" \
  -F "voice=Joana" \
  -F "engine=xtts-v2" \
  -F "speed=1.0" \
  -F "temperature=0.75" \
  -F "top_k=50" \
  -F "top_p=0.85" \
  -F "length_scale=1.0" \
  -F "gpt_cond_len=30.0" \
  --output audio_xtts.wav
```

#### Teste 3: Síntese com StyleTTS2
```bash
curl -X POST http://localhost:8000/v1/synthesize \
  -F "text=Olá, mundo!" \
  -F "language=pt" \
  -F "voice=Joana" \
  -F "engine=stylets2" \
  -F "speed=1.0" \
  -F "temperature=0.75" \
  -F "top_k=50" \
  -F "top_p=0.85" \
  -F "length_scale=1.0" \
  -F "gpt_cond_len=30.0" \
  --output audio_stylets2.wav
```

#### Teste 4: Engine Inválido (deve retornar erro)
```bash
curl -X POST http://localhost:8000/v1/synthesize \
  -F "text=Teste" \
  -F "language=pt" \
  -F "voice=Joana" \
  -F "engine=invalid-engine" \
  --output audio.wav
```

### 🐍 Script de Teste Python

Execute o script criado:
```bash
python test_frontend_engine.py
```

Este script testa:
1. ✅ /v1/engines endpoint
2. ✅ Síntese com XTTS v2
3. ✅ Síntese com StyleTTS2

### 📊 Teste de Performance

Para comparar performance entre engines:
```bash
# XTTS v2
time curl -X POST http://localhost:8000/v1/synthesize \
  -F "text=Este é um teste de performance com o motor XTTS v2" \
  -F "language=pt" \
  -F "voice=Joana" \
  -F "engine=xtts-v2" \
  -F "speed=1.0" \
  -F "temperature=0.75" \
  -F "top_k=50" \
  -F "top_p=0.85" \
  -F "length_scale=1.0" \
  -F "gpt_cond_len=30.0" \
  --output /dev/null

# StyleTTS2
time curl -X POST http://localhost:8000/v1/synthesize \
  -F "text=Este é um teste de performance com o motor StyleTTS2" \
  -F "language=pt" \
  -F "voice=Joana" \
  -F "engine=stylets2" \
  -F "speed=1.0" \
  -F "temperature=0.75" \
  -F "top_k=50" \
  -F "top_p=0.85" \
  -F "length_scale=1.0" \
  -F "gpt_cond_len=30.0" \
  --output /dev/null
```

### 🎯 Critérios de Aceitação

- ✅ Engine selector aparece na UI
- ✅ Ambos engines (XTTS v2 e StyleTTS2) podem ser selecionados
- ✅ Descrição muda dinamicamente com seleção
- ✅ Síntese usa o engine selecionado
- ✅ Clone voice usa o engine selecionado
- ✅ Seleção é persistida no localStorage
- ✅ Seleção é restaurada ao recarregar página
- ✅ Browser console mostra logs de save/load
- ✅ API /v1/engines retorna ambos engines
- ✅ Síntese com ambos engines produz áudio válido

### 📝 Problemas Conhecidos e Soluções

| Problema | Solução |
|----------|---------|
| Engine não aparece no dropdown | Verificar que `#tts-engine` existe em web_ui.html |
| Descrição não atualiza | Abrir DevTools e verificar se setupEngineDescriptionListener() foi chamado |
| localStorage não persiste | Verificar que localStorage está habilitado no navegador (não modo privado) |
| Síntese falha com 500 | Verificar que main.py foi reiniciado após mudanças |
| Síntese lenta | Normal para XTTS v2 (15-20s), StyleTTS2 deve ser mais rápido |

### 🚀 Próximos Passos

Após validar tudo acima:

1. **Phase 4.2:** Executar `test_frontend_engine.py` completo
2. **Phase 4.3:** Testes de integração com pytest
3. **Phase 5:** Documentação final e benchmarking de performance

---

**Última Atualização:** 29 de Novembro, 2025
**Status:** ✅ Pronto para Testes
