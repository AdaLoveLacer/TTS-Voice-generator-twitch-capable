#!/bin/bash

# ========================================================
# AUTO-SETUP LAUNCHER - Escolha de Engine TTS
# ========================================================
# Executa setup automático + servidor com seleção de engine
# Execute este script a partir da raiz do repositório
# ========================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTO_SETUP="${SCRIPT_DIR}/auto-setup.sh"

if [ ! -f "$AUTO_SETUP" ]; then
    echo "❌ Erro: auto-setup.sh não encontrado em $AUTO_SETUP"
    exit 1
fi

# Detectar modo automático (sem argumentos = interativo, com argumento = modo direto)
ENGINE_CHOICE="${1:-}"

if [ -z "$ENGINE_CHOICE" ]; then
    # Modo Interativo
    clear
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║         TTS Voice Generator - Seleção de Engine           ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Escolha o engine TTS desejado:"
    echo ""
    echo "  [1] ⭐ XTTS v2 (RECOMENDADO)"
    echo "      - Multilíngue, excelente qualidade"
    echo "      - Clonagem de voz suportada"
    echo "      - Mais estável e rápido"
    echo ""
    echo "  [2] 🎨 StyleTTS2 (EXPERIMENTAL)"
    echo "      - Qualidade superior para EN/PT"
    echo "      - Mais natureza nas expressões"
    echo "      - Requer mais recursos"
    echo ""
    echo "  [3] 🔄 AMBOS (Recomendado ter 16GB+ RAM)"
    echo "      - Instala em venvs separados"
    echo "      - Permite testar ambos"
    echo "      - Mais espaço em disco"
    echo ""
    read -p "👉 Digite sua escolha [1-3] (padrão: 1): " -e -i "1" ENGINE_CHOICE
    echo ""
fi

# Validar entrada
case "$ENGINE_CHOICE" in
    1|xtts)
        echo "✅ Engine selecionado: XTTS v2"
        export ENGINE_TYPE="xtts"
        bash "$AUTO_SETUP"
        ;;
    2|styletts2)
        echo "✅ Engine selecionado: StyleTTS2"
        export ENGINE_TYPE="styletts2"
        bash "$AUTO_SETUP"
        ;;
    3|ambos|both)
        echo "✅ Modo AMBOS os engines selecionado"
        export ENGINE_TYPE="both"
        bash "$AUTO_SETUP"
        ;;
    *)
        echo "❌ Opção inválida: $ENGINE_CHOICE"
        echo "Use: bash run-auto.sh [1|xtts|2|styletts2|3|ambos]"
        exit 1
        ;;
esac
