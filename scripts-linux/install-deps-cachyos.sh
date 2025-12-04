#!/bin/bash

################################################################################
# Instalar Dependências Direto do CachyOS
# Alternativa quando pip não funciona
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Instalando Dependências CachyOS"
echo -e "========================================${NC}"
echo ""

if ! command -v pacman &> /dev/null; then
    echo -e "${RED}[X] CachyOS/Arch não detectado${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Instalando dependências do CachyOS/Arch...${NC}"

# Dependências base
echo -e "${CYAN}[*] Base build${NC}"
sudo pacman -S base-devel --noconfirm

# Python e ferramentas
echo -e "${CYAN}[*] Python 3.11${NC}"
sudo pacman -S python311 python311-pip --noconfirm

# Audio
echo -e "${CYAN}[*] Bibliotecas de áudio${NC}"
sudo pacman -S libsndfile alsa-lib portaudio --noconfirm

# FFmpeg
echo -e "${CYAN}[*] FFmpeg${NC}"
sudo pacman -S ffmpeg --noconfirm

# Dependências de build
echo -e "${CYAN}[*] Ferramentas de build${NC}"
sudo pacman -S gcc cmake git curl wget --noconfirm

# Dependências de desenvolvimento
echo -e "${CYAN}[*] Dependências de desenvolvimento${NC}"
sudo pacman -S libffi openssl blas lapack --noconfirm

echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Dependências do CachyOS instaladas!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Próximo passo:${NC}"
echo -e "  ${YELLOW}python3.11 -m venv venv${NC}"
echo -e "  ${YELLOW}source venv/bin/activate${NC}"
echo -e "  ${YELLOW}pip install -r requirements-linux.txt${NC}"
