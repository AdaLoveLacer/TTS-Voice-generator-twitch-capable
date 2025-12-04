#!/bin/bash

################################################################################
# Fix PEP 668 - Contorna restrições externally-managed-environment
# Para CachyOS/Arch Linux que bloqueiam instalações no Python do sistema
################################################################################

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}========================================"
echo -e "Corrigindo PEP 668 (externally-managed)"
echo -e "========================================${NC}"
echo ""

# Detectar se estamos em CachyOS/Arch
if ! command -v pacman &> /dev/null; then
    echo -e "${YELLOW}[!] Este script é otimizado para CachyOS/Arch${NC}"
    echo -e "${YELLOW}[!] Continuando mesmo assim...${NC}"
    echo ""
fi

# Opção 1: Instalar python311-pip via pacman
if command -v pacman &> /dev/null; then
    echo -e "${CYAN}[*] Tentando instalar python311-pip via pacman...${NC}"
    sudo pacman -S --noconfirm python311-pip 2>&1 | tail -5
    
    if python3.11 -m pip --version &> /dev/null; then
        echo -e "${GREEN}✓ pip instalado com sucesso via pacman${NC}"
        python3.11 -m pip --version
        exit 0
    fi
fi

# Opção 2: Usar --break-system-packages com ensurepip
echo ""
echo -e "${CYAN}[*] Tentando ensurepip com --break-system-packages...${NC}"
python3.11 -m ensurepip --upgrade --default-pip --break-system-packages 2>&1 | tail -5

if python3.11 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓ pip instalado com sucesso${NC}"
    python3.11 -m pip --version
    exit 0
fi

# Opção 3: Usar get-pip.py com --break-system-packages
echo ""
echo -e "${CYAN}[*] Tentando get-pip.py com --break-system-packages...${NC}"

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py 2>/dev/null || \
wget -q https://bootstrap.pypa.io/get-pip.py 2>/dev/null || {
    echo -e "${RED}[X] Não foi possível baixar get-pip.py${NC}"
    exit 1
}

python3.11 get-pip.py --break-system-packages 2>&1 | tail -5

cd - > /dev/null
rm -rf "$TEMP_DIR"

if python3.11 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓ pip instalado com sucesso${NC}"
    python3.11 -m pip --version
    exit 0
else
    echo -e "${RED}[X] Não foi possível instalar pip${NC}"
    exit 1
fi
