@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo ==========================================
echo  Installer CUDA (cu118) para Torch/Torchaudio
echo ==========================================
echo.

REM Ativar venv
echo [INFO] Ativando venv...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERRO] Falha ao ativar venv!
    pause
    exit /b 1
)

REM Definir cache
set "PIP_CACHE_DIR=%CD%\.pip-cache"
set "TMP=%CD%\.pip-tmp"
set "TEMP=%CD%\.pip-tmp"

if not exist "%PIP_CACHE_DIR%" mkdir "%PIP_CACHE_DIR%"
if not exist "%TMP%" mkdir "%TMP%"

echo [INFO] Desinstalando torch e torchaudio...
python -m pip uninstall -y torch torchaudio

echo [INFO] Instalando torch e torchaudio com CUDA 11.8...
python -m pip install --upgrade pip setuptools wheel
python -m pip install --prefer-binary --extra-index-url https://download.pytorch.org/whl/cu118 torch==2.9.1 torchaudio==2.9.1

echo.
echo [INFO] Verificando instalacao...
python -c "import torch; print('TORCH VERSION:', torch.__version__); print('CUDA AVAILABLE:', torch.cuda.is_available()); print('CUDA DEVICES:', torch.cuda.device_count())"

echo.
echo [OK] Instalacao completa!
pause
