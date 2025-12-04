#!/bin/bash

# Atalho para executar setup automático + servidor
# Execute este script a partir da raiz do repositório

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SETUP="${SCRIPT_DIR}/auto-setup.sh"

if [ ! -f "$AUTO_SETUP" ]; then
    echo "Erro: auto-setup.sh não encontrado em $AUTO_SETUP"
    exit 1
fi

bash "$AUTO_SETUP"
