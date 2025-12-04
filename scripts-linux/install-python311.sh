#!/bin/bash

################################################################################
# Instalar Python 3.11 com pip
# Garante que Python 3.11 e pip estão instalados
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Instalando Python 3.11"
echo -e "========================================${NC}"
echo ""

# Verificar se Python 3.11 já está instalado
if command -v python3.11 &> /dev/null; then
    echo -e "${GREEN}✓ Python 3.11 já está instalado${NC}"
    python3.11 --version
else
    echo -e "${CYAN}[*] Python 3.11 não encontrado, instalando...${NC}"

    # Detectar distribuição
    if command -v pacman &> /dev/null; then
        echo -e "${CYAN}[*] Detectado: CachyOS/Arch${NC}"
        
        echo -e "${CYAN}[*] Atualizando base-devel...${NC}"
        sudo pacman -Sy base-devel --noconfirm
        
        echo -e "${CYAN}[*] Instalando Python 3.11...${NC}"
        sudo pacman -S python311 --noconfirm
        
    elif command -v apt-get &> /dev/null; then
        echo -e "${CYAN}[*] Detectado: Debian/Ubuntu${NC}"
        
        if grep -qi ubuntu /etc/os-release; then
            echo -e "${CYAN}[*] Adicionando repositório deadsnakes...${NC}"
            sudo add-apt-repository -y ppa:deadsnakes/ppa 2>/dev/null || true
        fi
        
        echo -e "${CYAN}[*] Atualizando pacotes...${NC}"
        sudo apt-get update
        
        echo -e "${CYAN}[*] Instalando Python 3.11...${NC}"
        sudo apt-get install -y \
            python3.11 \
            python3.11-dev \
            python3.11-venv
        
    elif command -v yum &> /dev/null; then
        echo -e "${CYAN}[*] Detectado: RHEL/CentOS${NC}"
        
        sudo yum groupinstall -y "Development Tools"
        sudo yum install -y python3.11 python3.11-devel
    else
        echo -e "${RED}[X] Distribuição não suportada${NC}"
        exit 1
    fi
    
    if ! command -v python3.11 &> /dev/null; then
        echo -e "${RED}[X] Erro ao instalar Python 3.11${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Python 3.11 instalado${NC}"
    python3.11 --version
fi

# Garantir pip está funcionando
echo ""
echo -e "${CYAN}[*] Atualizando pip para Python 3.11...${NC}"
python3.11 -m pip install --upgrade pip setuptools wheel

if [ $? -ne 0 ]; then
    echo -e "${RED}[X] Erro ao atualizar pip${NC}"
    exit 1
fi

echo -e "${GREEN}✓ pip atualizado${NC}"

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Python 3.11 pronto para usar!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
