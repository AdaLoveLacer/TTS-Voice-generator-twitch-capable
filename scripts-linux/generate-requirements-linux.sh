#!/bin/bash

# Script para atualizar requirements-linux.txt
# Execute este script a partir da raiz do repositório

echo "Gerando requirements-linux.txt com pacotes instalados..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    pip freeze > requirements-linux.txt
    echo "✓ requirements-linux.txt atualizado"
    pip freeze > xtts-server/requirements-linux.txt
    echo "✓ xtts-server/requirements-linux.txt atualizado"
else
    echo "Erro: ambiente virtual não encontrado"
    exit 1
fi
