@echo off
setlocal enabledelayedexpansion

REM Automaticamente passa opcoes 2 e 2 ao start-server.bat
cd /d "%~dp0"

REM Executar start-server.bat com entrada automatica
(
  echo 2
  echo 2
) | .\start-server.bat

endlocal
