#!/usr/bin/env python3
"""
Setup script to configure MSVC and Windows SDK for TTS compilation
Encontrado em: F:\C++\dev
"""
import os
import subprocess
import sys
from pathlib import Path

# MSVC paths found on F: drive
MSVC_PATH = r"F:\C++\dev"
VCVARS_64 = rf"{MSVC_PATH}\VC\Auxiliary\Build\vcvars64.bat"
MSVC_VERSION = "14.44.35207"  # Latest found
MSVC_INCLUDE = rf"{MSVC_PATH}\VC\Tools\MSVC\{MSVC_VERSION}\include"
MSVC_LIB = rf"{MSVC_PATH}\VC\Tools\MSVC\{MSVC_VERSION}\lib\x64"

def setup_msvc_env():
    """Setup MSVC environment variables"""
    print("[*] Configurando ambiente MSVC...")
    
    # Add MSVC to environment
    os.environ["INCLUDE"] = MSVC_INCLUDE
    os.environ["LIB"] = MSVC_LIB
    os.environ["PATH"] = rf"{MSVC_PATH}\VC\Tools\MSVC\{MSVC_VERSION}\bin\HostX64\x64" + ";" + os.environ.get("PATH", "")
    
    print(f"[✓] INCLUDE: {MSVC_INCLUDE}")
    print(f"[✓] LIB: {MSVC_LIB}")
    print(f"[✓] PATH updated with MSVC")
    
    return True

def activate_vcvars():
    """Try to activate vcvars"""
    if not Path(VCVARS_64).exists():
        print(f"[!] vcvars64.bat não encontrado em {VCVARS_64}")
        return False
    
    print(f"[*] Ativando vcvars64.bat...")
    try:
        result = subprocess.run(f'cmd /c "{VCVARS_64}"', shell=True, capture_output=True, text=True)
        if "Environment initialized" in result.stdout:
            print("[✓] vcvars ativado com sucesso")
            return True
    except Exception as e:
        print(f"[!] Erro ao ativar vcvars: {e}")
    
    return False

def main():
    print("="*70)
    print("MSVC Setup para TTS Compilation")
    print("="*70)
    print(f"\n[i] MSVC encontrado em: {MSVC_PATH}")
    print(f"[i] Versão: {MSVC_VERSION}")
    
    # Setup environment
    setup_msvc_env()
    
    # Try vcvars
    activate_vcvars()
    
    print("\n[✓] Ambiente MSVC configurado!")
    print("\nAgora execute:")
    print("  py -3.11 start.py install")
    print("\nOu se isso não funcionar, tente:")
    print("  pip install TTS --no-build-isolation")

if __name__ == "__main__":
    main()
