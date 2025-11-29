#!/bin/bash
# Instalador CUDA (cu118) para Torch/Torchaudio (Linux/macOS)

set -e

cd "$(dirname "$0")"

echo "=========================================="
echo " Instalador CUDA (cu118) para Torch/Torchaudio"
echo "=========================================="
echo ""

# Ativar venv
echo "[INFO] Ativando venv..."
if [ ! -d "venv" ]; then
    echo "[ERRO] venv nao encontrado! Execute start-server.sh primeiro."
    exit 1
fi

source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao ativar venv!"
    exit 1
fi

# Criar diretorio de cache
mkdir -p ".pip-cache"

echo "[INFO] Desinstalando torch e torchaudio..."
python -m pip uninstall -y torch torchaudio 2>/dev/null || true

echo "[INFO] Instalando torch e torchaudio com CUDA 11.8..."
python -m pip install --upgrade pip setuptools wheel
python -m pip install --cache-dir ".pip-cache" --prefer-binary -i https://download.pytorch.org/whl/cu118 torch==2.7.1 torchaudio==2.7.1

echo ""
echo "[INFO] Verificando instalacao..."
python -c "import torch; print('TORCH VERSION:', torch.__version__); print('CUDA AVAILABLE:', torch.cuda.is_available()); print('CUDA DEVICES:', torch.cuda.device_count())"

echo ""
echo "[OK] Instalacao completa!"
