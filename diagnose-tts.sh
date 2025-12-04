#!/bin/bash

################################################################################
# Diagnóstico Detalhado do TTS Server
# Identifica problemas e exibe logs verbose
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m'

SEPARATOR="════════════════════════════════════════════════════════════════════"

echo -e "${CYAN}$SEPARATOR${NC}"
echo -e "${GREEN}🔍 DIAGNÓSTICO DETALHADO DO TTS SERVER${NC}"
echo -e "${CYAN}$SEPARATOR${NC}"
echo ""

# ============================================================================
# 1. Verificar Python e venv
# ============================================================================
echo -e "${BLUE}[1/10] Verificando Python e venv...${NC}"
echo ""

echo "Python executável:"
which python3 || which python
echo ""

echo "Versão Python:"
python3 --version 2>&1 || python --version 2>&1
echo ""

echo "venv status:"
if [ -d "venv" ]; then
    echo "✓ venv existe"
    if [ -f "venv/bin/activate" ]; then
        echo "✓ venv/bin/activate encontrado"
    else
        echo "✗ venv/bin/activate NÃO encontrado"
    fi
else
    echo "✗ venv NÃO existe"
fi
echo ""

# ============================================================================
# 2. Ativar venv e testar imports críticos
# ============================================================================
echo -e "${BLUE}[2/10] Testando imports Python...${NC}"
echo ""

if [ -f "venv/bin/python" ]; then
    PYTHON="venv/bin/python"
else
    PYTHON="python3"
fi

echo "Python a usar: $PYTHON"
echo ""

echo "Testando numpy:"
$PYTHON -c "import numpy; print('✓ numpy OK:', numpy.__version__)" 2>&1 || echo "✗ ERRO com numpy"
echo ""

echo "Testando torch:"
$PYTHON -c "import torch; print('✓ torch OK:', torch.__version__); print('  CUDA:', torch.cuda.is_available())" 2>&1 || echo "✗ ERRO com torch"
echo ""

echo "Testando librosa:"
$PYTHON -c "import librosa; print('✓ librosa OK:', librosa.__version__)" 2>&1 || echo "✗ ERRO com librosa"
echo ""

echo "Testando soundfile:"
$PYTHON -c "import soundfile; print('✓ soundfile OK')" 2>&1 || echo "✗ ERRO com soundfile"
echo ""

echo "Testando TTS (CRÍTICO):"
$PYTHON -c "from TTS.api import TTS; print('✓ TTS OK')" 2>&1 || echo "✗ ERRO com TTS - este é o problema!"
echo ""

echo "Testando FastAPI:"
$PYTHON -c "from fastapi import FastAPI; print('✓ FastAPI OK')" 2>&1 || echo "✗ ERRO com FastAPI"
echo ""

# ============================================================================
# 3. Testar imports dos engines
# ============================================================================
echo -e "${BLUE}[3/10] Testando imports dos engines...${NC}"
echo ""

echo "Testando engines.base_engine:"
$PYTHON -c "from xtts-server.engines.base_engine import BaseTTSEngine; print('✓ BaseTTSEngine OK')" 2>&1 || echo "✗ ERRO com BaseTTSEngine"
echo ""

echo "Testando engines.xtts_engine:"
$PYTHON -c "from xtts-server.engines.xtts_engine import XTTSEngine; print('✓ XTTSEngine OK')" 2>&1 || echo "✗ ERRO com XTTSEngine"
echo ""

echo "Testando engines.stylets2_engine:"
$PYTHON -c "from xtts-server.engines import stylets2_engine; print('✓ stylets2_engine importável')" 2>&1 || echo "⚠ stylets2_engine com erro (OK se styletts2 não está instalado)"
echo ""

# ============================================================================
# 4. Listar dependências instaladas
# ============================================================================
echo -e "${BLUE}[4/10] Dependências instaladas...${NC}"
echo ""

$PYTHON -m pip list | grep -E "torch|TTS|numpy|librosa|soundfile|fastapi|styletts2" || echo "Nenhuma dependência crítica encontrada!"
echo ""

# ============================================================================
# 5. Testar arquivo requirements
# ============================================================================
echo -e "${BLUE}[5/10] Verificando requirements...${NC}"
echo ""

if [ -f "requirements-linux.txt" ]; then
    echo "✓ requirements-linux.txt encontrado"
    echo "Conteúdo relevante:"
    grep -E "torch|TTS|numpy|librosa|soundfile|fastapi|styletts2" requirements-linux.txt || echo "Nenhuma dependência crítica no arquivo!"
else
    echo "✗ requirements-linux.txt NÃO encontrado"
fi
echo ""

if [ -f "xtts-server/requirements-linux.txt" ]; then
    echo "✓ xtts-server/requirements-linux.txt encontrado"
    echo "Conteúdo relevante:"
    grep -E "torch|TTS|numpy|librosa|soundfile|fastapi|styletts2" xtts-server/requirements-linux.txt || echo "Nenhuma dependência crítica no arquivo!"
else
    echo "✗ xtts-server/requirements-linux.txt NÃO encontrado"
fi
echo ""

# ============================================================================
# 6. Testar start.py
# ============================================================================
echo -e "${BLUE}[6/10] Testando start.py...${NC}"
echo ""

if [ -f "xtts-server/start.py" ]; then
    echo "✓ start.py encontrado"
    echo ""
    echo "Testando import de start.py:"
    cd xtts-server
    $PYTHON -c "import start; print('✓ start.py importável')" 2>&1 || echo "✗ ERRO ao importar start.py"
    cd ..
else
    echo "✗ start.py NÃO encontrado"
fi
echo ""

# ============================================================================
# 7. Testar main.py (o importante!)
# ============================================================================
echo -e "${BLUE}[7/10] Testando main.py (CRÍTICO)...${NC}"
echo ""

if [ -f "xtts-server/main.py" ]; then
    echo "✓ main.py encontrado"
    echo ""
    echo "Executando main.py com verbose mode (com timeout de 15s)..."
    echo ""
    cd xtts-server
    timeout 15 $PYTHON -u main.py 2>&1 <<< "y" || {
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 124 ]; then
            echo "✓ Main.py rodou por 15s (timeout esperado)"
        else
            echo "⚠ Main.py saiu com código: $EXIT_CODE"
        fi
    }
    cd ..
else
    echo "✗ main.py NÃO encontrado"
fi
echo ""

# ============================================================================
# 8. Checar porta 8877
# ============================================================================
echo -e "${BLUE}[8/10] Verificando porta 8877...${NC}"
echo ""

if lsof -i :8877 &>/dev/null; then
    echo "⚠ Porta 8877 já está em uso!"
    lsof -i :8877
else
    echo "✓ Porta 8877 livre"
fi
echo ""

# ============================================================================
# 9. Checar logs do servidor anterior
# ============================================================================
echo -e "${BLUE}[9/10] Verificando logs anteriores...${NC}"
echo ""

if [ -f "server.log" ]; then
    echo "✓ server.log encontrado"
    echo ""
    echo "Últimas 30 linhas com erros/warnings:"
    tail -100 server.log | grep -E "ERROR|ERRO|WARN|Exception|Traceback|Failed" | tail -30 || echo "Nenhum erro/warning encontrado"
    echo ""
    echo "Últimas 10 linhas do log:"
    tail -10 server.log
else
    echo "✗ server.log NÃO encontrado"
fi
echo ""

# ============================================================================
# 10. Resumo
# ============================================================================
echo -e "${BLUE}[10/10] Resumo do Diagnóstico${NC}"
echo ""

echo -e "${CYAN}$SEPARATOR${NC}"
echo -e "${GREEN}✓ Diagnóstico concluído!${NC}"
echo -e "${CYAN}$SEPARATOR${NC}"
echo ""

echo "Próximos passos:"
echo "1. Se TTS falhar em import, execute: pip install TTS"
echo "2. Se torch falhar, execute: pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118"
echo "3. Se main.py não rodar por 15s, há erro ao carregar modelo"
echo "4. Verifique variável CUDA se torch.cuda.is_available() for False"
echo ""
