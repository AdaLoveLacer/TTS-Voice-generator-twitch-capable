#!/bin/bash

################################################################################
# Validar e Preparar Ambiente para Instalação
# Verifica compatibilidade antes de instalar dependências
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Validando Ambiente para Python 3.11"
echo -e "========================================${NC}"
echo ""

# Verificar Python 3.11
echo -e "${CYAN}[*] Verificando Python 3.11...${NC}"
if command -v python3.11 &> /dev/null; then
    python3_version=$(python3.11 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
    echo -e "${GREEN}✓ Python 3.11 encontrado: $python3_version${NC}"
else
    echo -e "${RED}[X] Python 3.11 não encontrado${NC}"
    exit 1
fi

# Verificar pip
echo ""
echo -e "${CYAN}[*] Verificando pip3.11...${NC}"
if python3.11 -m pip --version &> /dev/null; then
    pip_version=$(python3.11 -m pip --version | awk '{print $2}')
    echo -e "${GREEN}✓ pip encontrado: $pip_version${NC}"
else
    echo -e "${YELLOW}[!] pip não disponível no momento${NC}"
    echo -e "${YELLOW}[!] Será recuperado durante a instalação${NC}"
fi

# Verificar venv
echo ""
echo -e "${CYAN}[*] Verificando módulo venv...${NC}"
if python3.11 -c "import venv" 2>/dev/null; then
    echo -e "${GREEN}✓ Módulo venv disponível${NC}"
else
    echo -e "${RED}[X] Módulo venv não disponível${NC}"
    exit 1
fi

# Verificar espaço em disco
echo ""
echo -e "${CYAN}[*] Verificando espaço em disco...${NC}"
available_space=$(df . | awk 'NR==2 {print $4}')
required_space=5242880  # 5GB em KB
if [ "$available_space" -gt "$required_space" ]; then
    echo -e "${GREEN}✓ Espaço disponível: $(numfmt --to=iec-i --suffix=B $((available_space * 1024)))${NC}"
else
    echo -e "${YELLOW}[!] Espaço limitado: $(numfmt --to=iec-i --suffix=B $((available_space * 1024)))${NC}"
    echo -e "${YELLOW}[!] Recomenda-se pelo menos 5GB${NC}"
fi

# Verificar distribuição
echo ""
echo -e "${CYAN}[*] Detectando distribuição...${NC}"
if [ -f /etc/os-release ]; then
    . /etc/os-release
    echo -e "${GREEN}✓ Sistema: $PRETTY_NAME${NC}"
    
    if command -v pacman &> /dev/null; then
        echo -e "${CYAN}[*] CachyOS detectado (Arch-based)${NC}"
        echo -e "${YELLOW}[!] Certifique-se de ter build tools instalados:${NC}"
        echo -e "    ${YELLOW}sudo pacman -S base-devel${NC}"
    fi
fi

# Resumo final
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Ambiente validado com sucesso!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "${CYAN}Próximo passo: execute o script de instalação${NC}"
echo -e "  ${YELLOW}./menu.sh${NC}"
echo -e "  ${YELLOW}Escolha: 1 (Instalar Python 3.11 + Dependências)${NC}"
