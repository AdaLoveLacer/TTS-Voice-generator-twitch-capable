#!/bin/bash

################################################################################
# Create Release Advanced (Linux)
# Cria e compacta um release do projeto
# Oferece opções: TAR.GZ ou ZIP
################################################################################

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(pwd)"
RELEASE_BASE="${PROJECT_ROOT}/Releases"
RELEASE_DIR="${RELEASE_BASE}/release-$(date +%Y%m%d-%H%M%S)"

function write_status() {
    local message=$1
    local type=${2:-"Info"}
    
    case "$type" in
        "Info")
            echo -e "${CYAN}[$(date +'%H:%M:%S')] $message${NC}"
            ;;
        "Success")
            echo -e "${GREEN}[$(date +'%H:%M:%S')] $message${NC}"
            ;;
        "Warn")
            echo -e "${YELLOW}[$(date +'%H:%M:%S')] $message${NC}"
            ;;
        "Error")
            echo -e "${RED}[$(date +'%H:%M:%S')] $message${NC}"
            ;;
        "Process")
            echo -e "${MAGENTA}[$(date +'%H:%M:%S')] $message${NC}"
            ;;
    esac
}

function show_menu() {
    echo ""
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
    echo -e "${CYAN}       SPEAKERBOT RELEASE CREATOR - MENU${NC}"
    echo -e "${CYAN}$(printf '=%.0s' {1..80})${NC}"
    echo ""
    echo "Escolha uma opção:"
    echo ""
    echo "  1 - Criar release simples (pasta)"
    echo "  2 - Criar e compactar em TAR.GZ"
    echo "  3 - Criar e compactar em ZIP"
    echo "  4 - Criar ambos (TAR.GZ + ZIP)"
    echo "  5 - Sair"
    echo ""
}

function get_menu_choice() {
    while true; do
        read -p "Digite sua opção (1-5): " choice
        if [[ "$choice" =~ ^[1-5]$ ]]; then
            echo "$choice"
            return
        fi
        write_status "Opção inválida! Tente novamente." "Error"
    done
}

function create_release() {
    local release_path=$1
    
    write_status "Criando estrutura de release..." "Process"
    echo ""
    
    # Remove previous release if exists
    if [ -d "$release_path" ]; then
        write_status "Removendo diretório anterior..." "Warn"
        rm -rf "$release_path"
        sleep 0.5
    fi
    
    # Create main directory
    mkdir -p "$release_path"
    write_status "Criado: $release_path" "Success"
    
    # Create voice subdirectories
    for subdir in custom embeddings presets; do
        mkdir -p "$release_path/xtts-server/voices/$subdir"
    done
    write_status "Estrutura de vozes criada" "Success"
    
    # Root files to copy
    local root_files=(
        'README.md'
        'requirements.txt'
    )
    
    for file in "${root_files[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            cp "$PROJECT_ROOT/$file" "$release_path/"
            write_status "Copiado: $file" "Success"
        fi
    done
    
    # Server files to copy
    local server_files=(
        'main.py'
        'web_ui.html'
        'speaker_embedding_manager.py'
        'voice_manager.py'
        'requirements.txt'
        'start.py'
        'check_torch.py'
    )
    
    local xtts_server_path="$PROJECT_ROOT/xtts-server"
    
    # Create engines directory
    mkdir -p "$release_path/xtts-server/engines"
    
    # Copy engine files
    local engine_files=(
        '__init__.py'
        'base_engine.py'
        'xtts_engine.py'
        'stylets2_engine.py'
    )
    
    for file in "${engine_files[@]}"; do
        if [ -f "$xtts_server_path/engines/$file" ]; then
            cp "$xtts_server_path/engines/$file" "$release_path/xtts-server/engines/"
            write_status "Copiado: xtts-server/engines/$file" "Success"
        fi
    done
    
    # Copy server files
    for file in "${server_files[@]}"; do
        if [ -f "$xtts_server_path/$file" ]; then
            cp "$xtts_server_path/$file" "$release_path/xtts-server/"
            write_status "Copiado: xtts-server/$file" "Success"
        fi
    done
    
    # Copy custom voices
    write_status "Copiando vozes customizadas..." "Process"
    
    if [ -d "$xtts_server_path/voices/custom" ]; then
        mkdir -p "$release_path/xtts-server/voices/custom"
        cp -r "$xtts_server_path/voices/custom"/* "$release_path/xtts-server/voices/custom/" 2>/dev/null || true
        write_status "Vozes customizadas copiadas" "Success"
    fi
    
    # Copy voice metadata
    if [ -f "$xtts_server_path/voices/custom/metadata.json" ]; then
        cp "$xtts_server_path/voices/custom/metadata.json" "$release_path/xtts-server/voices/custom/"
    fi
    
    if [ -f "$xtts_server_path/voices/presets/metadata.json" ]; then
        mkdir -p "$release_path/xtts-server/voices/presets"
        cp "$xtts_server_path/voices/presets/metadata.json" "$release_path/xtts-server/voices/presets/"
    fi
    
    # Create README for release
    cat > "$release_path/RELEASE_INFO.md" << 'EOF'
# TTS Voice Generator - Release

## Conteúdo

- `xtts-server/` - Servidor principal
  - `main.py` - Script principal
  - `web_ui.html` - Interface web
  - `requirements.txt` - Dependências Python
  - `engines/` - Motores de TTS (xtts_engine, stylets2_engine)
  - `voices/` - Diretório de vozes
    - `custom/` - Vozes customizadas
    - `presets/` - Vozes pré-configuradas
- `README.md` - Documentação principal

## Instalação

1. Extrair o arquivo
2. Instalar dependências: `pip install -r requirements.txt`
3. Executar: `python main.py`

## Requisitos

- Python 3.10 ou superior
- CUDA 11.8 (opcional, para GPU)
- FFmpeg
- Build tools (gcc, make, etc.)

EOF
    
    write_status "Release criado com sucesso em: $release_path" "Success"
}

function compress_targz() {
    local release_path=$1
    local output_file="${release_path}.tar.gz"
    
    write_status "Compactando em TAR.GZ..." "Process"
    
    cd "$(dirname "$release_path")"
    tar -czf "$(basename "$output_file")" "$(basename "$release_path")"
    
    if [ -f "$output_file" ]; then
        local size=$(du -h "$output_file" | cut -f1)
        write_status "Criado: $output_file ($size)" "Success"
        return 0
    else
        write_status "Erro ao criar TAR.GZ" "Error"
        return 1
    fi
}

function compress_zip() {
    local release_path=$1
    local output_file="${release_path}.zip"
    
    write_status "Compactando em ZIP..." "Process"
    
    if command -v zip &> /dev/null; then
        cd "$(dirname "$release_path")"
        zip -r -q "$(basename "$output_file")" "$(basename "$release_path")"
        
        if [ -f "$output_file" ]; then
            local size=$(du -h "$output_file" | cut -f1)
            write_status "Criado: $output_file ($size)" "Success"
            return 0
        else
            write_status "Erro ao criar ZIP" "Error"
            return 1
        fi
    else
        write_status "zip não está instalado" "Error"
        return 1
    fi
}

# Main
echo ""
echo -e "${GREEN}========================================"
echo -e "SPEAKERBOT RELEASE CREATOR"
echo -e "========================================${NC}"
echo ""

# Create release directory
mkdir -p "$RELEASE_BASE"

# Show menu and get choice
show_menu
choice=$(get_menu_choice)

case "$choice" in
    1)
        write_status "Criando release simples..." "Process"
        create_release "$RELEASE_DIR"
        write_status "Release disponível em: $RELEASE_DIR" "Success"
        ;;
    2)
        write_status "Criando release e compactando em TAR.GZ..." "Process"
        create_release "$RELEASE_DIR"
        compress_targz "$RELEASE_DIR"
        ;;
    3)
        write_status "Criando release e compactando em ZIP..." "Process"
        create_release "$RELEASE_DIR"
        compress_zip "$RELEASE_DIR"
        ;;
    4)
        write_status "Criando release e compactando em ambos formatos..." "Process"
        create_release "$RELEASE_DIR"
        compress_targz "$RELEASE_DIR"
        compress_zip "$RELEASE_DIR"
        ;;
    5)
        write_status "Saindo..." "Info"
        exit 0
        ;;
esac

echo ""
echo -e "${GREEN}========================================"
echo -e "Release criado com sucesso!"
echo -e "========================================${NC}"
echo ""
write_status "Diretório: $RELEASE_BASE" "Info"
echo ""
