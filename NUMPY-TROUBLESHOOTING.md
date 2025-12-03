# 🔧 Troubleshooting - Numpy Conflict (Fase 4.2)

## O Problema

```
ERROR: gruut 2.2.3 requires numpy<2.0.0,>=1.19.0
       but you have numpy 2.3.5 which is incompatible
```

## Por Que Acontece?

Pip cria um **build environment isolado** durante a compilação de pacotes Cython (como TTS).

Neste ambiente:
- Numpy é instalado para build (usa versão latest = 2.3.5)
- Gruut precisa de numpy < 2.0.0
- Conflito!

## ✅ Como Fix (Implementado)

### 1. **numpy==1.24.3 Pinned (Etapa 2)**

```batch
python -m pip install --upgrade -v --cache-dir "%PIP_CACHE_DIR%" 
  --default-timeout=300 "numpy==1.24.3" cython
```

**O quê faz:**
- Instala numpy 1.24.3 ANTES de qualquer package Cython
- Garante que build env use 1.24.3 (dentro do range <2.0.0)

### 2. **--no-build-isolation (Etapa 3)**

```batch
python -m pip install --upgrade -v --cache-dir "%PIP_CACHE_DIR%" 
  --default-timeout=300 --no-build-isolation -r requirements.txt --prefer-binary
```

**O quê faz:**
- Reutiliza numpy 1.24.3 do sistema
- NÃO cria build env isolado
- Previne pip de downgrade numpy

### 3. **--prefer-binary**

```batch
--prefer-binary  # Evita compilação desnecessária
```

**O quê faz:**
- Usa wheels pré-compiladas quando possível
- Reduz compile time (evita Cython)
- Mantém numpy 1.24.3 intacto

---

## 🔍 Verificar Se Funcionou

### Método 1: Verificar install.log

```bash
Get-Content .\install.log | Select-String "numpy"
```

**Esperado:**
```
Installing collected packages: ..., numpy-1.24.3, ...
Successfully installed numpy-1.24.3
```

**NÃO deve aparecer:**
```
numpy 2.3.5
Conflict
ERROR
```

### Método 2: Verificar Versão Instalada

```bash
.\venv\Scripts\python.exe -c "import numpy; print(numpy.__version__)"
```

**Esperado:** `1.24.3`

### Método 3: Verificar Gruut

```bash
.\venv\Scripts\python.exe -c "import gruut; print(gruut.__version__)"
```

**Esperado:** `2.2.3` (sem erro de incompatibilidade)

### Método 4: Verificar TTS

```bash
.\venv\Scripts\python.exe -c "import TTS; print(TTS.__version__)"
```

**Esperado:** Não deve dar erro (compilação bem-sucedida)

---

## ❌ Se Ainda Falhar

### Cenário 1: numpy 2.3.5 Ainda Aparece

```bash
# Forçar limpeza de cache pip
rmdir /s /q ..\pip_cache
mkdir ..\pip_cache

# Forçar rebuild
rmdir /s /q venv
python -m venv venv
start-server.bat 2 1
```

### Cenário 2: "gruut version conflict"

```bash
# Verificar requirements.txt
findstr /i "numpy\|gruut\|styletts2" requirements.txt

# Verificar o que estava instalado
.\venv\Scripts\pip show gruut
.\venv\Scripts\pip show numpy
.\venv\Scripts\pip show styletts2
```

### Cenário 3: Outra versão de Numpy Instalada

```bash
# Desinstalar todas versões
.\venv\Scripts\pip uninstall -y numpy

# Instalar 1.24.3 especificamente
.\venv\Scripts\pip install --force-reinstall numpy==1.24.3

# Verificar
.\venv\Scripts\python.exe -c "import numpy; print(numpy.__version__)"
```

---

## 📊 Comparação: Antes vs Depois

| Aspecto | Antes (Falho) | Depois (Fix) |
|---------|---------------|-------------|
| numpy versão | 2.3.5 | 1.24.3 |
| Build isolation | DEFAULT (sim) | DESABILITADO |
| Binários pré-compiled | Não (compila tudo) | Sim (--prefer-binary) |
| Gruut compatível | NÃO ❌ | SIM ✅ |
| Tempo install | Mais longo | Mais rápido |
| Conflitos | SIM | NÃO |

---

## 🧪 Teste Full

```bash
# 1. Verificar Python
python --version

# 2. Pre-flight check
preflight-check.bat

# 3. Instalar com fix
start-server.bat 2 1
# Aguarde 15-30 min

# 4. Verificar versões
.\venv\Scripts\pip list | Select-String "numpy\|gruut\|TTS\|styletts2"

# 5. Testar server
start-server.bat 3 1
# Em outro terminal:
test-server.py

# 6. Verificar engines
curl http://localhost:8000/v1/monitor/info | python -m json.tool
```

---

## 💾 Cache Directories (Todos Configurados)

Após o fix, todos esses diretórios usam projeto-local:

```
..\pip_cache                  # pip cache
..\tts_cache                  # TTS models
..\torch_cache                # Torch weights
..\huggingface_cache          # HF models
..\numba_cache                # Numba compilations
..\matplotlib_cache           # Matplotlib fonts
```

✅ **Zero poluição em C:\ ou %APPDATA%**

---

## 🎯 Summary

**O quê foi feito:**
1. Pinnar numpy em 1.24.3 (compatível com gruut <3.0.0)
2. Desabilitar build isolation (reutilizar numpy do sistema)
3. Usar binários pré-compilados (--prefer-binary)
4. Adicionar logging para debug

**Resultado esperado:**
- ✅ numpy 1.24.3 instalado
- ✅ gruut 2.2.3 instalado SEM CONFLITO
- ✅ TTS compilado com sucesso
- ✅ styletts2 carregado
- ✅ Servidor iniciado

**Se não funcionar:**
- Limpar cache: `rmdir /s /q ..\pip_cache`
- Reconstruir venv: `rmdir /s /q venv`
- Tentar novamente: `start-server.bat 1 1`

---

## 📞 Escalation

Se mesmo depois do fix persistir erro:

1. **Coletar info:**
   ```bash
   Get-Content .\install.log > install-error.log
   ```

2. **Executar monitor:**
   ```bash
   powershell -NoProfile -ExecutionPolicy Bypass .\install-monitor.ps1
   # Opção 1: Analisar log
   # Opção 2: Verificar versões
   ```

3. **Verificar ambiente:**
   ```bash
   python --version
   pip --version
   Get-Item Env:PIP_CACHE_DIR
   ```

4. **Último recurso:**
   ```bash
   # Limpar TUDO
   rmdir /s /q venv ..\pip_cache ..\torch_cache ..\huggingface_cache ..\tts_cache ..\numba_cache ..\matplotlib_cache
   
   # Reinstalar do zero
   python -m venv venv
   start-server.bat 1 1
   ```

---

## ✨ Confirmação de Sucesso

Quando ver isso no console:

```
[%date% %time%] Iniciando Etapa 2...
Installing collected packages: numpy
Successfully installed numpy-1.24.3

[%date% %time%] Etapa 2 concluida
[OK] Etapa 2 concluida

[%date% %time%] Iniciando Etapa 3...
Successfully installed TTS-... gruut-2.2.3 styletts2-0.1.6 ...

[OK] Etapa 3 concluida
[OK] Todas as dependencias instaladas com sucesso!

INFO:     Uvicorn running on http://0.0.0.0:8000
```

**🎉 VOCÊ CONSEGUIU! Fase 4.2 Operacional!**
