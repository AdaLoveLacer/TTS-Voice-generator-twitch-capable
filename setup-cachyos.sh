#!/bin/bash

# Script de Preparação Rápida para CachyOS
# Executa: validação → instalação Python 3.11 → dependências

cd "$(dirname "$0")" || exit 1

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║           🚀 Setup Rápido para CachyOS - Python 3.11 🚀           ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Instalar build tools do CachyOS
echo "[1/4] Instalando build tools..."
sudo pacman -Sy base-devel python311 curl wget --noconfirm
if [ $? -ne 0 ]; then
    echo "Erro ao instalar build tools"
    exit 1
fi

# Step 2: Recuperar pip (não-fatal)
echo ""
echo "[2/4] Preparando pip..."
bash scripts-linux/recover-pip-python311.sh || echo "[!] Continuando mesmo assim..."

# Step 3: Validar ambiente
echo ""
echo "[3/4] Validando ambiente..."
bash scripts-linux/validate-env.sh
if [ $? -ne 0 ]; then
    echo "Erro na validação do ambiente"
    exit 1
fi

# Step 4: Instalar dependências
echo ""
echo "[4/4] Instalando dependências..."
bash scripts-linux/install-deps-python311.sh

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                      ✓ Setup Completo!                            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "Para ativar o ambiente virtual:"
echo "  source venv/bin/activate"
