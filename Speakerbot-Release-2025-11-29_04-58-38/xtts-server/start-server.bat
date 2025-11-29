@echo off
setlocal enabledelayedexpansion
REM Script para iniciar servidor XTTS v2
REM - Cria venv automaticamente se nao existir
REM - Cacheia pacotes localmente no projeto
REM - Inicia servidor automaticamente

echo ==========================================
echo    XTTS v2 TTS Server para Speakerbot
echo ==========================================
echo.

REM Forcar Python 3.11
set PATH=C:\Users\bonga\AppData\Local\Programs\Python\Python311;C:\Users\bonga\AppData\Local\Programs\Python\Python311\Scripts;%PATH%

REM Definir diretorio do script como pasta atual
cd /d "%~dp0"

REM Garantir cache e diretorios temporarios do pip dentro do projeto
set "PIP_CACHE_DIR=%CD%\.pip-cache"
set "PIP_TEMP_DIR=%CD%\.pip-tmp"
if not exist "%PIP_CACHE_DIR%" (
    mkdir "%PIP_CACHE_DIR%"
)
if not exist "%PIP_TEMP_DIR%" (
    mkdir "%PIP_TEMP_DIR%"
)
REM Apontar TMP/TEMP para pasta do projeto para evitar uso de C:\ temporario
set "TMP=%PIP_TEMP_DIR%"
set "TEMP=%PIP_TEMP_DIR%"

REM Verificar se Python 3.11 esta instalado
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERRO] Python 3.11 nao encontrado! 
    echo Por favor instale Python 3.11 em: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [OK] Python 3.11 encontrado
py -3.11 --version
echo.

REM Criar diretorio de cache local se nao existir
if not exist ".pip-cache" (
    echo [INFO] Criando diretorio de cache local...
    mkdir .pip-cache
)

echo [INFO] Verificando ambiente virtual...

REM Criar ambiente virtual se nao existir
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    echo Isso pode levar alguns minutos...
    echo.
    py -3.11 -m venv venv
    
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
echo Deseja reinstalar/verificar CUDA (torch/torchaudio)?
echo ==========================================
echo 1 - Sim, reinstalar CUDA 11.8 (cu118)
echo 2 - Nao, usar versao existente
echo.
set /p cuda_choice="Digite sua escolha (1 ou 2): "

if "%cuda_choice%"=="1" goto cuda_install
if "%cuda_choice%"=="2" goto cuda_skip
echo [AVISO] Opcao invalida. Continuando...
goto cuda_skip

:cuda_install
echo [INFO] Desinstalando torch e torchaudio...
python -m pip uninstall -y torch torchaudio
echo.
echo [INFO] Instalando torch e torchaudio com CUDA 11.8 (cu118)...
python -m pip install --upgrade pip setuptools wheel
python -m pip install --no-cache-dir --force-reinstall -i https://download.pytorch.org/whl/cu118 torch==2.7.1 torchaudio==2.7.1
echo.
echo [INFO] Verificando CUDA...
python -c "import torch; print('TORCH:', torch.__version__); print('CUDA AVAILABLE:', torch.cuda.is_available()); print('CUDA DEVICES:', torch.cuda.device_count())"
echo.
echo [OK] Instalacao CUDA completa!
echo.
goto cache_menu

:cuda_skip
echo [INFO] Usando versao existente de torch/torchaudio...
echo.

:cache_menu

:cache_menu
REM Menu de limpeza de cache
echo ==========================================
echo Deseja limpar o cache do pip?
echo ==========================================
echo 1 - Sim, limpar tudo (reinstalar do zero)
echo 2 - Nao, usar cache existente (mais rapido)
echo.
set /p cache_choice="Digite sua escolha (1 ou 2): "

if "%cache_choice%"=="1" goto cache_clean
if "%cache_choice%"=="2" goto cache_use
echo [ERRO] Opcao invalida! Usando cache local
goto cache_use

:cache_clean
echo [INFO] Limpando cache do pip...
if exist ".pip-cache\" (
    rmdir /s /q ".pip-cache"
    echo [OK] Diretorio removido
)
pip cache purge
set CACHE_FLAGS=--no-cache-dir --force-reinstall --no-deps
echo [OK] Cache limpo!
echo.
goto cache_done

:cache_use
echo [INFO] Usando cache existente...
set CACHE_FLAGS=--cache-dir ".pip-cache"
echo.

:cache_done

REM Atualizar pip, setuptools e wheel
echo [INFO] Atualizando pip, setuptools e wheel...
python -m pip install --upgrade pip setuptools wheel %CACHE_FLAGS% -vv

REM Instalar dependencias
echo [INFO] Instalando dependencias...
echo.
pip install -r requirements.txt %CACHE_FLAGS% --prefer-binary -vv

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao instalar dependencias!
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] Servidor pronto para iniciar!
echo ==========================================
echo.
echo Documentacao API: http://127.0.0.1:8877/docs
echo Health check: http://127.0.0.1:8877/v1/health
echo Endpoint TTS: http://127.0.0.1:8877/v1/tts
echo.
echo Informacoes do servidor:
python -c "import torch; print('   GPU (CUDA): ' + ('Disponivel' if torch.cuda.is_available() else 'Nao disponivel'))"
echo.
echo Pressione CTRL+C para parar o servidor
echo.
echo ==========================================
echo.

REM Iniciar servidor
echo [INFO] Iniciando servidor XTTS v2 na porta 8877...
echo.

start "" file://"%cd%\web_ui.html"

python main.py

if errorlevel 1 (
    echo.
    echo [ERRO] Falha ao iniciar servidor!
    pause
)

endlocal

