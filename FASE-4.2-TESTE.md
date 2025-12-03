# 🚀 Fase 4.2 - Teste de Multi-Engine TTS com StyleTTS2

## Resumo das Mudanças

### 1. **Batch Script (`start-server.bat`) - Versão v4 com Logging**
- ✅ Adicionado suporte a logging detalhado (`install.log`)
- ✅ Etapa 2 agora instala `numpy==1.24.3` (pinned exato)
- ✅ Etapa 3 com `--no-build-isolation` para evitar build env conflicts
- ✅ Todos os comandos pip agora registram output no log
- ✅ Mensagens de erro indicam onde verificar (install.log)

### 2. **Monitor de Instalação (`install-monitor.ps1`)**
- ✅ Script PowerShell para análise de erros pós-install
- ✅ Detecta conflitos de versão (especialmente numpy)
- ✅ Lista versões instaladas
- ✅ Menu interativo para limpeza de cache

### 3. **Requirements.txt - Versão v2**
- ✅ `numpy==1.24.3` (exato, compatível com gruut<3.0.0)
- ✅ `styletts2==0.1.6` ativo (foi comentado antes)
- ✅ `gruut==2.2.3` (da dependência TTS)

---

## 🔧 Como Testar (Fase 4.2)

### Opção A: Teste Rápido com Cache Limpo (Recomendado)

```bash
# Terminal 1: Executar instalação com cache limpo e seleção automática
cd xtts-server
start-server.bat 2 1
# 2 = Instalação (skip cache purge)
# 1 = CUDA 11.8
```

**Tempo esperado:** 15-30 minutos (depende da internet)

### Opção B: Teste com Cache Purge (Se houve erro anterior)

```bash
cd xtts-server
start-server.bat 1 1
# 1 = Instalação + limpar cache
# 1 = CUDA 11.8
```

**Tempo esperado:** 30-45 minutos

### Opção C: Teste com Servidor Já Instalado

```bash
cd xtts-server
start-server.bat 3 1
# 3 = Skip instalação, ir direto pro servidor
# 1 = CUDA (ignorado nesta opção)
```

**Tempo esperado:** 5 segundos

---

## 📊 Monitoramento Durante a Instalação

### 1. **Acompanhar em Tempo Real**
```bash
# Em outro PowerShell, enquanto instalação roda:
Get-Content .\install.log -Tail 20 -Wait
```

### 2. **Verificar Versões Instaladas**
```bash
# Depois que instalação terminar:
powershell -NoProfile -ExecutionPolicy Bypass .\install-monitor.ps1
# Selecionar opção 2 (Verificar versões instaladas)
```

### 3. **Análise de Erros**
```bash
# Se houver erro:
Get-Content .\install.log | Select-String "ERROR|ERRO|numpy|gruut|Conflict"
```

---

## ✅ Checklist Pós-Instalação

Quando o servidor iniciar, verificar:

- [ ] Log mostra `[OK] Etapa 1 concluida`
- [ ] Log mostra `[OK] Etapa 2 concluida` (numpy==1.24.3)
- [ ] Log mostra `[OK] Etapa 3 concluida`
- [ ] Nenhuma mensagem de conflito de versão
- [ ] Servidor respondendo em http://localhost:8000
- [ ] API Docs acessível em http://localhost:8000/docs
- [ ] Nenhum erro ImportError para engines

### Verificar Motores Carregados

```bash
# Terminal com servidor rodando, pressione CTRL+C depois:
curl -s http://localhost:8000/v1/monitor/info | python -m json.tool
# Deve listar engines: xtts_v2, styletts2
```

### Testar Seleção de Motor

```bash
# Selecionar StyleTTS2
curl -X POST "http://localhost:8000/v1/monitor/select-engine?engine=styletts2"

# Verificar que foi selecionado
curl -s http://localhost:8000/v1/monitor/info | python -m json.tool
# current_engine deve ser "styletts2"
```

---

## 🐛 Troubleshooting

### Problema: "numpy 2.3.5 which is incompatible"

**Causa:** Pip instala numpy 2.x na build environment mesmo com restrição

**Solução:** Agora corrigido com:
- `numpy==1.24.3` (pinned exato)
- `--no-build-isolation` (Etapa 3)

**Se ainda falhar:**
```bash
# Limpar cache
rmdir /s /q ..\pip_cache ..\torch_cache ..\huggingface_cache
# Tentar novamente
start-server.bat 1 1
```

### Problema: "StyleTTS2 módulo não encontrado"

**Verificar instalação:**
```bash
.\venv\Scripts\python.exe -c "import styletts2; print(styletts2.__version__)"
```

**Se falhar, reinstalar:**
```bash
.\venv\Scripts\python.exe -m pip install --force-reinstall styletts2==0.1.6
```

### Problema: "Servidor não inicia / Timeout"

**Verificar logs:**
```bash
Get-Content .\install.log | tail -100
```

**Procurar por:**
- CUDA initialization errors
- Missing dependencies
- Port 8000 already in use

**Se porta está em uso:**
```bash
# Encontrar processo
netstat -ano | findstr :8000
# Matar processo (substituir PID)
taskkill /PID <PID> /F
```

---

## 📝 Variáveis de Ambiente Configuradas

Automaticamente setadas no batch:

```
PIP_CACHE_DIR = ..\pip_cache
TTS_HOME = ..\tts_cache
TORCH_HOME = ..\torch_cache
HF_HOME = ..\huggingface_cache
NUMBA_CACHE_DIR = ..\numba_cache
MPLCONFIGDIR = ..\matplotlib_cache
```

✅ Nenhuma poluição em `C:\` ou `%APPDATA%`

---

## 🎯 Próximas Etapas (Fase 4.2 Completa)

1. ✅ **Instalação:** Run `start-server.bat 2 1`
2. ✅ **Verificação:** Confirmar no console que `[OK] Todas as dependencias instaladas`
3. ✅ **Servidor:** Verificar http://localhost:8000 respondendo
4. ⏳ **Motores:** Testar seleção via API
5. ⏳ **Síntese:** Testar TTS com ambos os motores

---

## 📞 Se Algo Der Errado

1. **Capturar log:**
   ```bash
   Copy-Item .\install.log .\install-error.log
   ```

2. **Analisar com monitor:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass .\install-monitor.ps1
   ```

3. **Limpar tudo e recomeçar:**
   ```bash
   rmdir /s /q venv ..\pip_cache ..\torch_cache ..\huggingface_cache
   start-server.bat 1 1
   ```

---

## 🏁 Status Atual

- **Batch v4:** ✅ Com logging e --no-build-isolation
- **Requirements:** ✅ numpy==1.24.3 pinned
- **Monitor:** ✅ Script de análise criado
- **Teste:** ⏳ Aguardando execução do usuário

**Comando para iniciar:** `cd xtts-server && start-server.bat 2 1`
