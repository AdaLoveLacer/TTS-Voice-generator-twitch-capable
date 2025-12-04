#!/bin/bash

# Atalho para iniciar o menu interativo
# Execute este script a partir da raiz do repositório

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MENU_SCRIPT="${SCRIPT_DIR}/scripts-linux/menu-interativo.sh"

if [ ! -f "$MENU_SCRIPT" ]; then
    echo "Erro: Menu interativo não encontrado em $MENU_SCRIPT"
    exit 1
fi

# Criar venv se não existir
if [ ! -d "venv" ]; then
    echo ""
    echo "🔧 Criando ambiente virtual (venv)..."
    python3 -m venv venv 2>&1 | grep -v "DeprecationWarning" || true
    if [ ! -d "venv" ]; then
        echo "❌ Erro ao criar venv. Tente manualmente:"
        echo "   python3 -m venv venv"
        exit 1
    fi
    echo "✓ Ambiente virtual criado com sucesso!"
    echo ""
fi

# Ativar venv e executar menu
source venv/bin/activate
bash "$MENU_SCRIPT"
EXIT_CODE=$?
deactivate 2>/dev/null || true
exit $EXIT_CODE
