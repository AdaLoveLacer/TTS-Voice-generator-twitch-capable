#!/bin/bash
# Iniciar servidor automaticamente respondendo "Nao" aos prompts de CUDA

cd "$(dirname "$0")"

# Executar start-server.sh com entrada automatica
echo "2" | bash start-server.sh
