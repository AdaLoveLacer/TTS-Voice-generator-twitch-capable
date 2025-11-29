# Linux/macOS Setup Guide

Guia completo de setup para Linux e macOS.

## 📝 Scripts Disponíveis

### `start-server.sh`
Script principal para iniciar o servidor em Linux/macOS.

**Recursos:**
- ✅ Cria virtual environment se não existir
- ✅ Ativa venv automaticamente
- ✅ Menu CUDA simples (sim/não)
- ✅ Instala dependências via pip
- ✅ Inicia o servidor (main.py abre navegador)
- ✅ Cache local em `.pip-cache`

**Uso:**
```bash
chmod +x start-server.sh
./start-server.sh
```

### `start-server-auto.sh`
Versão automática (responde "Não" ao menu CUDA).

```bash
chmod +x start-server-auto.sh
./start-server-auto.sh
```

### `install-cuda.sh`
Instala/reinstala CUDA 11.8.

```bash
chmod +x install-cuda.sh
./install-cuda.sh
```

---

## 🔄 Windows ↔ Linux/macOS

| Feature | Windows | Linux/macOS |
|---------|---------|-------------|
| Setup | `start-server.bat` | `start-server.sh` |
| Auto | `start-server-auto.bat` | `start-server-auto.sh` |
| CUDA | `install-cuda.bat` | `install-cuda.sh` |

---

## ⚙️ Instalação Inicial

```bash
cd xtts-server

# Dar permissão executável
chmod +x *.sh

# Executar
./start-server.sh
```

---

## 🐧 Compatibilidade

- ✅ Ubuntu 20.04+
- ✅ Debian 11+
- ✅ macOS 10.14+ (Mojave+)
- ✅ Fedora 35+
- ✅ CentOS 8+

**Requisitos:**
- Python 3.10+
- bash 4.0+
- pip3

---

## 🔧 Troubleshooting

### "Permission denied"
```bash
chmod +x *.sh
```

### Python não encontrado
```bash
python3 --version
# ou
python --version

# Instalar: https://www.python.org/downloads/
```

### CUDA indisponível
Se tem GPU NVIDIA:
```bash
./install-cuda.sh
```

### Erro ao ativar venv
```bash
rm -rf venv
./start-server.sh
```

---

## 📝 Notas

1. Scripts `.sh` e `.bat` fazem exatamente a mesma coisa
2. Cache centralizado em `.pip-cache/`
3. Menu CUDA idêntico em funcionalidade
4. Navegador abre automaticamente
5. Todos os scripts devem estar executáveis

---

**Pronto?** → [Quick Start](../QUICK_START.md)
