#!/bin/bash

################################################################################
# Menu Automático - Setup + Servidor
# Executa todas as etapas automaticamente e inicia o servidor
# Em caso de erro, solicita ao usuário o que fazer
# 
# Uso:
#   bash auto-setup.sh          # Modo interativo (pede input em caso de erro)
#   bash auto-setup.sh --daemon # Modo daemon (pula erros silenciosamente)
################################################################################

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SEPARATOR="════════════════════════════════════════════════════════════════════"

# Detectar se está rodando em modo daemon/background
DAEMON_MODE=0
if [ "$1" = "--daemon" ] || [ -z "$PS1" ] || ! [ -t 0 ]; then
    DAEMON_MODE=1
fi

################################################################################
# FUNÇÕES AUXILIARES
################################################################################

show_header() {
    clear
    echo -e "${BLUE}"
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║        🚀 TTS VOICE GENERATOR - SETUP AUTOMÁTICO + SERVIDOR 🚀    ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

show_step() {
    echo ""
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${GREEN}[*] $1${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

show_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

show_error() {
    echo -e "${RED}✗ $1${NC}"
}

show_warning() {
    echo -e "${YELLOW}[!] $1${NC}"
}

# Menu de ação em caso de erro
error_menu() {
    local error_msg=$1
    local step_name=$2
    
    echo ""
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}ERRO EM: $step_name${NC}"
    echo -e "${RED}Mensagem: $error_msg${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Em modo daemon, sempre pula o erro
    if [ $DAEMON_MODE -eq 1 ]; then
        echo -e "${YELLOW}[DAEMON] Pulando erro e continuando...${NC}"
        return 1
    fi
    
    echo ""
    echo -e "${YELLOW}O que você quer fazer?${NC}"
    echo "  1) Tentar novamente este passo"
    echo "  2) Pular este passo e continuar"
    echo "  3) Cancelar e sair"
    echo ""
    
    read -p "Escolha uma opção (1-3): " choice
    echo ""
    
    case $choice in
        1) return 0 ;; # retry
        2) return 1 ;; # skip
        3) 
            echo -e "${YELLOW}Abortando setup...${NC}"
            exit 1
            ;;
        *)
            echo -e "${RED}Opção inválida${NC}"
            error_menu "$error_msg" "$step_name"
            ;;
    esac
}

check_repo() {
    if [ ! -d ".git" ] && [ ! -f "requirements.txt" ]; then
        show_error "Execute este script a partir da raiz do repositório"
        exit 1
    fi
}

################################################################################
# ETAPAS DO SETUP
################################################################################

# Etapa 1: Validar ambiente
step_validate() {
    show_step "1/5 Validando Ambiente"
    
    if ! command -v python3 &> /dev/null; then
        show_error "Python 3 não encontrado"
        return 1
    fi
    
    show_success "Python 3 encontrado: $(python3 --version)"
    
    if ! command -v python3.11 &> /dev/null; then
        show_warning "Python 3.11 não encontrado (opcional)"
    else
        show_success "Python 3.11 encontrado"
    fi
    
    return 0
}

# Etapa 2: Criar/validar venv
step_venv() {
    show_step "2/5 Configurando Ambiente Virtual"
    
    if [ ! -d "venv" ]; then
        echo "Criando ambiente virtual..."
        python3 -m venv venv 2>&1 | grep -v "DeprecationWarning" || true
        
        if [ ! -d "venv" ]; then
            show_error "Falha ao criar ambiente virtual"
            return 1
        fi
        show_success "Ambiente virtual criado"
    else
        show_success "Ambiente virtual já existe"
        
        # Verificar se venv está funcional
        if [ ! -f "venv/bin/activate" ]; then
            show_warning "venv corrompido, recriando..."
            rm -rf venv
            python3 -m venv venv 2>&1 | grep -v "DeprecationWarning" || true
            
            if [ ! -d "venv" ]; then
                show_error "Falha ao recriar ambiente virtual"
                return 1
            fi
            show_success "Ambiente virtual recriado"
        fi
    fi
    
    # Ativar venv AGORA, antes de continuar
    source venv/bin/activate 2>&1 || {
        show_error "Falha ao ativar ambiente virtual"
        return 1
    }
    show_success "Ambiente virtual ativado"
    
    return 0
}

# Etapa 3: Recuperar/instalar pip
step_pip() {
    show_step "3/5 Instalando Gerenciador de Pacotes (pip)"
    
    # Verificar se pip funciona
    if python -m pip --version &> /dev/null 2>&1; then
        show_success "pip já disponível"
        # Upgrade pip, setuptools, wheel
        echo "Atualizando pip, setuptools e wheel..."
        pip install --upgrade pip setuptools wheel 2>&1 | tail -2 || true
        return 0
    fi
    
    echo "Tentando instalar pip..."
    
    # Tentar ensurepip com --break-system-packages
    python -m ensurepip --upgrade --default-pip --break-system-packages 2>&1 | tail -3 || true
    
    if python -m pip --version &> /dev/null 2>&1; then
        show_success "pip instalado com sucesso"
        pip install --upgrade pip setuptools wheel 2>&1 | tail -2 || true
        return 0
    fi
    
    # Se falhar, tentar get-pip.py
    echo "Tentando método alternativo (get-pip.py)..."
    TEMP_DIR=$(mktemp -d)
    cd "$TEMP_DIR" || return 1
    
    curl -s https://bootstrap.pypa.io/get-pip.py -o get-pip.py 2>/dev/null || \
    wget -q https://bootstrap.pypa.io/get-pip.py 2>/dev/null || {
        cd - > /dev/null
        rm -rf "$TEMP_DIR"
        show_error "Não foi possível baixar get-pip.py"
        return 1
    }
    
    python get-pip.py --break-system-packages 2>&1 | tail -3 || true
    
    cd - > /dev/null
    rm -rf "$TEMP_DIR"
    
    if python -m pip --version &> /dev/null 2>&1; then
        show_success "pip instalado via get-pip.py"
        pip install --upgrade pip setuptools wheel 2>&1 | tail -2 || true
        return 0
    fi
    
    show_error "Falha ao instalar pip"
    return 1
}

# Etapa 4: Instalar dependências
step_dependencies() {
    show_step "4/5 Instalando Dependências"
    
    # Determinar qual requirements usar baseado no ENGINE_TYPE
    local engine_type="${ENGINE_TYPE:-xtts}"
    local req_file="requirements-xtts.txt"
    
    case "$engine_type" in
        xtts)
            req_file="requirements-xtts.txt"
            echo -e "${CYAN}Engine selecionado: XTTS v2${NC}"
            ;;
        styletts2)
            req_file="requirements-styletts2.txt"
            echo -e "${CYAN}Engine selecionado: StyleTTS2${NC}"
            ;;
        both)
            req_file="requirements-xtts.txt"
            echo -e "${CYAN}Engine selecionado: AMBOS (XTTS + StyleTTS2)${NC}"
            ;;
    esac
    
    echo ""
    
    if [ ! -f "$req_file" ] && [ "$engine_type" != "both" ]; then
        show_error "$req_file não encontrado"
        return 1
    fi
    
    # Verificar se pip está funcionando
    if ! python -m pip --version &> /dev/null 2>&1; then
        show_error "pip não está disponível"
        return 1
    fi
    
    # Verificar dependências críticas
    echo "Verificando dependências já instaladas..."
    local missing_deps=0
    local engine_type="${ENGINE_TYPE:-xtts}"
    
    case "$engine_type" in
        xtts)
            for module in numpy torch librosa soundfile TTS; do
                if python -c "import $module" 2>/dev/null; then
                    show_success "✓ $module já instalado"
                else
                    show_warning "✗ $module não encontrado"
                    ((missing_deps++))
                fi
            done
            ;;
        styletts2)
            for module in numpy torch librosa soundfile styletts2; do
                if python -c "import $module" 2>/dev/null; then
                    show_success "✓ $module já instalado"
                else
                    show_warning "✗ $module não encontrado"
                    ((missing_deps++))
                fi
            done
            ;;
        both)
            for module in numpy torch librosa soundfile TTS styletts2; do
                if python -c "import $module" 2>/dev/null; then
                    show_success "✓ $module já instalado"
                else
                    show_warning "✗ $module não encontrado"
                    ((missing_deps++))
                fi
            done
            ;;
    esac
    
    # Se há dependências faltando, instalar
    if [ $missing_deps -gt 0 ]; then
        echo ""
        echo "Instalando dependências faltantes..."
        local engine_type="${ENGINE_TYPE:-xtts}"
        
        case "$engine_type" in
            xtts)
                echo "Instalando requirements XTTS v2..."
                python -m pip install -q -r requirements-xtts.txt 2>&1 | tail -5 || {
                    show_warning "Erro ao instalar requirements-xtts.txt"
                    python -m pip install -q torch torchaudio 2>&1 | tail -3 || true
                    python -m pip install -q TTS librosa soundfile numpy 2>&1 | tail -3 || true
                }
                ;;
            styletts2)
                echo "Instalando requirements StyleTTS2..."
                python -m pip install -q -r requirements-styletts2.txt 2>&1 | tail -5 || {
                    show_warning "Erro ao instalar requirements-styletts2.txt"
                    python -m pip install -q torch torchaudio 2>&1 | tail -3 || true
                    python -m pip install -q styletts2 librosa soundfile numpy 2>&1 | tail -3 || true
                }
                ;;
            both)
                echo "========================================="
                echo "Instalando AMBOS os engines TTS"
                echo "========================================="
                echo ""
                
                echo "📦 [1/2] Instalando XTTS v2 no venv principal..."
                python -m pip install -q -r requirements-xtts.txt 2>&1 | tail -3 || {
                    show_warning "Erro ao instalar XTTS v2, tentando fallback..."
                    python -m pip install -q torch torchaudio TTS 2>&1 | tail -2 || true
                }
                
                if python -c "import TTS" 2>/dev/null; then
                    show_success "✓ XTTS v2 instalado no venv principal"
                else
                    show_warning "⚠ XTTS v2 pode ter problemas"
                fi
                
                echo ""
                echo "📦 [2/2] Criando venv separado para StyleTTS2..."
                
                if [ -d "venv-styletts2" ]; then
                    echo "   (venv-styletts2 já existe, atualizando...)"
                    venv-styletts2/bin/python -m pip install -q --upgrade pip setuptools wheel 2>&1 | tail -1 || true
                else
                    echo "   Criando novo venv..."
                    python3.11 -m venv venv-styletts2 2>/dev/null || python -m venv venv-styletts2 2>/dev/null || {
                        show_error "Falha ao criar venv-styletts2"
                        return 1
                    }
                    
                    echo "   Atualizando pip..."
                    venv-styletts2/bin/python -m pip install -q --upgrade pip setuptools wheel 2>&1 | tail -1 || true
                fi
                
                echo "   Instalando StyleTTS2 com todas as dependências..."
                venv-styletts2/bin/python -m pip install -q -r requirements-styletts2.txt 2>&1 | tail -3 || {
                    show_warning "⚠ Erro ao instalar requirements-styletts2.txt, tentando pacotes individuais..."
                    venv-styletts2/bin/python -m pip install -q styletts2 TTS librosa soundfile numpy 2>&1 | tail -2 || true
                }
                
                if venv-styletts2/bin/python -c "from styletts2 import tts; import TTS" 2>/dev/null; then
                    show_success "✓ StyleTTS2 instalado em venv-styletts2"
                else
                    show_warning "⚠ StyleTTS2 pode ter problemas"
                fi
                
                echo ""
                echo "✅ AMBOS os engines estão configurados!"
                echo "   - XTTS v2: Venv principal (venv)"
                echo "   - StyleTTS2: venv-styletts2"
                ;;
        esac
        
        if [ -f "xtts-server/requirements-linux.txt" ]; then
            echo "Instalando dependências do servidor..."
            python -m pip install -q -r xtts-server/requirements-linux.txt 2>&1 | tail -5 || true
        fi
    else
        show_success "Todas as dependências já estão instaladas"
        return 0
    fi
    
    # Verificar instalação por engine
    local engine_type="${ENGINE_TYPE:-xtts}"
    
    case "$engine_type" in
        xtts)
            if python -c "import TTS" 2>/dev/null; then
                show_success "✓ XTTS v2 instalado corretamente"
            else
                show_warning "⚠ TTS pode não ter sido instalado corretamente"
            fi
            ;;
        styletts2)
            if python -c "from styletts2 import tts" 2>/dev/null; then
                show_success "✓ StyleTTS2 instalado corretamente"
            else
                show_warning "⚠ StyleTTS2 pode não ter sido instalado corretamente"
            fi
            ;;
        both)
            if python -c "import TTS" 2>/dev/null; then
                show_success "✓ XTTS v2 disponível"
            else
                show_warning "⚠ XTTS v2 com problemas"
            fi
            
            if [ -d "venv-styletts2" ] && venv-styletts2/bin/python -c "from styletts2 import tts; import TTS" 2>/dev/null; then
                show_success "✓ StyleTTS2 disponível em venv-styletts2"
            else
                show_warning "⚠ StyleTTS2 pode ter problemas ou não instalado"
            fi
            ;;
    esac
    
    return 0
}

# Etapa 5: Iniciar servidor
step_server() {
    show_step "5/5 Iniciando Servidor"
    
    if [ ! -f "xtts-server/start.py" ]; then
        show_error "xtts-server/start.py não encontrado"
        return 1
    fi
    
    # Verificar pré-requisitos
    echo "Verificando pré-requisitos..."
    local engine_type="${ENGINE_TYPE:-xtts}"
    
    case "$engine_type" in
        xtts)
            if ! python -c "import TTS" 2>/dev/null; then
                show_error "Módulo TTS não encontrado!"
                echo "Tentando instalar TTS..."
                python -m pip install -q "TTS>=0.21.0" 2>&1 | tail -3 || true
                
                if ! python -c "import TTS" 2>/dev/null; then
                    show_error "Falha ao instalar TTS"
                    return 1
                fi
            fi
            ;;
        styletts2)
            if ! python -c "from styletts2 import tts" 2>/dev/null; then
                show_error "Módulo StyleTTS2 não encontrado!"
                echo "Tentando instalar StyleTTS2..."
                python -m pip install -q "styletts2>=0.1.6" 2>&1 | tail -3 || true
                
                if ! python -c "from styletts2 import tts" 2>/dev/null; then
                    show_error "Falha ao instalar StyleTTS2"
                    return 1
                fi
            fi
            ;;
        both)
            if ! python -c "import TTS" 2>/dev/null; then
                show_warning "⚠ XTTS v2 não encontrado"
                python -m pip install -q "TTS>=0.21.0" 2>&1 | tail -3 || true
            fi
            
            if [ -d "venv-styletts2" ] && ! venv-styletts2/bin/python -c "from styletts2 import tts" 2>/dev/null; then
                show_warning "⚠ StyleTTS2 não encontrado em venv-styletts2"
            fi
            ;;
    esac
    show_success "Pré-requisitos OK"
    
    # Verificar se estamos no venv ativado
    if [ -z "$VIRTUAL_ENV" ]; then
        show_warning "Ambiente virtual não está ativado"
        echo "Ativando venv..."
        source venv/bin/activate || {
            show_error "Falha ao ativar venv"
            return 1
        }
    fi
    
    cd xtts-server
    
    echo ""
    local engine_type="${ENGINE_TYPE:-xtts}"
    case "$engine_type" in
        xtts)
            echo -e "${CYAN}Iniciando servidor XTTS v2...${NC}"
            ;;
        styletts2)
            echo -e "${CYAN}Iniciando servidor StyleTTS2...${NC}"
            ;;
        both)
            echo -e "${CYAN}Iniciando servidor com suporte a XTTS v2 + StyleTTS2...${NC}"
            ;;
    esac
    echo -e "${YELLOW}(Pressione CTRL+C para parar)${NC}"
    echo ""
    
    # Executar servidor com stdin redirectionado para /dev/null
    # Isso evita problema de fechamento de stdin após piped input
    export XTTS_AUTO_LICENSE=1
    python main.py </dev/null 2>&1
    local exit_code=$?
    unset XTTS_AUTO_LICENSE
    
    cd - > /dev/null
    
    if [ $exit_code -eq 0 ]; then
        show_success "Servidor finalizado normalmente"
        return 0
    elif [ $exit_code -eq 130 ] || [ $exit_code -eq 2 ]; then
        show_warning "Servidor interrompido pelo usuário"
        return 0
    else
        show_error "Servidor finalizado com erro: $exit_code"
        return 1
    fi
}

################################################################################
# FLUXO PRINCIPAL
################################################################################

main() {
    show_header
    
    # Verificar se está na raiz do repositório
    check_repo
    
    echo ""
    echo -e "${GREEN}Iniciando setup automático...${NC}"
    echo ""
    
    # Array de etapas
    declare -a STEPS=(
        "step_validate:Validação do Ambiente"
        "step_venv:Configuração do Ambiente Virtual"
        "step_pip:Instalação do pip"
        "step_dependencies:Instalação de Dependências"
        "step_server:Inicialização do Servidor"
    )
    
    # Executar cada etapa
    for step_info in "${STEPS[@]}"; do
        IFS=':' read -r step_func step_name <<< "$step_info"
        
        # Para a etapa de venv, garantir que é executada
        if [ "$step_func" = "step_venv" ]; then
            while true; do
                $step_func
                local result=$?
                
                if [ $result -eq 0 ]; then
                    # Garantir que venv está ativado
                    if [ -z "$VIRTUAL_ENV" ]; then
                        source venv/bin/activate
                    fi
                    break
                else
                    error_menu "Falha na execução de $step_name" "$step_name"
                    local user_choice=$?
                    
                    if [ $user_choice -eq 0 ]; then
                        continue
                    else
                        show_warning "Pulando $step_name..."
                        break
                    fi
                fi
            done
            continue
        fi
        
        while true; do
            $step_func
            local result=$?
            
            if [ $result -eq 0 ]; then
                # Sucesso, continuar
                break
            else
                # Erro, perguntar ao usuário
                error_menu "Falha na execução de $step_name" "$step_name"
                local user_choice=$?
                
                if [ $user_choice -eq 0 ]; then
                    # Tentar novamente
                    continue
                else
                    # Pular esta etapa
                    show_warning "Pulando $step_name..."
                    break
                fi
            fi
        done
    done
    
    echo ""
    echo -e "${BLUE}$SEPARATOR${NC}"
    echo -e "${GREEN}✓ Setup Completo!${NC}"
    echo -e "${BLUE}$SEPARATOR${NC}"
    echo ""
    echo -e "${CYAN}Para próximas vezes, ative o ambiente com:${NC}"
    echo -e "  ${YELLOW}source venv/bin/activate${NC}"
    echo ""
}

# Executar
main
