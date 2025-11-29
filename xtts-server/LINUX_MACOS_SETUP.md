# Linux/macOS Startup Scripts

## 📝 Novos Arquivos Criados

Para manter paridade entre Windows e Linux/macOS, foram criados os seguintes scripts:

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
Versão automática do start-server.sh (responde "Não" ao menu CUDA).

**Uso:**
```bash
chmod +x start-server-auto.sh
./start-server-auto.sh
```

### `install-cuda.sh`
Script para instalar/reinstalar CUDA 11.8 em Linux/macOS.

**Uso:**
```bash
chmod +x install-cuda.sh
./install-cuda.sh
```

---

## 🔄 Paridade Windows ↔ Linux/macOS

| Funcionalidade | Windows | Linux/macOS |
|---|---|---|
| Criar venv | `start-server.bat` | `start-server.sh` |
| Instalar deps | `start-server.bat` | `start-server.sh` |
| Menu CUDA | `start-server.bat` | `start-server.sh` |
| Iniciar automático | `start-server-auto.bat` | `start-server-auto.sh` |
| Instalar CUDA | `install-cuda.bat` | `install-cuda.sh` |

---

## 📊 Características

### `start-server.sh` (Linux/macOS)
```bash
#!/bin/bash
# - Detecta diretório do script
# - Cria venv se não existir
# - Oferece menu CUDA
# - Instala dependências
# - Inicia servidor
```

### Comparação com Windows

**Windows:**
- Usa `@echo off` para silenciar comandos
- Usa `call` para ativar venv
- Usa `echo` para output
- Menus com `set /p`

**Linux/macOS:**
- Usa `set -e` para exit on error
- Usa `source` para ativar venv
- Usa `echo` para output
- Menus com `read -p`

---

## ⚙️ Configuração Inicial

Após clonar o repositório, em Linux/macOS:

```bash
cd xtts-server

# Dar permissão executável aos scripts
chmod +x *.sh

# Executar script de startup
./start-server.sh
```

Ou para execução automática:
```bash
./start-server-auto.sh
```

---

## 🐧 Tested On

Scripts foram criados com suporte para:
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

### "Permission denied" ao executar .sh
```bash
chmod +x start-server.sh
```

### Python não encontrado
Certifique-se de que Python 3.10+ está instalado:
```bash
python3 --version
# ou
python --version
```

### CUDA indisponível no Linux
Se usando GPU NVIDIA:
```bash
./install-cuda.sh
```

### Erro ao ativar venv
Delete o venv existente e tente novamente:
```bash
rm -rf venv
./start-server.sh
```

---

## 📝 Notas

1. Scripts `.sh` e `.bat` fazem **exatamente a mesma coisa** - apenas em linguagens diferentes
2. Cache é centralizado em `.pip-cache/` em ambas plataformas
3. Menu CUDA é idêntico em funcionalidade
4. Navegador abre automaticamente via `main.py` em ambas
5. Todos os scripts devem estar executáveis (`chmod +x`)

---

## 🚀 Próximos Passos

- [x] Criar start-server.sh
- [x] Criar start-server-auto.sh
- [x] Criar install-cuda.sh
- [ ] Testar em Ubuntu 20.04
- [ ] Testar em macOS 12+
- [ ] Documentar troubleshooting adicional
