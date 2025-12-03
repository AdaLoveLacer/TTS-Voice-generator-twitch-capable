#!/usr/bin/env python3
"""
Cleanup stuck pip/build processes and venv state
Useful when installation is interrupted or gets stuck
"""
import os
import sys
import shutil
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent
VENV_PATH = BASE_DIR / "venv"
PIP_CACHE = BASE_DIR / ".pip-cache"

def clean_venv_lock_files():
    """Remove lock files that might be causing issues"""
    print("[*] Removendo arquivos de lock do venv...")
    
    lock_files = [
        VENV_PATH / "pyvenv.cfg.lock",
        VENV_PATH / ".venv.lock",
        BASE_DIR / ".pip-cache" / ".lock",
    ]
    
    for lock_file in lock_files:
        if lock_file.exists():
            try:
                lock_file.unlink()
                print(f"[✓] Removido: {lock_file}")
            except Exception as e:
                print(f"[!] Falha ao remover {lock_file}: {e}")

def kill_pip_processes():
    """Kill stuck pip processes"""
    print("[*] Parando processos pip...")
    
    try:
        subprocess.run("taskkill /F /IM python.exe /T", shell=True, capture_output=True)
        subprocess.run("taskkill /F /IM pip.exe /T", shell=True, capture_output=True)
        print("[✓] Processos pip parados")
    except Exception as e:
        print(f"[!] Erro ao parar pip: {e}")

def clean_pip_cache():
    """Clear pip cache to avoid corruption"""
    print("[*] Limpando cache pip...")
    
    if PIP_CACHE.exists():
        try:
            # Keep the directory but clear contents
            for item in PIP_CACHE.iterdir():
                if item.is_dir():
                    shutil.rmtree(item, ignore_errors=True)
                else:
                    item.unlink(missing_ok=True)
            print(f"[✓] Cache pip limpo")
        except Exception as e:
            print(f"[!] Erro ao limpar cache: {e}")

def clean_venv():
    """Remove and recreate clean venv"""
    print("[*] Removendo venv corrompido...")
    
    if VENV_PATH.exists():
        try:
            shutil.rmtree(VENV_PATH, ignore_errors=True)
            print("[✓] Venv removido")
        except Exception as e:
            print(f"[!] Erro ao remover venv: {e}")

def main():
    print("")
    print("="*70)
    print("XTTS Server - Limpeza de Processos Travados")
    print("="*70)
    print("")
    
    # Kill processes
    kill_pip_processes()
    
    # Clean lock files
    clean_venv_lock_files()
    
    # Ask if user wants full cleanup
    print("")
    response = input("Deseja limpar o cache pip completamente? (s/n): ").strip().lower()
    if response == 's':
        clean_pip_cache()
    
    response = input("Deseja remover e reconstruir o venv? (s/n): ").strip().lower()
    if response == 's':
        clean_venv()
    
    print("")
    print("="*70)
    print("[✓] Limpeza concluída")
    print("="*70)
    print("")
    print("Próximas ações:")
    print("  1. Feche o VS Code")
    print("  2. Abra um novo terminal PowerShell")
    print("  3. Execute: py -3.11 start.py install")
    print("")

if __name__ == "__main__":
    main()
