#!/bin/bash

################################################################################
# Install Dependencies - Smart Version Detection
# Instala dependências com suporte a múltiplas versões do Python
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Instalando Dependências (Inteligente)"
echo -e "========================================${NC}"
echo ""

# Check if we're in the repo root
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[X] Erro: requirements.txt não encontrado${NC}"
    echo -e "${RED}[X] Execute este script a partir da raiz do repositório${NC}"
    exit 1
fi

# Detectar versão do Python
echo -e "${CYAN}[*] Detectando versão do Python...${NC}"
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
python_major=$(echo "$python_version" | cut -d. -f1)
python_minor=$(echo "$python_version" | cut -d. -f2)

echo -e "${CYAN}Versão detectada: Python $python_version${NC}"

# Verificar compatibilidade
if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo -e "${RED}[X] Python 3.8+ é necessário${NC}"
    exit 1
fi

# Instalar dependências do sistema
echo ""
echo -e "${CYAN}[*] Verificando dependências de build do sistema...${NC}"
if command -v apt-get &> /dev/null; then
    echo -e "${YELLOW}[!] Instalando dependências (Ubuntu/Debian)...${NC}"
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        python3-dev \
        python3-pip \
        python3-venv \
        git \
        curl \
        libffi-dev \
        libssl-dev \
        libsndfile1 \
        ffmpeg
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao instalar dependências de sistema${NC}"
        exit 1
    fi
elif command -v yum &> /dev/null; then
    echo -e "${YELLOW}[!] Instalando dependências (RHEL/CentOS)...${NC}"
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
        python3-devel \
        python3-pip \
        git \
        curl \
        libffi-devel \
        openssl-devel \
        libsndfile-devel \
        ffmpeg
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao instalar dependências de sistema${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}[!] Distribuição não detectada${NC}"
fi

# Criar venv se não existir
if [ ! -d "venv" ]; then
    echo ""
    echo -e "${CYAN}[*] Criando ambiente virtual...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao criar ambiente virtual${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
fi

echo ""
echo -e "${CYAN}[*] Ativando ambiente virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"

# Atualizar ferramentas de build
echo ""
echo -e "${CYAN}[*] Atualizando pip, setuptools e wheel...${NC}"
pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao atualizar ferramentas${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ferramentas de build atualizadas${NC}"

# Criar requirements.txt temporário com versões compatíveis
echo ""
echo -e "${CYAN}[*] Criando requirements.txt com versões compatíveis...${NC}"

TEMP_REQUIREMENTS=$(mktemp)
cat > "$TEMP_REQUIREMENTS" << 'EOF'
--index-url https://pypi.org/simple/
--extra-index-url https://download.pytorch.org/whl/cu118

# Core dependencies
librosa>=0.10.0
soundfile>=0.12.0
gtts>=2.3.0
sounddevice>=0.4.5

# PyTorch - CUDA 11.8
torch>=2.0.0,<3.0
torchaudio>=2.0.0,<3.0

# TTS Engines
TTS>=0.22.0
StyleTTS2>=0.2.0
transformers>=4.30.0

# FastAPI Web Server
fastapi>=0.104.1
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pydantic>=2.0.0

# ML/Audio utilities
rich>=13.0.0
av>=11.0.0
faiss-cpu>=1.7.4
scipy>=1.9.0,<1.13
scikit-learn>=1.1.0
requests>=2.28.0

# Utilities
python-dotenv>=0.19.0
click>=8.0.0
EOF

# Adicionar NumPy com versão compatível
if [ "$python_minor" -ge 13 ]; then
    echo -e "${YELLOW}[!] Python 3.13 detectado - usando NumPy 2.x${NC}"
    echo "numpy>=2.0.0,<3.0" >> "$TEMP_REQUIREMENTS"
elif [ "$python_minor" -ge 12 ]; then
    echo -e "${YELLOW}[!] Python 3.12 detectado - usando NumPy 1.26+${NC}"
    echo "numpy>=1.26.0,<3.0" >> "$TEMP_REQUIREMENTS"
else
    echo -e "${YELLOW}[!] Python 3.8-3.11 detectado - usando NumPy 1.24.3 ou superior${NC}"
    echo "numpy>=1.21.0,<3.0" >> "$TEMP_REQUIREMENTS"
fi

echo -e "${GREEN}✓ Requirements.txt customizado criado${NC}"

# Instalar requirements.txt base (usar requirements-linux.txt se existir)
echo ""
echo -e "${CYAN}[*] Instalando dependências do projeto...${NC}"

if [ -f "requirements-linux.txt" ]; then
    echo -e "${YELLOW}[*] Usando requirements-linux.txt${NC}"
    pip install -r requirements-linux.txt
else
    echo -e "${YELLOW}[*] Usando requirements.txt${NC}"
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao instalar requirements${NC}"
    rm "$TEMP_REQUIREMENTS"
    exit 1
fi
echo -e "${GREEN}✓ Dependências do projeto instaladas${NC}"

# Instalar requirements do xtts-server (customizado)
echo ""
echo -e "${CYAN}[*] Instalando dependências do xtts-server...${NC}"
pip install -r "$TEMP_REQUIREMENTS"

if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao instalar dependências do xtts-server${NC}"
    rm "$TEMP_REQUIREMENTS"
    exit 1
fi
echo -e "${GREEN}✓ Dependências do xtts-server instaladas${NC}"

# Limpar arquivo temporário
rm "$TEMP_REQUIREMENTS"

# Listar pacotes instalados
echo ""
echo -e "${CYAN}[*] Listando pacotes instalados...${NC}"
pip list

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Resumo:${NC}"
echo -e "  Python: ${YELLOW}$python_version${NC}"
echo -e "  NumPy: ${YELLOW}$([ $python_minor -ge 13 ] && echo "2.x+" || ([ $python_minor -ge 12 ] && echo "1.26+" || echo "1.24.3"))${NC}"
echo -e "  Ambiente virtual: ${YELLOW}./venv${NC}"
echo ""
echo -e "${CYAN}Para ativar o ambiente, execute:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
