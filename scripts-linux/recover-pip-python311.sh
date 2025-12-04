#!/bin/bash

################################################################################
# Recuperar pip Python 3.11 - Com suporte a PEP 668 (CachyOS/Arch)
# Garante que pip está funcionando corretamente
# Contorna externally-managed-environment em distros Arch-based
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Recuperando pip para Python 3.11"
echo -e "========================================${NC}"
echo ""

if ! command -v python3.11 &> /dev/null; then
    echo -e "${RED}[X] Python 3.11 não encontrado${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Tentando recuperar pip...${NC}"

# Opção 1: ensurepip com --break-system-packages (para CachyOS/Arch)
echo -e "${CYAN}[*] Método 1: Usando ensurepip com --break-system-packages...${NC}"
python3.11 -m ensurepip --upgrade --default-pip --break-system-packages 2>&1 | grep -v "DeprecationWarning" || true

if python3.11 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓ pip funcionando (ensurepip)${NC}"
    python3.11 -m pip --version
    exit 0
fi

# Opção 2: Baixar get-pip.py
echo ""
echo -e "${CYAN}[*] Método 2: Instalando via get-pip.py...${NC}"

TEMP_DIR=$(mktemp -d)
cd "$TEMP_DIR" || exit 1

echo -e "${CYAN}[*] Baixando get-pip.py...${NC}"
curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py 2>/dev/null || \
wget -q https://bootstrap.pypa.io/get-pip.py 2>/dev/null || {
    echo -e "${YELLOW}[!] Não foi possível baixar get-pip.py (rede indisponível)${NC}"
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    # Opção 3: Tentar instalar via pacman em CachyOS/Arch
    echo ""
    echo -e "${CYAN}[*] Método 3: Tentando instalar python311-pip via pacman...${NC}"
    if command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python311-pip 2>/dev/null || true
        
        if python3.11 -m pip --version &> /dev/null; then
            echo -e "${GREEN}✓ pip funcionando (pacman)${NC}"
            exit 0
        fi
    fi
    
    # Opção 4: Usar pip do sistema
    echo ""
    echo -e "${CYAN}[*] Método 4: Criando symlink para pip do sistema...${NC}"
    if command -v pip3 &> /dev/null; then
        sudo ln -sf $(which pip3) /usr/local/bin/pip3.11 2>/dev/null || true
        
        if python3.11 -m pip --version &> /dev/null; then
            echo -e "${GREEN}✓ pip funcionando (pip do sistema)${NC}"
            exit 0
        fi
    fi
    
    exit 1
}

echo -e "${CYAN}[*] Instalando pip via get-pip.py com --break-system-packages...${NC}"
python3.11 get-pip.py --break-system-packages 2>&1 | grep -v "DeprecationWarning" || true

cd - > /dev/null
rm -rf "$TEMP_DIR"

if python3.11 -m pip --version &> /dev/null; then
    echo -e "${GREEN}✓ pip recuperado com sucesso (get-pip.py)!${NC}"
    python3.11 -m pip --version
    exit 0
else
    echo -e "${RED}[X] Não foi possível recuperar pip${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ pip Python 3.11 pronto!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
