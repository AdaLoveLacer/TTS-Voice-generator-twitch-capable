# Scripts Linux para TTS Voice Generator

Este diretório contém equivalentes em shell script (bash) dos scripts PowerShell e BAT originais criados para Windows.

## Scripts Disponíveis

### 1. `cleanup-git-cache.sh`
**Equivalente a:** `cleanup-git-cache.ps1`

Remove arquivos de cache do repositório git (venv, logs, build artifacts, etc).

```bash
chmod +x cleanup-git-cache.sh
./cleanup-git-cache.sh
```

**O que faz:**
- Lista arquivos que serão removidos
- Pede confirmação
- Remove arquivos do git cache
- Oferece opção de fazer commit automático

---

### 2. `install-deps-verbose.sh`
**Equivalente a:** `install-deps-verbose.bat`

Instala as dependências Python com output verboso e cache local.

```bash
chmod +x install-deps-verbose.sh
./install-deps-verbose.sh
```

**Requisitos:**
- Virtual environment já criado em `./venv`

**O que faz:**
- Ativa o virtual environment
- Instala dependências com output verboso (-vv)
- Usa cache local em `.pip_cache`

---

### 3. `stop-build-processes.sh`
**Equivalente a:** `stop-build-processes.ps1`

Para forcadamente todos os processos de compilação/Python que podem estar travados.

```bash
chmod +x stop-build-processes.sh
./stop-build-processes.sh
```

**O que faz:**
- Identifica processos python, pip, gcc, g++, etc
- Mata os processos com SIGKILL
- Recomenda próximos passos

---

### 4. `diagnose-cpu.sh`
**Equivalente a:** `diagnose-cpu.ps1`

Diagnostica processos que consomem alto CPU e oferece opção de terminá-los.

```bash
chmod +x diagnose-cpu.sh
./diagnose-cpu.sh
```

**O que faz:**
- Lista top 10 processos por CPU
- Procura processos problemáticos (python, gcc, etc)
- Oferece opção de terminar
- Fornece recomendações

---

### 5. `diagnose-sdk.sh`
**Equivalente a:** `diagnose-sdk.ps1`

Diagnostica status da instalação de compiladores e SDK.

```bash
chmod +x diagnose-sdk.sh
./diagnose-sdk.sh
```

**O que verifica:**
- GCC/Clang disponível
- Make instalado
- Headers de desenvolvimento
- Python dev files
- Gerenciadores de pacotes

---

### 6. `install-sdk-robust.sh`
**Equivalente a:** `install-sdk-robust.ps1`

Instala automaticamente build-essential e dependências necessárias.

```bash
chmod +x install-sdk-robust.sh
./install-sdk-robust.sh
```

**Suporta:**
- Debian/Ubuntu (apt)
- Fedora (dnf)
- Arch/Manjaro (pacman)
- CentOS/RHEL (yum)

**O que faz:**
- Detecta a distribuição Linux
- Instala build-essential automaticamente
- Verifica a instalação ao final

---

### 7. `create-release-advanced.sh`
**Equivalente a:** `create-release-advanced.ps1`

Cria e compacta releases do projeto em diferentes formatos.

```bash
chmod +x create-release-advanced.sh
./create-release-advanced.sh
```

**Opções:**
1. Criar release simples (pasta)
2. Criar e compactar em TAR.GZ
3. Criar e compactar em ZIP
4. Criar ambos (TAR.GZ + ZIP)
5. Sair

**O que copia:**
- Arquivos principais (README, requirements.txt)
- Servidor (main.py, web_ui.html, etc)
- Engines (base_engine.py, xtts_engine.py, stylets2_engine.py)
- Vozes customizadas
- Metadata

---

## Como Usar

### Configuração Inicial

1. **Tornar scripts executáveis:**
   ```bash
   cd scripts-linux
   chmod +x *.sh
   ```

2. **Ou de uma vez:**
   ```bash
   chmod +x /path/to/scripts-linux/*.sh
   ```

### Uso Típico

**Para instalar dependências:**
```bash
./scripts-linux/install-sdk-robust.sh    # Instalar SDK (uma única vez)
./scripts-linux/install-deps-verbose.sh  # Instalar Python deps
```

**Para diagnosticar problemas:**
```bash
./scripts-linux/diagnose-sdk.sh   # Verificar compiladores
./scripts-linux/diagnose-cpu.sh   # Verificar processos
```

**Para limpeza:**
```bash
./scripts-linux/stop-build-processes.sh  # Matar processos travados
./scripts-linux/cleanup-git-cache.sh     # Limpar cache git
```

**Para criar release:**
```bash
./scripts-linux/create-release-advanced.sh
```

---

## Notas Importantes

### Diferenças entre Windows e Linux

| Aspecto | Windows | Linux |
|--------|---------|-------|
| **Compilador** | MSVC (Visual Studio Build Tools) | GCC/Clang |
| **SDK** | Windows SDK | build-essential |
| **Gerenciador pacotes** | winget/chocolatey | apt/dnf/pacman/yum |
| **Estrutura caminhos** | `\` | `/` |
| **Variáveis env** | Permanentes | Sessão |
| **Permissões exec** | Automáticas | chmod +x |

### Requisitos de Sistema

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install build-essential python3-dev python3-pip
```

**Fedora:**
```bash
sudo dnf groupinstall "Development Tools"
sudo dnf install python3-devel
```

**Arch/Manjaro:**
```bash
sudo pacman -S base-devel python
```

**macOS:**
```bash
xcode-select --install
brew install python3
```

---

## Troubleshooting

### "Permission denied"
```bash
chmod +x scripts-linux/*.sh
```

### "Command not found: python3"
```bash
sudo apt install python3  # Debian/Ubuntu
sudo dnf install python3  # Fedora
```

### "pip: command not found"
```bash
python3 -m pip install --upgrade pip
```

### Venv não ativado
Certifique-se que o venv existe:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Contribuindo

Se encontrar problemas ou tiver sugestões de melhorias, abra uma issue ou PR com:
- Sistema operacional e distribuição
- Output do erro
- Passos para reproduzir

---

## Licença

Os scripts seguem a mesma licença do projeto principal.
