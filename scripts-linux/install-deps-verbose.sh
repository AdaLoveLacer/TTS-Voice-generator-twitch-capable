#!/bin/bash

################################################################################
# Install Dependencies - Verbose Mode
# Instala todas as dependências do projeto com logs detalhados
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Instalando Dependências (Verbose)"
echo -e "========================================${NC}"
echo ""

# Check if we're in the repo root
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}[X] Erro: requirements.txt não encontrado${NC}"
    echo -e "${RED}[X] Execute este script a partir da raiz do repositório${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Verificando ambiente Python...${NC}"
python3 --version
python3_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "${CYAN}Versão detectada: Python $python3_version${NC}"

# Verificar dependências do sistema
echo ""
echo -e "${CYAN}[*] Verificando dependências de build do sistema...${NC}"
if command -v apt-get &> /dev/null; then
    echo -e "${CYAN}[*] Distribuição baseada em Debian/Ubuntu detectada${NC}"
    echo -e "${YELLOW}[!] Instalando dependências de build necessárias...${NC}"
    sudo apt-get update
    sudo apt-get install -y \
        build-essential \
        python3-dev \
        python3-pip \
        python3-venv \
        git \
        curl \
        libffi-dev \
        libssl-dev
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao instalar dependências de sistema${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependências de sistema instaladas${NC}"
elif command -v yum &> /dev/null; then
    echo -e "${CYAN}[*] Distribuição baseada em RHEL/CentOS detectada${NC}"
    echo -e "${YELLOW}[!] Instalando dependências de build necessárias...${NC}"
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y \
        python3-devel \
        python3-pip \
        git \
        curl \
        libffi-devel \
        openssl-devel
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao instalar dependências de sistema${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependências de sistema instaladas${NC}"
else
    echo -e "${YELLOW}[!] Distribuição não detectada automaticamente${NC}"
    echo -e "${YELLOW}[!] Certifique-se de ter build-essential/Development Tools instalado${NC}"
fi

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

echo ""
echo -e "${CYAN}[*] Atualizando pip, setuptools e wheel...${NC}"
pip install --upgrade pip setuptools wheel
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao atualizar ferramentas de build${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Ferramentas de build atualizadas${NC}"

echo ""
echo -e "${CYAN}[*] Instalando dependências do projeto...${NC}"
pip install -r requirements.txt --verbose
if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao instalar requirements.txt${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Dependências do projeto instaladas${NC}"

echo ""
echo -e "${CYAN}[*] Instalando dependências do xtts-server...${NC}"
if [ -f "xtts-server/requirements.txt" ]; then
    pip install -r xtts-server/requirements.txt --verbose
    if [ $? -ne 0 ]; then
        echo -e "${RED}[X] Erro ao instalar xtts-server/requirements.txt${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ Dependências do xtts-server instaladas${NC}"
else
    echo -e "${YELLOW}[!] xtts-server/requirements.txt não encontrado${NC}"
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Instalação concluída com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Para ativar o ambiente, execute:${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
