#!/bin/bash

################################################################################
# Install SDK and Build Tools (Linux)
# Instala automaticamente build-essential e dependencies
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

set -e  # Exit on error

echo -e "${GREEN}========================================"
echo -e "Instalador do SDK/Build Tools (Linux)"
echo -e "========================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${CYAN}[*] Executando como root${NC}"
    SUDO=""
else
    echo -e "${YELLOW}[!] Esta operação requer privilégios de sudo${NC}"
    SUDO="sudo"
fi

echo ""

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo -e "${RED}[X] Não foi possível detectar a distribuição Linux${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Distribuição detectada: $DISTRO${NC}"
echo ""

# Install based on distribution
case "$DISTRO" in
    ubuntu|debian)
        echo -e "${CYAN}[*] Instalando via apt (Debian/Ubuntu)...${NC}"
        echo ""
        
        echo -e "${CYAN}    Atualizando lista de pacotes...${NC}"
        $SUDO apt update
        
        echo -e "${CYAN}    Instalando build-essential...${NC}"
        $SUDO apt install -y build-essential python3-dev python3-pip
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] build-essential instalado com sucesso via apt${NC}"
        else
            echo -e "${RED}[X] Falha ao instalar build-essential${NC}"
            exit 1
        fi
        ;;
        
    fedora)
        echo -e "${CYAN}[*] Instalando via dnf (Fedora)...${NC}"
        echo ""
        
        echo -e "${CYAN}    Instalando desenvolvimento tools...${NC}"
        $SUDO dnf groupinstall -y "Development Tools"
        
        echo -e "${CYAN}    Instalando Python dev...${NC}"
        $SUDO dnf install -y python3-devel
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] Development Tools instalados com sucesso via dnf${NC}"
        else
            echo -e "${RED}[X] Falha ao instalar Development Tools${NC}"
            exit 1
        fi
        ;;
        
    arch|manjaro)
        echo -e "${CYAN}[*] Instalando via pacman (Arch/Manjaro)...${NC}"
        echo ""
        
        echo -e "${CYAN}    Instalando base-devel...${NC}"
        $SUDO pacman -S --noconfirm base-devel python
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] base-devel instalado com sucesso via pacman${NC}"
        else
            echo -e "${RED}[X] Falha ao instalar base-devel${NC}"
            exit 1
        fi
        ;;
        
    centos|rhel)
        echo -e "${CYAN}[*] Instalando via yum (CentOS/RHEL)...${NC}"
        echo ""
        
        echo -e "${CYAN}    Instalando desenvolvimento tools...${NC}"
        $SUDO yum groupinstall -y "Development Tools"
        
        echo -e "${CYAN}    Instalando Python dev...${NC}"
        $SUDO yum install -y python3-devel
        
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] Development Tools instalados com sucesso via yum${NC}"
        else
            echo -e "${RED}[X] Falha ao instalar Development Tools${NC}"
            exit 1
        fi
        ;;
        
    *)
        echo -e "${YELLOW}[!] Distribuição não reconhecida: $DISTRO${NC}"
        echo ""
        echo -e "${CYAN}Instale manualmente os development tools:${NC}"
        echo ""
        echo "Para Debian/Ubuntu:"
        echo "  sudo apt update && sudo apt install build-essential python3-dev"
        echo ""
        echo "Para Fedora:"
        echo "  sudo dnf groupinstall 'Development Tools' && sudo dnf install python3-devel"
        echo ""
        echo "Para Arch:"
        echo "  sudo pacman -S base-devel python"
        echo ""
        exit 1
        ;;
esac

echo ""

# Verify installation
echo -e "${CYAN}[*] Verificando instalação...${NC}"
echo ""

if command -v gcc &> /dev/null; then
    gcc_version=$(gcc --version | head -1)
    echo -e "${GREEN}[✓] GCC: $gcc_version${NC}"
else
    echo -e "${RED}[X] GCC não encontrado${NC}"
    exit 1
fi

if command -v make &> /dev/null; then
    make_version=$(make --version | head -1)
    echo -e "${GREEN}[✓] Make: $make_version${NC}"
fi

python3_version=$(python3 --version)
echo -e "${GREEN}[✓] Python: $python3_version${NC}"

echo ""
echo -e "${GREEN}========================================"
echo -e "Instalação concluída com sucesso!"
echo -e "========================================${NC}"
echo ""
echo -e "${CYAN}Próximo passo:${NC}"
echo "  python3 xtts-server/start.py install"
echo ""
