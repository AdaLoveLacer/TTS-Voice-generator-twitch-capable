#!/usr/bin/env python3
"""
Windows SDK Installer for TTS Compilation
Automatically downloads and installs Windows 11 SDK
"""
import os
import subprocess
import sys
from pathlib import Path
import ctypes
import tempfile

def try_winget_install():
    """Try to install via winget"""
    try:
        print("[*] Tentando instalar via winget...")
        result = subprocess.run(
            "winget install --id Microsoft.WindowsSDK --version=11.0",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[✓] Windows SDK instalado via winget")
            return True
    except:
        pass
    
    return False

def install_via_chocolatey():
    """Try to install via Chocolatey"""
    try:
        print("[*] Tentando instalar via Chocolatey...")
        result = subprocess.run(
            "choco install windows-sdk-10.1 -y",
            shell=True,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print("[✓] Windows SDK instalado via Chocolatey")
            return True
    except:
        pass
    
    return False

def is_admin():
    """Return True if running with admin privileges (Windows)"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def try_vs_buildtools_install():
    """Download and run Visual Studio Build Tools installer silently (requires admin)."""
    # vs_BuildTools official aka.ms link (Visual Studio 2022 Build Tools)
    vs_url = "https://aka.ms/vs/17/release/vs_BuildTools.exe"
    # Temporary path
    tmp_dir = tempfile.gettempdir()
    installer_path = os.path.join(tmp_dir, 'vs_BuildTools.exe')
    # If not admin, ask to elevate and re-run the script as admin
    if not is_admin():
        print('[!] É necessário executar como Administrador para instalar o Visual Studio Build Tools')
        response = input('Tentar reexecutar este script com privilégios elevados agora? (s/n): ').strip().lower()
        if response == 's':
            # Launch the current Python executable with the script as admin
            script_path = Path(__file__).absolute()
            py_exec = sys.executable
            elevate_cmd = (
                f'powershell -Command "Start-Process -FilePath \"{py_exec}\" ' \
                f'-ArgumentList \"{script_path}\" -Verb RunAs"'
            )
            try:
                subprocess.run(elevate_cmd, shell=True)
                print('[i] Janela elevadora iniciada; aguarde a finalização da instalação')
                return True
            except Exception as e:
                print(f'[!] Falha ao tentar elevar: {e}')
                return False
        return False
    try:
        print('[*] Baixando Visual Studio Build Tools...')
        cmd = f'powershell -Command "Invoke-WebRequest -Uri \"{vs_url}\" -OutFile \"{installer_path}\" -UseBasicParsing"'
        r = subprocess.run(cmd, shell=True)
        if r.returncode != 0 or not Path(installer_path).exists():
            print('[!] Falha ao baixar vs_BuildTools.exe')
            return False

        print('[*] Executando instalador do Build Tools (C++ workload)')
        # Workload ID for C++ build tools
        workload = 'Microsoft.VisualStudio.Workload.VCTools'
        install_cmd = f'"{installer_path}" --add {workload} --includeRecommended --quiet --wait --norestart'
        r2 = subprocess.run(install_cmd, shell=True)
        if r2.returncode == 0:
            print('[✓] Visual Studio Build Tools instalado com sucesso')
            return True
        else:
            print('[!] Falha ao executar instalador do Build Tools')
            return False
    except Exception as e:
        print(f'[!] Exceção durante instalação do Build Tools: {e}')
        return False

def manual_install_instructions():
    """Print manual installation instructions"""
    print("\n" + "="*70)
    print("[!] Instalação Automática Falhou")
    print("="*70)
    print("\nPara compilar TTS no Windows, siga estes passos:")
    print("\n1. Instale Visual Studio Build Tools 2022:")
    print("   URL: https://visualstudio.microsoft.com/downloads/")
    print("   - Clique em 'Download'")
    print("   - Execute o instalador")
    print("   - Selecione 'C++ Build Tools'")
    print("   - Clique em 'Install'")
    print("\nOU\n")
    print("2. Instale Windows 11 SDK:")
    print("   URL: https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
    print("   - Clique em 'Download'")
    print("   - Execute o instalador")
    print("   - Selecione as opções de SDK")
    print("   - Clique em 'Install'")
    print("\nDepois execute novamente:")
    print("   python start.py install")
    print("="*70 + "\n")

def main():
    print("[*] Instalando Windows SDK para compilação TTS...")
    print()
    
    # Try automated installation methods
    if try_winget_install():
        return 0
    
    if install_via_chocolatey():
        return 0

    # Try downloading and running Visual Studio Build Tools installer
    if try_vs_buildtools_install():
        return 0
    
    # Show manual instructions if automatic methods fail
    manual_install_instructions()
    
    print("Abrir página de download? (s/n): ", end="")
    response = input().strip().lower()
    
    if response == 's':
        import webbrowser
        webbrowser.open("https://visualstudio.microsoft.com/downloads/")
        print("\n[*] Página aberta no navegador padrão")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
