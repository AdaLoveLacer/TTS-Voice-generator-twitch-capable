#!/bin/bash
# Script para iniciar servidor XTTS v2 (Linux/macOS)
# - Cria venv automaticamente se nao existir
# - Instala dependencias
# - Inicia servidor (main.py abre navegador automaticamente)

set -e  # Exit on error

echo "=========================================="
echo "    XTTS v2 TTS Server para Speakerbot"
echo "=========================================="
echo ""

# Definir diretorio do script como pasta atual
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Criar diretorio de cache local se nao existir
mkdir -p ".pip-cache"

echo "[INFO] Verificando ambiente virtual..."

# Criar ambiente virtual se nao existir
if [ ! -d "venv" ]; then
    echo "[INFO] Criando ambiente virtual..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "[ERRO] Falha ao criar venv!"
        exit 1
    fi
    
    echo "[OK] Ambiente virtual criado!"
    echo ""
fi

# Ativar ambiente virtual
echo "[INFO] Ativando ambiente virtual..."
source venv/bin/activate

if [ $? -ne 0 ]; then
    echo "[ERRO] Falha ao ativar venv!"
    exit 1
fi

echo "[OK] Ambiente virtual ativado!"
echo ""

# Menu de instalacao CUDA
echo "=========================================="
echo "Deseja verificar/reinstalar CUDA?"
echo "=========================================="
echo "1 - Sim, reinstalar torch/torchaudio com CUDA 11.8"
echo "2 - Nao, usar versao existente"
echo ""
read -p "Digite sua escolha (1 ou 2): " cuda_choice

case $cuda_choice in
    1)
        echo "[INFO] Desinstalando torch e torchaudio..."
        python -m pip uninstall -y torch torchaudio 2>/dev/null || true
        echo ""
        echo "[INFO] Instalando torch e torchaudio com CUDA 11.8..."
        python -m pip install --cache-dir ".pip-cache" -i https://download.pytorch.org/whl/cu118 torch==2.7.1 torchaudio==2.7.1
        echo ""
        python -c "import torch; print('CUDA disponivel:', torch.cuda.is_available()); print('Dispositivos:', torch.cuda.device_count())"
        echo ""
        ;;
    2)
        echo "[INFO] Usando versao existente de torch/torchaudio..."
        echo ""
        ;;
    *)
        echo "[AVISO] Opcao invalida. Usando versao existente..."
        echo ""
        ;;
esac

# Instalar dependencias
echo "[INFO] Instalando dependencias..."
python -m pip install --upgrade pip setuptools wheel
pip install --cache-dir ".pip-cache" -r requirements.txt --prefer-binary

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Falha ao instalar dependencias!"
    exit 1
fi

echo ""
echo "=========================================="
echo "[OK] Iniciando servidor XTTS v2..."
echo "=========================================="
echo ""
echo "Abra seu navegador em: http://localhost:8877"
echo "API Docs: http://localhost:8877/docs"
echo ""
echo "Pressione CTRL+C para parar o servidor"
echo ""

# Iniciar servidor (main.py abre navegador automaticamente)
python main.py

# Capturar status de saida
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERRO] Falha ao iniciar servidor!"
    exit 1
fi
