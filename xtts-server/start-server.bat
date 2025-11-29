@echo off
setlocal enabledelayedexpansion
REM Script para iniciar servidor XTTS v2
REM - Cria venv automaticamente se nao existir
REM - Instala dependencias
REM - Inicia servidor (main.py abre navegador automaticamente)

echo ==========================================
echo    XTTS v2 TTS Server para Speakerbot
echo ==========================================
echo.

REM Definir diretorio do script como pasta atual
cd /d "%~dp0"

REM Criar diretorio de cache local se nao existir
if not exist ".pip-cache" (
    mkdir ".pip-cache"
)

echo [INFO] Verificando ambiente virtual...

REM Criar ambiente virtual se nao existir
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
    
    if errorlevel 1 (
        echo.
        echo [ERRO] Falha ao criar venv!
        pause
        exit /b 1
    )
    
    echo [OK] Ambiente virtual criado!
    echo.
)

REM Ativar ambiente virtual
echo [INFO] Ativando ambiente virtual...
call venv\Scripts\activate.bat

if errorlevel 1 (
    echo [ERRO] Falha ao ativar venv!
    pause
    exit /b 1
)

echo [OK] Ambiente virtual ativado!
echo.

REM Menu de instalacao CUDA
echo ==========================================
echo Deseja verificar/reinstalar CUDA?
echo ==========================================
echo 1 - Sim, reinstalar torch/torchaudio com CUDA 11.8
echo 2 - Nao, usar versao existente
echo.
set /p cuda_choice="Digite sua escolha (1 ou 2): "

if "%cuda_choice%"=="1" (
    echo [INFO] Desinstalando torch e torchaudio...
    python -m pip uninstall -y torch torchaudio
    echo.
    echo [INFO] Instalando torch e torchaudio com CUDA 11.8...
    python -m pip install --cache-dir ".pip-cache" -i https://download.pytorch.org/whl/cu118 torch==2.7.1 torchaudio==2.7.1
    echo.
    python -c "import torch; print('CUDA disponivel:', torch.cuda.is_available()); print('Dispositivos:', torch.cuda.device_count())"
    echo.
)

REM Instalar dependencias
echo [INFO] Instalando dependencias...
python -m pip install --upgrade pip setuptools wheel
pip install --cache-dir ".pip-cache" -r requirements.txt --prefer-binary

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] Iniciando servidor XTTS v2...
echo ==========================================
echo.
echo Abra seu navegador em: http://localhost:8877
echo API Docs: http://localhost:8877/docs
echo.
echo Pressione CTRL+C para parar o servidor
echo.

REM Iniciar servidor (main.py abre navegador automaticamente)
python main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar servidor!
    pause
)

endlocal

