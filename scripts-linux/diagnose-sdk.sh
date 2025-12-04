#!/bin/bash

################################################################################
# Diagnose SDK Installation Status
# Verifica status de instalação do SDK, compiladores e bibliotecas
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "SDK / GCC / Build Tools Diagnostics"
echo -e "========================================${NC}"
echo ""

# 1. Check for GCC/Clang
echo -e "${CYAN}[*] Procurando compiladores...${NC}"
echo ""

if command -v gcc &> /dev/null; then
    gcc_version=$(gcc --version | head -1)
    echo -e "${GREEN}[✓] GCC encontrado: $gcc_version${NC}"
else
    echo -e "${RED}[!] GCC não encontrado${NC}"
fi

if command -v clang &> /dev/null; then
    clang_version=$(clang --version | head -1)
    echo -e "${GREEN}[✓] Clang encontrado: $clang_version${NC}"
else
    echo -e "${YELLOW}[!] Clang não encontrado${NC}"
fi

if command -v cc &> /dev/null; then
    cc_version=$(cc --version | head -1)
    echo -e "${GREEN}[✓] CC encontrado: $cc_version${NC}"
fi

echo ""

# 2. Check for Make
echo -e "${CYAN}[*] Procurando make...${NC}"
echo ""

if command -v make &> /dev/null; then
    make_version=$(make --version | head -1)
    echo -e "${GREEN}[✓] Make encontrado: $make_version${NC}"
else
    echo -e "${RED}[!] Make não encontrado${NC}"
fi

echo ""

# 3. Check for development headers
echo -e "${CYAN}[*] Procurando headers de desenvolvimento...${NC}"
echo ""

header_locations=(
    "/usr/include"
    "/usr/local/include"
    "/opt/include"
)

headers_found=0
for path in "${header_locations[@]}"; do
    if [ -d "$path" ]; then
        header_count=$(find "$path" -name "*.h" 2>/dev/null | wc -l)
        if [ $header_count -gt 0 ]; then
            echo -e "${GREEN}[✓] Headers encontrados em: $path ($header_count arquivo(s))${NC}"
            headers_found=$((headers_found + 1))
        fi
    fi
done

if [ $headers_found -eq 0 ]; then
    echo -e "${RED}[!] Nenhum header de desenvolvimento encontrado${NC}"
    echo -e "${YELLOW}    Considere instalar: build-essential ou equivalent${NC}"
fi

echo ""

# 4. Check for Python development files
echo -e "${CYAN}[*] Procurando Python dev files...${NC}"
echo ""

python3_version=$(python3 --version 2>&1)
echo -e "${GREEN}[✓] Python encontrado: $python3_version${NC}"

if python3 -c "import sys; print(sys.prefix)" &> /dev/null; then
    python_prefix=$(python3 -c "import sys; print(sys.prefix)")
    
    # Check for Python.h
    if find "$python_prefix" -name "Python.h" 2>/dev/null | grep -q .; then
        echo -e "${GREEN}[✓] Python.h encontrado${NC}"
    else
        echo -e "${YELLOW}[!] Python.h não encontrado - você pode precisar de python3-dev${NC}"
    fi
fi

echo ""

# 5. Check package managers
echo -e "${CYAN}[*] Verificando gerenciadores de pacotes...${NC}"
echo ""

if command -v apt &> /dev/null; then
    echo -e "${GREEN}[✓] apt encontrado (Debian/Ubuntu)${NC}"
elif command -v dnf &> /dev/null; then
    echo -e "${GREEN}[✓] dnf encontrado (Fedora)${NC}"
elif command -v pacman &> /dev/null; then
    echo -e "${GREEN}[✓] pacman encontrado (Arch)${NC}"
elif command -v brew &> /dev/null; then
    echo -e "${GREEN}[✓] brew encontrado (macOS)${NC}"
else
    echo -e "${YELLOW}[!] Nenhum gerenciador de pacotes familiar encontrado${NC}"
fi

echo ""

# 6. Summary and recommendations
echo -e "${GREEN}========================================"
echo -e "RESUMO E RECOMENDAÇÕES"
echo -e "========================================${NC}"
echo ""

issues=0

if ! command -v gcc &> /dev/null && ! command -v clang &> /dev/null; then
    echo -e "${RED}[X] Nenhum compilador C/C++ encontrado${NC}"
    issues=$((issues + 1))
fi

if ! command -v make &> /dev/null; then
    echo -e "${RED}[X] Make não encontrado${NC}"
    issues=$((issues + 1))
fi

if [ $headers_found -eq 0 ]; then
    echo -e "${RED}[X] Headers de desenvolvimento não encontrados${NC}"
    issues=$((issues + 1))
fi

if [ $issues -eq 0 ]; then
    echo -e "${GREEN}[✓] Tudo parece estar configurado corretamente!${NC}"
else
    echo -e "${YELLOW}[!] Foram encontrados $issues problemas${NC}"
    echo ""
    echo -e "${CYAN}Para resolver, execute um dos comandos abaixo:${NC}"
    echo ""
    echo -e "${CYAN}Debian/Ubuntu:${NC}"
    echo "  sudo apt update"
    echo "  sudo apt install build-essential python3-dev"
    echo ""
    echo -e "${CYAN}Fedora:${NC}"
    echo "  sudo dnf groupinstall 'Development Tools'"
    echo "  sudo dnf install python3-devel"
    echo ""
    echo -e "${CYAN}Arch:${NC}"
    echo "  sudo pacman -S base-devel python"
    echo ""
    echo -e "${CYAN}macOS:${NC}"
    echo "  xcode-select --install"
    echo "  brew install python3"
fi

echo ""
