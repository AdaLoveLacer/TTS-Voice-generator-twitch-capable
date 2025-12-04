#!/bin/bash

################################################################################
# Menu Interativo - Gerenciador de Scripts Linux (OTIMIZADO)
# Interface centralizada para executar todos os scripts de manutenção
################################################################################

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Constantes
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEPARATOR="════════════════════════════════════════════════════════════════════"

################################################################################
# FUNÇÕES UTILITÁRIAS
################################################################################

# Verificar se estamos no diretório correto
check_repo() {
    if [ ! -d ".git" ] && [ ! -f "requirements.txt" ]; then
        echo -e "${RED}[X] Erro: Execute este script a partir da raiz do repositório${NC}"
        exit 1
    fi
}

# Função para exibir separador
show_separator() {
    echo -e "${BLUE}${SEPARATOR}${NC}"
}

# Função para exibir resultado e voltar
wait_return() {
    echo ""
    show_separator
    echo ""
    echo -e "${CYAN}Pressione Enter para voltar ao menu...${NC}"
    read -r
}

# Função genérica para executar script
run_script() {
    local script_name=$1
    local script_desc=$2
    local script_path="${SCRIPT_DIR}/${script_name}.sh"
    
    if [ ! -f "$script_path" ]; then
        echo -e "${RED}[X] Script não encontrado: $script_path${NC}"
        return 1
    fi
    
    clear
    show_separator
    echo -e "${GREEN}Executando: $script_desc${NC}"
    show_separator
    echo ""
    
    bash "$script_path"
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Script concluído com sucesso${NC}"
    else
        echo -e "${RED}✗ Script finalizado com código de erro: $exit_code${NC}"
    fi
    
    wait_return
}

################################################################################
# FUNÇÕES ESPECIAIS
################################################################################

# Executar setup-cachyos
run_cachyos_setup() {
    local setup_path="${SCRIPT_DIR}/../setup-cachyos.sh"
    
    if [ ! -f "$setup_path" ]; then
        echo -e "${RED}[X] Script não encontrado: $setup_path${NC}"
        return 1
    fi
    
    clear
    show_separator
    echo -e "${GREEN}Setup Rápido CachyOS - Python 3.11${NC}"
    show_separator
    echo ""
    
    bash "$setup_path"
    local exit_code=$?
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Setup CachyOS concluído com sucesso${NC}"
    else
        echo -e "${RED}✗ Setup finalizado com código de erro: $exit_code${NC}"
    fi
    
    wait_return
}

# Criar venv
create_venv() {
    clear
    show_separator
    echo -e "${GREEN}Criando Ambiente Virtual (venv)${NC}"
    show_separator
    echo ""
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}[!] Diretório venv já existe${NC}"
        read -p "Deseja sobrescrever? (s/n): " -r confirm
        if [[ ! $confirm =~ ^[Ss]$ ]]; then
            echo -e "${CYAN}Operação cancelada${NC}"
            wait_return
            return
        fi
        rm -rf venv
    fi
    
    echo -e "${CYAN}[*] Criando ambiente virtual...${NC}"
    python3 -m venv venv
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Ambiente virtual criado com sucesso${NC}"
        echo -e "${CYAN}Para ativar: source venv/bin/activate${NC}"
    else
        echo -e "${RED}✗ Erro ao criar ambiente virtual${NC}"
    fi
    
    wait_return
}

# Limpar venv
clean_venv() {
    clear
    show_separator
    echo -e "${GREEN}Limpando Ambiente Virtual (venv)${NC}"
    show_separator
    echo ""
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[!] Nenhum ambiente virtual encontrado${NC}"
        wait_return
        return
    fi
    
    echo -e "${YELLOW}[!] Esta ação removerá completamente o diretório venv${NC}"
    read -p "Deseja continuar? (s/n): " -r confirm
    
    if [[ ! $confirm =~ ^[Ss]$ ]]; then
        echo -e "${CYAN}Operação cancelada${NC}"
        wait_return
        return
    fi
    
    echo -e "${CYAN}[*] Removendo ambiente virtual...${NC}"
    rm -rf venv
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Ambiente virtual removido com sucesso${NC}"
    else
        echo -e "${RED}✗ Erro ao remover ambiente virtual${NC}"
    fi
    
    wait_return
}

# Iniciar servidor XTTS
start_server() {
    clear
    show_separator
    echo -e "${GREEN}Iniciando Servidor XTTS${NC}"
    show_separator
    echo ""
    
    local server_path="${SCRIPT_DIR}/../xtts-server"
    
    if [ ! -f "${server_path}/start.py" ]; then
        echo -e "${RED}[X] Arquivo start.py não encontrado em ${server_path}${NC}"
        wait_return
        return 1
    fi
    
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}[!] Ambiente virtual não encontrado${NC}"
        echo -e "${CYAN}Crie um ambiente virtual primeiro (opção 7)${NC}"
        wait_return
        return 1
    fi
    
    echo -e "${CYAN}[*] Ativando ambiente virtual...${NC}"
    source venv/bin/activate
    
    echo -e "${CYAN}[*] Iniciando servidor...${NC}"
    echo -e "${YELLOW}(Para parar o servidor, pressione CTRL+C)${NC}"
    echo ""
    
    cd "$server_path"
    python3 start.py
    local exit_code=$?
    cd - > /dev/null
    
    deactivate 2>/dev/null || true
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Servidor finalizado normalmente${NC}"
    elif [ $exit_code -eq 130 ]; then
        echo -e "${YELLOW}ℹ Servidor interrompido pelo usuário${NC}"
    else
        echo -e "${RED}✗ Servidor finalizado com erro: $exit_code${NC}"
    fi
    
    wait_return
}

# Selecionar script customizado
select_custom_script() {
    clear
    show_separator
    echo -e "${GREEN}Selecionar Script Customizado${NC}"
    show_separator
    echo ""
    
    local scripts=()
    local count=1
    
    for script in "$SCRIPT_DIR"/*.sh; do
        if [ "$(basename "$script")" != "menu-interativo.sh" ]; then
            scripts+=("$(basename "$script")")
            echo "  $count) $(basename "$script")"
            ((count++))
        fi
    done
    
    echo "  0) Voltar"
    echo ""
    echo -n "Escolha uma opção: "
    read -r choice
    
    if [ "$choice" -eq 0 ] 2>/dev/null; then
        return
    elif [ "$choice" -ge 1 ] && [ "$choice" -lt $count ]; then
        local selected_script="${scripts[$((choice-1))]}"
        run_script "${selected_script%.sh}" "$selected_script"
    else
        echo -e "${RED}Opção inválida${NC}"
        sleep 2
    fi
}

################################################################################
# MENU E AJUDA
################################################################################

# Mostrar menu principal
show_main_menu() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║           🚀 TTS VOICE GENERATOR - MENU INTERATIVO LINUX 🚀       ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    echo -e "${CYAN}INSTALAÇÃO E DEPENDÊNCIAS:${NC}"
    echo "  1) Setup Rápido CachyOS 🔥"
    echo "  2) Validar Ambiente 🔍"
    echo "  3) Instalar Python 3.11 + Dependências ⭐"
    echo "  4) Instalar Dependências (Verbose)"
    echo "  5) Instalar Dependências (Inteligente)"
    echo "  6) Instalar SDK Robusto"
    echo "  7) Corrigir PEP 668 (pip bloqueado) 🔧"
    echo ""
    echo -e "${CYAN}AMBIENTE VIRTUAL:${NC}"
    echo "  8) Criar Ambiente Virtual (venv)"
    echo "  9) Limpar Ambiente Virtual"
    echo ""
    echo -e "${CYAN}LIMPEZA E MANUTENÇÃO:${NC}"
    echo "  10) Limpar Cache Git"
    echo "  11) Parar Processos de Build"
    echo ""
    echo -e "${CYAN}DIAGNÓSTICO:${NC}"
    echo "  12) Diagnosticar CPU"
    echo "  13) Diagnosticar SDK"
    echo ""
    echo -e "${CYAN}RELEASE:${NC}"
    echo "  14) Criar Release Avançado"
    echo ""
    echo -e "${CYAN}SERVIDOR:${NC}"
    echo "  15) Iniciar Servidor XTTS 🌐"
    echo ""
    echo -e "${CYAN}UTILITÁRIOS:${NC}"
    echo "  16) Executar Script Customizado"
    echo "  17) Ver Ajuda"
    echo "  0) Sair"
    echo ""
}

# Mostrar ajuda
show_help() {
    clear
    show_separator
    echo -e "${GREEN}📖 AJUDA - SCRIPTS LINUX${NC}"
    show_separator
    echo ""
    
    echo -e "${YELLOW}1. INSTALAÇÃO E DEPENDÊNCIAS${NC}"
    echo "   - Setup Rápido CachyOS: Instalação automática 4-etapas"
    echo "   - Validar Ambiente: Verifica pré-requisitos do sistema"
    echo "   - Python 3.11: Instalação completa com todas as dependências"
    echo "   - Install Verbose/Inteligente: Alternativas de instalação"
    echo ""
    
    echo -e "${YELLOW}2. AMBIENTE VIRTUAL${NC}"
    echo "   - Criar venv: Cria ambiente isolado Python"
    echo "   - Limpar venv: Remove ambiente virtual existente"
    echo ""
    
    echo -e "${YELLOW}3. UTILITÁRIOS${NC}"
    echo "   - Corrigir PEP 668: Resolve erro externally-managed-environment"
    echo "   - Limpar Cache Git: Remove arquivos em cache (.gitignore)"
    echo "   - Parar Processos: Encerra builds em andamento"
    echo "   - Diagnóstico: Analisa CPU, SDK e compatibilidade"
    echo "   - Release: Cria pacotes de distribuição"
    echo ""
    
    echo -e "${YELLOW}4. SERVIDOR${NC}"
    echo "   - Iniciar XTTS: Inicia o servidor de síntese de voz"
    echo ""
    
    wait_return
}

################################################################################
# PROCESSAMENTO DE OPÇÃO
################################################################################

process_choice() {
    case $1 in
        1) run_cachyos_setup ;;
        2) run_script "validate-env" "Validar Ambiente" ;;
        3) run_script "install-deps-python311" "Instalar Python 3.11 + Dependências" ;;
        4) run_script "install-deps-verbose" "Instalar Dependências (Verbose)" ;;
        5) run_script "install-deps-smart" "Instalar Dependências (Inteligente)" ;;
        6) run_script "install-sdk-robust" "Instalar SDK Robusto" ;;
        7) run_script "fix-pep668" "Corrigir PEP 668" ;;
        8) create_venv ;;
        9) clean_venv ;;
        10) run_script "cleanup-git-cache" "Limpar Cache Git" ;;
        11) run_script "stop-build-processes" "Parar Processos de Build" ;;
        12) run_script "diagnose-cpu" "Diagnosticar CPU" ;;
        13) run_script "diagnose-sdk" "Diagnosticar SDK" ;;
        14) run_script "create-release-advanced" "Criar Release Avançado" ;;
        15) start_server ;;
        16) select_custom_script ;;
        17) show_help ;;
        0)
            clear
            echo -e "${GREEN}Até logo! 👋${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}Opção inválida!${NC}"
            sleep 2
            ;;
    esac
}

################################################################################
# MAIN
################################################################################

main() {
    check_repo
    
    while true; do
        show_main_menu
        echo -n "Escolha uma opção: "
        read -r choice
        process_choice "$choice"
    done
}

# Executar
main
