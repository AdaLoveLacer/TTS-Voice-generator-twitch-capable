# 📚 Speakerbot Documentation

Bem-vindo à documentação completa do Speakerbot!

## 🚀 Começando

**Primeira vez?** Comece aqui:
- **[Quick Start](QUICK_START.md)** - Guia rápido para Windows, Linux e macOS

## 📖 Documentação Principal

### Setup & Instalação
- **[GitHub Readiness Report](GITHUB_READINESS_REPORT.md)** - Status do projeto (97/100) para publicação
- **[Quick Start](QUICK_START.md)** - Setup universal (Windows, Linux, macOS)
- **[Setup Linux/macOS](setup/LINUX_MACOS_SETUP.md)** - Instruções detalhadas para Linux/macOS
- **[Startup Cleanup](setup/STARTUP_CLEANUP.md)** - Melhorias nos scripts de startup (79% redução)
- **[Linux/macOS Completion](setup/LINUX_MACOS_COMPLETION.md)** - Report de implementação cross-platform

### GitHub & Publicação
- **[GitHub Setup](GITHUB_SETUP.md)** - Checklist para publicar no GitHub
- **[GitHub Best Practices](GITHUB_BEST_PRACTICES.md)** - Workflow Git e melhores práticas

### Histórico & Contribuição
- **[Changelog](CHANGELOG.md)** - Histórico completo de mudanças por versão
- **[Contributing](CONTRIBUTING.md)** - Como contribuir para o projeto

### Recursos
- [Guias Técnicos](guides/) - Documentação de features específicas
- [API Reference](api/) - (Em desenvolvimento) Documentação da API REST

## 📋 Estrutura de Documentação

```
docs/
├── INDEX.md                           (você está aqui)
├── QUICK_START.md                     (guia rápido universal)
├── CHANGELOG.md                       (histórico de versões)
├── CONTRIBUTING.md                    (como contribuir)
├── GITHUB_READINESS_REPORT.md         (status 97/100)
├── GITHUB_SETUP.md                    (publicação no GitHub)
├── GITHUB_BEST_PRACTICES.md           (workflow e melhores práticas)
├── setup/
│   ├── LINUX_MACOS_SETUP.md           (setup detalhado)
│   ├── STARTUP_CLEANUP.md             (mudanças de startup)
│   └── LINUX_MACOS_COMPLETION.md      (report de conclusão)
├── guides/
│   └── (em desenvolvimento)
└── api/
    └── (em desenvolvimento)
```

## 🎯 Por Onde Começar?

| Caso de Uso | Documento |
|-------------|-----------|
| **Novo no Speakerbot** | [Quick Start](QUICK_START.md) |
| **Instalar em Linux/macOS** | [Setup Linux/macOS](setup/LINUX_MACOS_SETUP.md) |
| **Saber status do projeto** | [GitHub Readiness Report](GITHUB_READINESS_REPORT.md) |
| **Contribuir código** | [Contributing](CONTRIBUTING.md) |
| **Publicar no GitHub** | [GitHub Setup](GITHUB_SETUP.md) |
| **Solucionar problemas** | [Quick Start - Troubleshooting](QUICK_START.md#troubleshooting) |
| **Ver mudanças recentes** | [Changelog](CHANGELOG.md) |

## 📚 Tópicos Principais

### 1. Instalação
- **Windows**: Duplo-clique `start-server.bat`
- **Linux/macOS**: `chmod +x *.sh && ./start-server.sh`
- **Manual**: Veja [Setup Linux/macOS](setup/LINUX_MACOS_SETUP.md)
- **Status**: ✅ Cross-platform com 100% paridade funcional

### 2. Uso Básico
- Acesse `http://localhost:8877`
- Digite texto
- Escolha idioma e voz
- Clique "Sintetizar"

### 3. Recursos Avançados
- Clonar voz personalizada
- Monitor de arquivo TXT em tempo real
- Integração com OBS
- API REST completa

### 4. Desenvolvimento
- Veja [Contributing](CONTRIBUTING.md)
- Type hints com Pyright
- Scripts multiplataforma testados
- CI/CD pronto para GitHub

## 🔧 Requisitos

- **Python**: 3.10+
- **GPU NVIDIA**: RTX 3050+ (mínimo recomendado)
- **RAM**: 8GB (16GB recomendado)
- **Disco**: 5GB para modelos TTS
- **Sistemas Suportados**:
  - Windows 10+ (PowerShell)
  - Ubuntu 20.04+
  - Debian 11+
  - macOS 10.14+ (Mojave+)
  - CentOS 8+

## ✨ Destaques da Documentação

### Recém-Adicionado (29 de Nov 2025)
- ✅ Suporte completo para Linux/macOS
- ✅ Scripts simplificados (79% redução de código)
- ✅ Guia universal Quick Start
- ✅ Status GitHub (97/100 - Pronto para publicação)
- ✅ Documentação centralizada em `/docs`

### Totalmente Documentado
- ✅ Setup por plataforma
- ✅ Troubleshooting
- ✅ Histórico de mudanças
- ✅ Guia de contribuição
- ✅ Workflow GitHub

## 🆘 Suporte

**Documentação não resolveu?**
1. Verifique [Quick Start - Troubleshooting](QUICK_START.md#troubleshooting)
2. Leia [Contributing](CONTRIBUTING.md) para padrões de código
3. Abra issue no GitHub (em breve)
4. Verifique [Changelog](CHANGELOG.md) para mudanças recentes

## 🔗 Links Rápidos

| Link | Descrição |
|------|-----------|
| [README.md](../README.md) | Documentação principal do projeto |
| [LICENSE](../LICENSE) | MIT License |
| [xtts-server/main.py](../xtts-server/main.py) | Código do servidor FastAPI |
| [xtts-server/web_ui.html](../xtts-server/web_ui.html) | Interface web PWA |

## 📝 Versão da Documentação

**Última atualização**: 29 de Novembro de 2025  
**Versão**: 2.0 (Reorganizada em `/docs`)  
**Status**: ✅ Completa e organizada para publicação GitHub  
**Compatível com**: Speakerbot v1.0+

## 🎓 Documentação Adicional

- [README.md](../README.md) - Overview do projeto
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Guidelines para contribuidores
- [LICENSE](../LICENSE) - MIT License
- [CHANGELOG.md](../CHANGELOG.md) - Histórico de versões
- [GITHUB_SETUP.md](../GITHUB_SETUP.md) - Setup GitHub

## 🚀 Próximas Versões

Documentação planejada para futuras versões:
- [ ] API Reference detalhada
- [ ] Guias de resources
- [ ] Video tutorials
- [ ] Docker setup
- [ ] Deploy guides

---

**Pronto para começar?** → [Quick Start](QUICK_START.md)
