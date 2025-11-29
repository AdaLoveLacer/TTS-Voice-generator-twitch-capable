# 🚀 Boas Práticas para Enviar ao GitHub

## ✅ Checklist Final Antes do Push

### 1. Verificação do Repositório Local
```bash
# Estar na pasta correta
cd Speakerbot-local-voice

# Verificar status
git status

# Deve mostrar:
# On branch main
# nothing to commit, working tree clean
```

### 2. Arquivos Configurados
- [x] `.gitignore` - Exclui venv, __pycache__, logs, etc
- [x] `.gitattributes` - Line endings corretos (LF para código)
- [x] `LICENSE` - MIT License
- [x] `README.md` - Documentação completa com badges
- [x] `CONTRIBUTING.md` - Guia de contribuição
- [x] `CHANGELOG.md` - Histórico de mudanças
- [x] `.github/workflows/lint.yml` - CI/CD
- [x] `.github/ISSUE_TEMPLATE/bug_report.yml` - Template de bugs
- [x] `.github/ISSUE_TEMPLATE/feature_request.yml` - Template de features
- [x] `.github/pull_request_template.md` - Template de PRs

### 3. Estrutura do Projeto
```
Speakerbot-local-voice/
├── .github/
│   ├── workflows/
│   │   └── lint.yml
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.yml
│   │   ├── feature_request.yml
│   │   └── config.yml
│   └── pull_request_template.md
├── docs/
│   ├── CORREÇÕES_FREEZE_BACKEND.md
│   ├── README-PIP-CACHE.md
│   └── ... (documentação)
├── xtts-server/
│   ├── main.py
│   ├── web_ui.html
│   ├── manifest.json
│   ├── service-worker.js
│   └── ... (código principal)
├── .gitattributes
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── GITHUB_SETUP.md
└── requirements.txt
```

---

## 🔄 Git Workflow Correto

### Step 1: Inicializar Repositório
```bash
cd Speakerbot-local-voice
git init
git config user.name "Seu Nome"
git config user.email "seu-email@exemplo.com"
```

### Step 2: Adicionar Remote
```bash
git remote add origin https://github.com/seu-usuario/Speakerbot-local-voice.git
git remote -v  # Verificar
```

### Step 3: Primeiro Commit
```bash
# Adicionar todos os arquivos
git add .

# Revisar o que vai ser commitado
git status

# Commit com mensagem descritiva
git commit -m "Initial commit: Speakerbot PWA with XTTS v2

- Text-to-Speech engine with voice cloning
- Progressive Web App with offline support
- FastAPI backend with GPU acceleration
- Multi-language support (16 idiomas)
- Complete web UI with dark theme
- Docker and CI/CD ready"

# Ver commits
git log --oneline
```

### Step 4: Push para Main
```bash
# Renomear branch (se necessário)
git branch -M main

# Push com tracking
git push -u origin main

# Verificar no GitHub
# https://github.com/seu-usuario/Speakerbot-local-voice
```

### Step 5: Criar Release Tag
```bash
# Criar tag
git tag v0.2.0 -m "Release v0.2.0 - PWA support"

# Push tags
git push origin v0.2.0

# Ver tags
git tag -l
```

---

## 📌 Melhores Práticas Git

### Commit Messages
```bash
# ✅ BOM
git commit -m "feat: add PWA support with service worker"

# ✅ BOM
git commit -m "fix: resolve CUDA device-side assert error

- Validate audio WAV files before processing
- Add NaN/Inf sanitization
- Implement recovery mechanism"

# ❌ RUIM
git commit -m "fix stuff"
git commit -m "changes"
```

### Branches para Features
```bash
# Feature
git checkout -b feature/stylets-support

# Bug fix
git checkout -b fix/cuda-error-handling

# Documentação
git checkout -b docs/api-reference
```

### Pull Request Workflow
```bash
# 1. Criar branch
git checkout -b feature/awesome

# 2. Fazer mudanças e commits
git add .
git commit -m "feat: awesome feature"

# 3. Push
git push origin feature/awesome

# 4. No GitHub: Create Pull Request
# 5. Aguardar review e merge
```

---

## 🎯 README.md Essencial

✅ Seu README.md tem:
- [x] Título com emojis
- [x] Badges (status, linguagem, license)
- [x] Descrição breve
- [x] Características principais
- [x] Quick Start (3 passos)
- [x] Requisitos
- [x] Como usar
- [x] API examples
- [x] Troubleshooting
- [x] Roadmap
- [x] Como contribuir
- [x] License
- [x] Créditos

---

## 🔐 Segurança & Best Practices

### O que NÃO fazer
```bash
❌ Não comitar:
- Senhas ou API keys
- Tokens de autenticação
- Informações privadas
- Grandes arquivos binários
- node_modules ou venv

✅ Use .gitignore:
# Dependências
venv/
node_modules/
.env
.env.local

# Cache
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Sistema
.DS_Store
Thumbs.db

# Builds
dist/
build/
*.egg-info/
```

---

## 🚀 Publicar no GitHub (Passo a Passo)

### 1. Criar repositório no GitHub
1. Acesse https://github.com/new
2. Nome: `Speakerbot-local-voice`
3. Descrição: "Local Text-to-Speech engine with voice cloning and PWA support"
4. Public
5. Clique "Create repository"

### 2. Clonar e subir código
```bash
cd Speakerbot-local-voice
git init
git add .
git commit -m "Initial commit: Speakerbot with XTTS v2"
git branch -M main
git remote add origin https://github.com/seu-usuario/Speakerbot-local-voice.git
git push -u origin main
```

### 3. Adicionar Deploy (Opcional - GitHub Pages)
Crie `.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-pages@v3
      - run: mkdir -p _site
      - run: cp -r docs/* _site/
      - uses: actions/upload-pages-artifact@v2
      - uses: actions/deploy-pages@v2
```

---

## 📊 Badges Recomendados

Adicione ao README.md:
```markdown
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![PyTorch](https://img.shields.io/badge/pytorch-2.7.1-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-active-brightgreen.svg)
![GitHub stars](https://img.shields.io/github/stars/seu-usuario/Speakerbot-local-voice.svg)
```

---

## ✨ Dicas Finais

1. **Branch Protection**: Ativa em Settings → Branches
2. **Auto-merge**: Configure para PRs automáticas
3. **Discussions**: Ativa para comunidade
4. **Wiki**: Documente tópicos avançados
5. **Releases**: Crie releases para cada versão
6. **Sponsorship**: Adicione opção de apoio (se desejar)

---

**Parabéns! Seu projeto está pronto para GitHub! 🎉**

Próximo passo: [GitHub Setup Checklist](GITHUB_SETUP.md)
