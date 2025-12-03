@echo off
REM Install Windows SDK 11 from Microsoft
REM This is needed for C/C++ compilation headers (io.h, etc.)

cd /d "%~dp0"

echo [*] Instalando Windows SDK 11...
echo.
echo Para compilar TTS (Python package) no Windows, necessário:
echo - Windows SDK (com C/C++ headers)
echo - Visual Studio Build Tools (instalado em F:\C++\dev\)
echo.

REM Tenta usar winget se disponível
where winget >nul 2>&1
if errorlevel 1 (
    echo [!] winget não encontrado. Instalando manualmente...
    echo [*] Baixando installer...
    
    REM Download Windows 11 SDK
    powershell -Command "Invoke-WebRequest -Uri 'https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/' -OutFile windows-sdk-installer.html"
    
    echo [!] Acesse: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/
    echo [!] Baixe e execute o instalador manualmente
    echo [!] Durante instalação, selecione os components:
    echo     - Windows App SDK Runtime
    echo     - Windows SDK
    pause
    exit /b 1
)

echo [*] Usando winget para instalar...
winget install --id Microsoft.WindowsSDK --version=11.0

if errorlevel 1 (
    echo [X] Falha ao instalar Windows SDK
    exit /b 1
)

echo [✓] Windows SDK instalado com sucesso!
echo [*] Tente novamente: python start.py install
