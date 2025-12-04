#!/bin/bash

################################################################################
# Git Cleanup - Remove Cached Files
# Remove venv, cache, logs e outros arquivos do git cache
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================"
echo -e "Git Cleanup - Remover Arquivos em Cache"
echo -e "========================================${NC}"
echo ""

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo -e "${RED}[X] Erro: Não estamos em um repositório git${NC}"
    exit 1
fi

echo -e "${CYAN}[*] Preparando para remover arquivos de cache do git...${NC}"
echo ""

# Array of patterns to remove from git cache
patterns=(
    ".vscode/"
    "xtts-server/venv/"
    "venv/"
    ".env"
    ".env.local"
    ".env.*.local"
    "req-no-tts-*.txt"
    "vs_BuildTools.exe"
    "xtts-server/voices/custom/*"
    "xtts-server/voices/embeddings/*"
    "*.log"
    "build/"
    "dist/"
    "__pycache__/"
    ".pytest_cache/"
    ".mypy_cache/"
    ".coverage"
    ".coverage.*"
    "*.pyc"
    ".pip-cache/"
    "Releases/"
    "*.whl"
)

# Show what will be removed (dry-run)
echo -e "${YELLOW}[*] Arquivos que serão removidos do git (modo seco):${NC}"
echo ""

total_count=0
for pattern in "${patterns[@]}"; do
    # Use find to count matching items
    count=$(find . -path "$pattern" -prune -print 2>/dev/null | wc -l)
    
    if [ $count -gt 0 ]; then
        echo -e "    ${CYAN}[→]${NC} $pattern ($count item(s))"
        total_count=$((total_count + count))
    fi
done

echo ""
echo -e "${YELLOW}Total: $total_count arquivos/pastas serão removidos${NC}"
echo ""

# Ask for confirmation
read -p "Tem certeza que deseja remover estes arquivos do git? (s/n): " response
if [ "$response" != "s" ] && [ "$response" != "S" ]; then
    echo -e "${YELLOW}[i] Operação cancelada pelo usuário${NC}"
    exit 0
fi

echo ""
echo -e "${CYAN}[*] Removendo arquivos do git...${NC}"
echo ""

removed_count=0
for pattern in "${patterns[@]}"; do
    # Use git rm with patterns
    git rm --cached -r -f "$pattern" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Removido: $pattern${NC}"
        removed_count=$((removed_count + 1))
    fi
done

echo ""
echo -e "${GREEN}========================================"
echo -e "Resumo da Limpeza"
echo -e "========================================${NC}"
echo -e "${GREEN}[✓] $removed_count padrões processados${NC}"
echo ""

# Show git status
echo -e "${CYAN}[*] Status do git:${NC}"
echo ""
git status --short | head -20
echo ""

# Suggest commit
echo -e "${CYAN}[i] Próximas ações:${NC}"
echo -e "    1. Revisar: ${CYAN}git status${NC}"
echo -e "    2. Commit:  ${CYAN}git commit -m 'Remove cached venv, logs and sensitive files'${NC}"
echo -e "    3. Push:    ${CYAN}git push${NC}"
echo ""

read -p "Deseja fazer o commit agora? (s/n): " commit_response
if [ "$commit_response" = "s" ] || [ "$commit_response" = "S" ]; then
    echo -e "${CYAN}[*] Fazendo commit...${NC}"
    git add .gitignore
    git commit -m "Remove cached venv, logs, build artifacts and sensitive files

- Remove .vscode/ configuration
- Remove venv/ virtual environment
- Remove .env* files
- Remove temporary requirements files
- Remove build/dist artifacts
- Remove cache and temporary files
- Add comprehensive .gitignore"

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] Commit realizado com sucesso!${NC}"
        echo ""
        echo -e "${CYAN}Próximo passo: git push${NC}"
    else
        echo -e "${RED}[!] Erro ao fazer commit${NC}"
    fi
fi

echo ""
