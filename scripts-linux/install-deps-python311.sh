#!/bin/bash

################################################################################
# Install Dependencies - Python 3.11 Optimized
# Instala dependências para Python 3.11 especificamente
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Instalando Dependências (Python 3.11)"
echo -e "========================================${NC}"
echo ""

# Check if we're in the repo root
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[X] Erro: requirements.txt não encontrado${NC}"
    echo -e "${RED}[X] Execute este script a partir da raiz do repositório${NC}"
    exit 1
fi

# Verificar e garantir Python 3.11
echo -e "${CYAN}[*] Verificando Python 3.11...${NC}"
if ! command -v python3.11 &> /dev/null; then
    echo -e "${YELLOW}[!] Python 3.11 não encontrado. Instalando...${NC}"
    
    if command -v apt-get &> /dev/null; then
        echo -e "${CYAN}[*] Sistema: Debian/Ubuntu${NC}"
        sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
        sudo apt-get update
        sudo apt-get install -y python3.11 python3.11-dev python3.11-venv build-essential
    elif command -v yum &> /dev/null; then
        echo -e "${CYAN}[*] Sistema: RHEL/CentOS${NC}"
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3.11 python3.11-devel
    else
        echo -e "${RED}[X] Distribuição não suportada${NC}"
        exit 1
    fi
    
    if ! command -v python3.11 &> /dev/null; then
        echo -e "${RED}[X] Falha ao instalar Python 3.11${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Python 3.11 disponível:${NC}"
python3.11 --version
echo ""

# Instalar dependências de build
echo -e "${CYAN}[*] Instalando dependências de build...${NC}"
if command -v apt-get &> /dev/null; then
    sudo apt-get install -y \
        build-essential \
        python3.11-dev \
        libffi-dev \
        libssl-dev \
        libsndfile1 \
        ffmpeg \
        git \
        curl
elif command -v yum &> /dev/null; then
    sudo yum install -y \
        python3.11-devel \
        libffi-devel \
        openssl-devel \
        libsndfile-devel \
        ffmpeg \
        git \
        curl
fi
echo -e "${GREEN}✓ Dependências de build instaladas${NC}"
echo ""

# Criar ou limpar venv
if [ -d "venv" ]; then
    echo -e "${YELLOW}[!] Removendo venv anterior...${NC}"
    rm -rf venv
fi

echo -e "${CYAN}[*] Criando ambiente virtual com Python 3.11...${NC}"
python3.11 -m venv venv
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao criar ambiente virtual${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ambiente virtual criado${NC}"
echo ""

# Ativar venv
echo -e "${CYAN}[*] Ativando ambiente virtual...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Ambiente virtual ativado${NC}"
echo ""

# Atualizar ferramentas
echo -e "${CYAN}[*] Atualizando pip, setuptools e wheel...${NC}"
pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao atualizar ferramentas${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ferramentas atualizadas${NC}"
echo ""
echo -e "${CYAN}[*] Instalando requirements-linux.txt...${NC}"
if [ -f "requirements-linux.txt" ]; then
    pip install -r requirements-linux.txt
else
    pip install -r requirements.txt
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao instalar requirements principais${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependências principais instaladas${NC}"
echo ""

# Instalar dependências do xtts-server
echo -e "${CYAN}[*] Instalando dependências do xtts-server...${NC}"
if [ -f "xtts-server/requirements-linux.txt" ]; then
    pip install -r xtts-server/requirements-linux.txt
else
    pip install -r xtts-server/requirements.txt
fi

if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao instalar dependências do xtts-server${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependências do xtts-server instaladas${NC}"
echo ""

# Listar pacotes
echo -e "${CYAN}[*] Pacotes instalados:${NC}"
pip list --format=columns
echo ""

# Resumo final
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Informações:${NC}"
echo -e "  Python: ${YELLOW}$(python3.11 --version)${NC}"
echo -e "  Pip: ${YELLOW}$(pip --version)${NC}"
echo -e "  Ambiente: ${YELLOW}./venv${NC}"
echo ""
echo -e "${CYAN}Para ativar o ambiente, execute:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
