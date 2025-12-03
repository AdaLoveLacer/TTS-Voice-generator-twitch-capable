#!/usr/bin/env python3
"""
XTTS Server Launcher - Robust Setup com Auto-Config MSVC
- Auto-detecta Visual Studio em F: drive
- Verifica venv continuamente
- Cache local apenas
- Limpeza/verificação de bibliotecas
"""
import os
import tempfile
import sys
import io
import subprocess
import shutil
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)
if hasattr(sys, 'stdin') and sys.stdin.encoding != 'utf-8':
    sys.stdin = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8')

BASE_DIR = Path(__file__).parent
VENV_PATH = BASE_DIR / "venv"
PIP_CACHE = BASE_DIR / ".pip-cache"
PYTHON_EXE = VENV_PATH / "Scripts" / "python.exe" if os.name == 'nt' else VENV_PATH / "bin" / "python"
PY_LAUNCHER = "py -3.11"

def get_skip_tts_flag():
    """Detect if we should skip TTS build via env var or --skip-tts flag"""
    if os.environ.get('XTTS_SKIP_TTS', '') == '1':
        return True
    if any(arg in ['--skip-tts', '--no-tts'] for arg in sys.argv):
        return True
    return False

def find_msvc():
    """Find MSVC compiler in system (preferring F: drive)"""
    possible_paths = [
        "F:/C++/dev/VC/Tools/MSVC",
        "F:/Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC",
        "F:/Program Files/Microsoft Visual Studio/2022/Community/VC/Tools/MSVC",
        "C:/Program Files/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC",
        "C:/Program Files (x86)/Microsoft Visual Studio/2022/BuildTools/VC/Tools/MSVC",
    ]
    
    for path in possible_paths:
        p = Path(path)
        if p.exists():
            versions = sorted([d for d in p.iterdir() if d.is_dir()], reverse=True)
            if versions:
                return versions[0]
    return None

def setup_msvc():
    """Configure MSVC environment for C++ compilation (TTS)"""
    msvc_path = find_msvc()
    if not msvc_path:
        print("[!] MSVC não encontrado - TTS pode falhar ao compilar")
        return False
    
    try:
        print(f"[✓] Encontrado MSVC em: {msvc_path.parent.parent.parent}")
        
        # Try to use vcvars64.bat for complete environment setup
        # Note: "Build" directory is capitalized!
        vcvars_path = msvc_path.parent.parent / "Auxiliary" / "Build" / "vcvars64.bat"
        if vcvars_path.exists():
            print(f"[✓] Usando vcvars64.bat para configuração completa")
            # Execute vcvars64.bat and capture environment
            cmd = f'cmd.exe /c "{vcvars_path}" && set'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                # Parse the output and set environment variables
                for line in result.stdout.split('\n'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                print(f"[✓] Ambiente MSVC ativado via vcvars64.bat")
                return True
        
        # Fallback: Manual environment setup if vcvars doesn't work
        print(f"[i] vcvars64.bat não disponível, configurando manualmente")
        
        # Set include paths (MSVC + Auxiliary)
        include_path = msvc_path / "include"
        auxiliary_include = msvc_path.parent.parent / "Auxiliary" / "VS" / "include"
        
        include_paths = []
        if include_path.exists():
            include_paths.append(str(include_path))
        if auxiliary_include.exists():
            include_paths.append(str(auxiliary_include))
        if include_paths:
            # Prepend to existing INCLUDE to override system includes
            existing_include = os.environ.get('INCLUDE', '')
            os.environ['INCLUDE'] = os.pathsep.join(include_paths)
            if existing_include:
                os.environ['INCLUDE'] += os.pathsep + existing_include
        
        # Set lib paths for x64
        lib_path = msvc_path / "lib" / "x64"
        if lib_path.exists():
            os.environ['LIB'] = str(lib_path) + os.pathsep + os.environ.get('LIB', '')
        
        # CRITICAL: Set compiler path - MUST be Hostx64/x64 for 64-bit Python
        bin_path = msvc_path / "bin" / "Hostx64" / "x64"
        if bin_path.exists():
            # Prepend MSVC bin to PATH to ensure it's used instead of HostX86
            existing_path = os.environ.get('PATH', '')
            os.environ['PATH'] = str(bin_path) + os.pathsep + existing_path
            print(f"[✓] MSVC compilador ativado (Hostx64/x64)")
            return True
        else:
            print("[!] Nenhum binário MSVC encontrado nos caminhos esperados")
            return False
        
    except Exception as e:
        print(f"[!] Erro ao configurar MSVC: {e}")
        return False
    

def run(cmd, check=True):
    """Execute command with output"""
    print(f"[cmd] {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print(f"[X] Erro ao executar: {cmd}")
        sys.exit(1)
    return result.returncode == 0

def run_with_env(cmd, check=True):
    """Execute command with inherited environment (for MSVC vars)"""
    print(f"[cmd] {cmd}")
    # Use current environment which has MSVC vars set
    result = subprocess.run(cmd, shell=True, env=os.environ.copy())
    if check and result.returncode != 0:
        print(f"[X] Erro ao executar: {cmd}")
        sys.exit(1)
    return result.returncode == 0

def ensure_pip_cache():
    """Ensure pip cache directory exists"""
    PIP_CACHE.mkdir(exist_ok=True)
    return PIP_CACHE

def check_venv():
    """Check if venv exists and is valid"""
    if not VENV_PATH.exists():
        return False
    if not PYTHON_EXE.exists():
        return False
    # Check pyvenv.cfg exists
    pyvenv_cfg = VENV_PATH / "pyvenv.cfg"
    if not pyvenv_cfg.exists():
        return False
    return True

def create_venv():
    """Create virtual environment"""
    if check_venv():
        print(f"[✓] venv válida encontrada: {VENV_PATH}")
        return True
    
    print("[*] venv não encontrada ou corrompida")
    print("[*] Criando venv...")
    
    # Remove old venv if exists
    if VENV_PATH.exists():
        print("[*] Removendo venv antiga...")
        shutil.rmtree(VENV_PATH, ignore_errors=True)
    
    # Try to use Python 3.11 if available (CRITICAL: Python 3.13 has pkgutil.ImpImporter issue)
    python_cmd = sys.executable
    using_py311 = False
    
    try:
        # Prefer using the py 3.11 launcher
        result = subprocess.run(f"{PY_LAUNCHER} --version", shell=True, capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("[i] Python 3.11 encontrado, usando via py launcher...")
            python_cmd = PY_LAUNCHER
            using_py311 = True
    except:
        pass
    
    if not using_py311:
        print("[!] Python 3.11 não encontrado, usando versão do sistema (pode falhar)")
        print("[!] Instale Python 3.11 de: https://www.python.org/downloads/")
    
    if not run(f"{python_cmd} -m venv {VENV_PATH}"):
        print("[X] Falha ao criar venv")
        return False
    
    if not check_venv():
        print("[X] venv criada mas inválida")
        return False
    
    print("[✓] venv criada com sucesso\n")
    return True

def parse_requirements():
    """Parse requirements.txt and return dict of {package_name: version_spec}"""
    req_file = BASE_DIR / 'requirements.txt'
    requirements = {}
    
    if not req_file.exists():
        return requirements
    
    try:
        with open(req_file, 'r', encoding='utf8') as f:
            for line in f:
                line = line.strip()
                # Skip comments and blank lines
                if not line or line.startswith('#'):
                    continue
                # Skip index URLs
                if line.startswith('--'):
                    continue
                # Parse package name and version
                # Handle formats: package, package==1.0, package>=1.0, package[extra]==1.0
                if '==' in line or '>=' in line or '<=' in line or '>' in line or '<' in line:
                    pkg_name = line.split('[')[0].split('=')[0].split('>')[0].split('<')[0].strip()
                else:
                    pkg_name = line.split('[')[0].strip()
                
                if pkg_name:
                    requirements[pkg_name.lower()] = line
    except Exception as e:
        print(f"[!] Erro ao ler requirements.txt: {e}")
    
    return requirements

def get_installed_packages():
    """Get list of installed packages in venv"""
    try:
        result = subprocess.run(
            f'{PYTHON_EXE} -m pip list --format json',
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            import json
            packages = json.loads(result.stdout)
            return {pkg['name'].lower(): pkg['version'] for pkg in packages}
    except Exception as e:
        print(f"[!] Erro ao obter lista de pacotes: {e}")
    return {}

def verify_libs():
    """Verify and auto-install missing libraries"""
    print("[*] Verificando bibliotecas...")
    print()
    
    # Get requirements
    requirements = parse_requirements()
    if not requirements:
        print("[!] Nenhum requirements.txt encontrado")
        return False
    
    # Get installed packages
    installed = get_installed_packages()
    
    # Compare
    missing = []
    installed_count = 0
    
    print(f"[*] Comparando {len(requirements)} dependências...")
    print()
    
    for pkg_name, pkg_spec in requirements.items():
        if pkg_name in installed:
            print(f"[✓] {pkg_name} ({installed[pkg_name]})")
            installed_count += 1
        else:
            print(f"[!] {pkg_name} - NÃO INSTALADO")
            missing.append(pkg_spec)
    
    print()
    print("="*70)
    print(f"Resumo: {installed_count}/{len(requirements)} dependências instaladas")
    print("="*70)
    
    # Check TTS status
    if is_tts_installed():
        print('[✓] TTS está instalado')
    else:
        print('[!] TTS não está instalado (use: py -3.11 start.py install-tts)')
    
    # Check StyleTTS2
    try:
        res = subprocess.run(f'{PYTHON_EXE} -m pip show StyleTTS2', shell=True, capture_output=True, text=True)
        if res.returncode == 0 and 'Name: StyleTTS2' in res.stdout:
            print('[✓] StyleTTS2 está instalado')
        else:
            print('[i] StyleTTS2 não instalado (opcional: py -3.11 start.py install-styletts2)')
    except Exception:
        pass
    
    print()
    
    # Auto-install missing packages
    if missing:
        print(f"[!] {len(missing)} dependência(s) faltando!")
        print()
        response = input("Deseja instalar automaticamente as dependências faltantes? (s/n): ").strip().lower()
        
        if response == 's':
            cache = ensure_pip_cache()
            print()
            print("[*] Instalando dependências faltantes...")
            
            for pkg_spec in missing:
                print(f"    Instalando: {pkg_spec}")
                cmd = f'{PYTHON_EXE} -m pip install --cache-dir "{cache}" "{pkg_spec}"'
                if not run_with_env(cmd, check=False):
                    print(f"    [!] Falha ao instalar {pkg_spec}")
                else:
                    print(f"    [✓] Instalado com sucesso")
            
            print()
            print("[*] Verificação final...")
            
            # Re-check after install
            installed_after = get_installed_packages()
            still_missing = []
            for pkg_name in missing:
                pkg_base = pkg_name.split('[')[0].split('=')[0].split('>')[0].split('<')[0].strip().lower()
                if pkg_base not in installed_after:
                    still_missing.append(pkg_name)
            
            if still_missing:
                print(f"[!] {len(still_missing)} pacote(s) ainda não instalado(s):")
                for pkg in still_missing:
                    print(f"    - {pkg}")
                print()
                print("[i] Tente instalar manualmente ou use:")
                print(f"    py -3.11 -m pip install {still_missing[0].split('=')[0]}")
                return False
            else:
                print("[✓] Todas as dependências instaladas com sucesso!")
                return True
        else:
            print("[i] Instalação cancelada pelo usuário")
            return False
    else:
        print("[✓] Todas as dependências estão instaladas!")
        return True

def verify_libs_simple():
    """Simple verification - just list installed packages"""
    print("[*] Listando bibliotecas instaladas...")
    if not run(f"{PYTHON_EXE} -m pip list", check=False):
        return False
    print()
    return True

def is_tts_installed():
    """Return True if TTS is installed in the venv (pip show)"""
    try:
        res = subprocess.run(f'{PYTHON_EXE} -m pip show TTS', shell=True, capture_output=True, text=True)
        return res.returncode == 0 and 'Name: TTS' in res.stdout
    except Exception:
        return False

def install_tts_only():
    """Install only the TTS package using the configured venv and MSVC environment."""
    if not check_venv():
        print("[!] venv não encontrado. Deseja criar agora? (s/n): ", end='')
        choice = input().strip().lower()
        if choice == 's':
            if not create_venv():
                print('[X] Falha ao criar venv')
                return False
        else:
            print('[i] Cancelado: venv é necessário para instalar TTS')
            return False

    # Ensure MSVC environment
    setup_msvc()
    # Check for SDK headers
    sdk_ok = check_windows_sdk() or io_header_exists()
    if not sdk_ok:
        print('[!] Windows SDK não detectado — TTS pode falhar se SDK estiver ausente')
        if not prompt_install_sdk():
            print('[X] Instalação do TTS cancelada (SDK é necessário para compilar)')
            return False
        sdk_ok = check_windows_sdk() or io_header_exists()
        if not sdk_ok:
            print('[X] SDK ainda não localizado — cancele ou instale manualmente e tente novamente')
            return False

    force = '--force' in sys.argv or '--reinstall' in sys.argv
    no_build_isolation = '--no-build-isolation' in sys.argv
    if is_tts_installed() and not force:
        print('[✓] TTS já instalado. Para reinstalar use --force')
        return True

    cache = ensure_pip_cache()
    cmd = f'{PYTHON_EXE} -m pip install --cache-dir "{cache}" "TTS>=0.22.0"'
    if no_build_isolation:
        cmd += ' --no-build-isolation'
    # Use run_with_env to ensure MSVC env propagates to pip builds
    print('[*] Instalando TTS...')
    success = run_with_env(cmd, check=False)
    if not success:
        print('[X] Falha ao instalar TTS. Tente instalar manualmente após instalar SDK.')
        return False
    print('[✓] TTS instalado com sucesso')
    return True

def install_styletts2_only():
    """Install only StyleTTS2 package (optional TTS engine)."""
    if not check_venv():
        print("[!] venv não encontrado. Execute primeiro: py -3.11 start.py install")
        return False

    force = '--force' in sys.argv or '--reinstall' in sys.argv
    
    # Check if already installed
    try:
        res = subprocess.run(f'{PYTHON_EXE} -m pip show StyleTTS2', shell=True, capture_output=True, text=True)
        if res.returncode == 0 and 'Name: StyleTTS2' in res.stdout and not force:
            print('[✓] StyleTTS2 já instalado. Para reinstalar use --force')
            return True
    except Exception:
        pass

    cache = ensure_pip_cache()
    cmd = f'{PYTHON_EXE} -m pip install --cache-dir "{cache}" "StyleTTS2>=0.2.0"'
    
    print('[*] Instalando StyleTTS2 (motor TTS alternativo)...')
    success = run_with_env(cmd, check=False)
    if not success:
        print('[X] Falha ao instalar StyleTTS2')
        return False
    print('[✓] StyleTTS2 instalado com sucesso')
    return True

def check_windows_sdk():
    """Check if Windows SDK is installed (required for TTS compilation)"""
    # Common Windows SDK locations
    possible_paths = [
        r"C:\Program Files (x86)\Windows Kits\10",
        r"C:\Program Files (x86)\Windows Kits\11",
        r"D:\Windows Kits\10",
        r"D:\Windows Kits\11",
        r"F:\Windows Kits\10",
        r"F:\Windows Kits\11",
    ]
    
    for path in possible_paths:
        include_dir = Path(path) / "Include"
        if include_dir.exists():
            return True
    # Check environment variables (vcvars64 may set INCLUDE to Windows Kits)
    include_env = os.environ.get('INCLUDE', '')
    if 'Windows Kits' in include_env or 'Windows\\ Kits' in include_env or 'Kits' in include_env:
        return True
    return False

def io_header_exists():
    """Check if io.h exists in any INCLUDE path (quick SDK presence check)"""
    include_env = os.environ.get('INCLUDE', '')
    if not include_env:
        return False
    for p in include_env.split(os.pathsep):
        try:
            if Path(p).exists():
                if (Path(p) / 'io.h').exists():
                    return True
                # sometimes headers are in subdirs with versioning
                for sub in Path(p).iterdir():
                    if (sub / 'io.h').exists():
                        return True
        except Exception:
            continue
    return False

def prompt_install_sdk():
    """Prompt user to install Windows SDK if missing"""
    print("\n" + "="*70)
    print("[!] Windows SDK não encontrado")
    print("="*70)
    print("\nPara compilar TTS (required para TTS>=0.22.0) no Windows,")
    print("é necessário instalar o Windows 11 SDK ou Visual Studio Build Tools")
    print("\nOpções:")
    print("  1. Instale Visual Studio Build Tools 2022:")
    print("     https://visualstudio.microsoft.com/downloads/")
    print("     (Selecione 'C++ Build Tools')")
    print("\n  2. Ou instale Windows 11 SDK:")
    print("     https://developer.microsoft.com/en-us/windows/downloads/windows-sdk/")
    print("\nDepois, execute novamente:")
    print("  python start.py install")
    print("="*70 + "\n")
    
    print("Opções de instalação automática:")
    print("  w = Winget (se disponível)")
    print("  c = Chocolatey (se disponível)")
    print("  b = Usar script local (install-sdk.py) para tentar várias opções (recomendado)")
    response = input("Escolha (w/c/b/n): ").strip().lower()
    if response == 'w':
        print("[*] Tentando instalar Windows 11 SDK via winget...")
        result = subprocess.run("winget install --id Microsoft.WindowsSDK --version=11.0", shell=True)
        if result.returncode == 0:
            print("[✓] Windows SDK instalado!")
            return True
        else:
            print("[!] Instalação via winget falhou. Instale manualmente.")
            return False
    if response == 'c':
        print("[*] Tentando instalar Windows SDK via Chocolatey...")
        result = subprocess.run("choco install windows-sdk-10.1 -y", shell=True)
        if result.returncode == 0:
            print("[✓] Windows SDK instalado via Chocolatey!")
            return True
        else:
            print("[!] Instalação via Chocolatey falhou. Instale manualmente.")
            return False
    if response == 'b':
        # run the bundled install-sdk.py which supports winget/choco/vs installer
        script = BASE_DIR / 'install-sdk.py'
        if not script.exists():
            print('[!] Script install-sdk.py não encontrado no diretório.')
            return False
        print('[*] Executando script local install-sdk.py (pode solicitar privilégios)...')
        cmd = f'{PY_LAUNCHER} "{script}"'
        return run_with_env(cmd, check=False)
    return False
    return False

def install_deps():
    """Install dependencies with local cache"""
    cache = ensure_pip_cache()
    
    # Setup MSVC environment variables (if available)
    setup_msvc()

    # Determine whether to skip TTS (by flag or if Windows SDK missing)
    skip_tts = get_skip_tts_flag()
    sdk_ok = check_windows_sdk() or io_header_exists()
    if not sdk_ok and not skip_tts:
        print("[!] Windows SDK não detectado e TTS é parte do requirements")
        if prompt_install_sdk():
            # If user attempts install, re-evaluate SDK presence
            sdk_ok = check_windows_sdk() or io_header_exists()
        else:
            # If the user declines or install fails, offer to continue without TTS
            print("[i] Prosseguindo sem TTS (skipping TTS-related packages)")
            skip_tts = True
    
    # CRITICAL: Set additional environment variables for distutils/setuptools
    # These help ensure the correct compiler is found
    os.environ['DISTUTILS_USE_SDK'] = '1'
    os.environ['MSSdk'] = '1'
    
    # Try to locate Windows SDK as well (for headers)
    # Priority: C:\Program Files (x86)\Windows Kits\11, C:\Program Files (x86)\Windows Kits\10
    for sdk_version in ['11', '10']:
        sdk_path_list = [
            f'C:\\Program Files (x86)\\Windows Kits\\{sdk_version}',
            f'C:\\Program Files\\Windows Kits\\{sdk_version}',
            f'D:\\Program Files (x86)\\Windows Kits\\{sdk_version}',
            f'F:\\Windows Kits\\{sdk_version}',
        ]
        for sdk_path in sdk_path_list:
            if Path(sdk_path).exists():
                sdk_include = Path(sdk_path) / 'Include'
                if sdk_include.exists():
                    # Add Windows SDK includes to INCLUDE
                    os.environ['INCLUDE'] = str(sdk_include) + os.pathsep + os.environ.get('INCLUDE', '')
                    print(f"[✓] Windows SDK encontrado em: {sdk_path}")
                    break
        else:
            continue
        break
    
    print("\n[*] Instalando dependências (com cache local)...")
    print(f"[i] Cache em: {cache}\n")
    
    print("[*] Etapa 1: pip/setuptools/wheel...")
    pip_cmd = f'{PYTHON_EXE} -m pip install --upgrade pip setuptools wheel --cache-dir "{cache}" --no-index --find-links "{cache}" 2>nul || {PYTHON_EXE} -m pip install --upgrade pip setuptools wheel --cache-dir "{cache}"'
    if not run_with_env(pip_cmd, check=False):
        print("[!] Aviso: pip update teve problemas")
    print("[✓] OK\n")
    
    print("[*] Etapa 2: requirements.txt...")
    print("[*] Isso pode levar 15-30 minutos (primeira vez)...\n")
    # If we should skip TTS, produce a temp requirements file without TTS
    if skip_tts:
        req_path = BASE_DIR / 'requirements.txt'
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.txt', prefix='req-no-tts-', dir=str(BASE_DIR))
        with open(req_path, 'r', encoding='utf8') as inf, open(tmp.name, 'w', encoding='utf8') as outf:
            for line in inf:
                # Keep comments, blank lines, but drop TTS entries
                stripped = line.strip()
                if stripped.startswith('#') or stripped == '':
                    outf.write(line)
                    continue
                # If the line includes 'TTS' as package name, skip
                if stripped.startswith('TTS') or stripped.startswith('TTS>=') or 'TTS' in stripped.split()[0]:
                    print(f"[i] Removendo linha TTS do requirements: {stripped}")
                    continue
                outf.write(line)
        requirements_cmd = f'{PYTHON_EXE} -m pip install --cache-dir "{cache}" -r "{tmp.name}"'
    else:
        requirements_cmd = f'{PYTHON_EXE} -m pip install --cache-dir "{cache}" -r "{BASE_DIR}/requirements.txt"'
    result = run_with_env(requirements_cmd, check=False)
    
    if not result:
        print("\n[!] Falha ao instalar requirements")
        print("[*] Tentando novamente...")
        result = run_with_env(requirements_cmd, check=False)
        if not result:
            print("[X] Falha persiste")
            return False
    # Cleanup temp file if it exists
    try:
        if 'tmp' in locals() and Path(tmp.name).exists():
            Path(tmp.name).unlink()
    except Exception:
        pass
    
    print("[✓] OK\n")
    return True

def clean_all():
    """Clean venv, cache and reinstall"""
    print("[*] Limpeza completa...")
    print("[*] Removendo venv...")
    shutil.rmtree(VENV_PATH, ignore_errors=True)
    print("[*] Removendo cache pip...")
    shutil.rmtree(PIP_CACHE, ignore_errors=True)
    print("[✓] Limpeza concluída\n")

def start_server():
    """Start the server"""
    if not check_venv():
        print("[X] venv não existe. Execute: python start.py install")
        sys.exit(1)
    
    print("[*] Iniciando XTTS Server...\n")
    print("    http://localhost:8000")
    print("    http://localhost:8000/docs\n")
    os.chdir(BASE_DIR)
    run(f"{PYTHON_EXE} main.py", check=False)

def menu():
    """Interactive menu"""
    print("\n" + "="*60)
    print("XTTS Server - Menu")
    print("="*60)
    print(f"venv status: {'✓ OK' if check_venv() else '✗ Não encontrada'}")
    print()
    print("Opções:")
    print("  1 = Instalar (criar venv + deps)")
    print("  2 = Verificar e corrigir bibliotecas")
    print("  3 = Iniciar servidor")
    print("  4 = Limpar e reinstalar")
    print("  5 = Sair")
    print("="*60)
    choice = input("Escolha (1-5): ").strip()
    return choice

def main():
    """Main entry point"""
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    
    if mode is None:
        # Interactive mode
        while True:
            choice = menu()
            if choice == "1":
                if create_venv():
                    install_deps()
            elif choice == "2":
                if check_venv():
                    verify_libs()
                else:
                    print("[X] venv não existe")
            elif choice == "3":
                start_server()
            elif choice == "4":
                clean_all()
                if create_venv():
                    install_deps()
            elif choice == "5":
                print("Saindo...")
                break
            else:
                print("[X] Opção inválida")
    else:
        # CLI mode
        if mode in ["1", "install"]:
            if create_venv():
                install_deps()
        elif mode in ["2", "check"]:
            if check_venv():
                verify_libs()
            else:
                print("[X] venv não existe")
        elif mode in ["3", "server"]:
            start_server()
        elif mode in ["install-tts", "tts-install", "install_tts"]:
            install_tts_only()
        elif mode in ["install-styletts2", "styletts2-install", "install-styletts"]:
            install_styletts2_only()
        elif mode in ["install-sdk", "sdk-install", "install_sdk"]:
            # Run the bundled install-sdk.py to attempt automated installation
            script = BASE_DIR / 'install-sdk.py'
            if script.exists():
                run_with_env(f'{PY_LAUNCHER} "{script}"')
            else:
                print('[!] Script install-sdk.py não encontrado')
        elif mode in ["install-sdk-robust", "sdk-install-robust"]:
            # Run the robust PowerShell installer
            script = BASE_DIR / 'install-sdk-robust.ps1'
            if script.exists():
                run(f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}"')
            else:
                print('[!] Script install-sdk-robust.ps1 não encontrado')
        elif mode in ["diagnose", "diag", "check-sdk"]:
            # Run diagnostic PowerShell script
            script = BASE_DIR / 'diagnose-sdk.ps1'
            if script.exists():
                run(f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}"')
            else:
                print('[!] Script diagnose-sdk.ps1 não encontrado')
        elif mode in ["diagnose-cpu", "diag-cpu", "cpu"]:
            # Run CPU diagnostic
            script = BASE_DIR / 'diagnose-cpu.ps1'
            if script.exists():
                run(f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}"')
            else:
                print('[!] Script diagnose-cpu.ps1 não encontrado')
        elif mode in ["stop-processes", "kill-build", "stop-build"]:
            # Force stop build processes
            script = BASE_DIR / 'stop-build-processes.ps1'
            if script.exists():
                run(f'powershell -NoProfile -ExecutionPolicy Bypass -File "{script}"')
            else:
                print('[!] Script stop-build-processes.ps1 não encontrado')
        elif mode in ["cleanup-stuck", "cleanup-processes"]:
            # Run Python cleanup script
            script = BASE_DIR / 'cleanup-stuck-processes.py'
            if script.exists():
                run(f'{PY_LAUNCHER} "{script}"')
            else:
                print('[!] Script cleanup-stuck-processes.py não encontrado')
        elif mode in ["4", "clean"]:
            clean_all()
            if create_venv():
                install_deps()
        else:
            print("Uso: python start.py [comando]")
            print("  1/install = Instalar")
            print("  2/check   = Verificar e corrigir libs (compara com requirements.txt)")
            print("  3/server  = Iniciar servidor")
            print("  4/clean   = Limpar e reinstalar")
            print("  (vazio)   = Menu interativo")
            print("  install-tts = Instalar somente TTS (requires SDK)")
            print("     use --force para reinstalar e --no-build-isolation se necessário")
            print("  install-styletts2 = Instalar StyleTTS2 (motor TTS alternativo mais rápido)")
            print("  diagnose = Diagnosticar instalação SDK/MSVC")
            print("  install-sdk-robust = Instalar SDK via PowerShell (recomendado)")
            print("  diagnose-cpu = Diagnosticar e parar processos com alto CPU")
            print("  stop-processes = Parar imediatamente todos os processos de build")
            print("  cleanup-stuck = Limpar arquivos de lock e cache corrompido")
            print("  --skip-tts = Alteração global: pular compilação TTS e instalação de dependências TTS")

if __name__ == "__main__":
    main()

