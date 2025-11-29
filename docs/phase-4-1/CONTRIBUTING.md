# Contributing to Speakerbot

Obrigado por considerar contribuir para o Speakerbot! Este documento fornece diretrizes e instruções para contribuições.

## 🚀 Como Contribuir

### Relatando Bugs

Antes de criar um relatório de bug, verifique a lista de issues pois você pode descobrir que o erro já foi reportado.

Ao criar um relatório de bug, inclua o máximo de detalhes possível:

* **Use um título claro e descritivo**
* **Descreva os passos exatos** que reproduzem o problema
* **Forneça exemplos específicos** para demonstrar os passos
* **Descreva o comportamento observado** e **o que você esperava ver**
* **Screenshots/logs** são muito úteis
* **Seu ambiente**: SO, Python version, GPU/CUDA info, etc.

### Sugestões de Melhorias

Sugestões de melhorias são rastreadas como GitHub issues. Ao criar uma sugestão, inclua:

* **Use um título claro e descritivo**
* **Forneça uma descrição passo-a-passo** da sugestão
* **Forneça exemplos específicos** para demonstrar as etapas
* **Descreva o comportamento atual** e **o comportamento sugerido**
* **Explique por que essa melhoria seria útil**

## 🔧 Pull Requests

* Preencha o template do pull request
* Siga o estilo de código Python (PEP 8)
* Inclua testes apropriados
* Atualize a documentação conforme necessário
* Termine todos os arquivos com uma nova linha

## 📋 Processo de Desenvolvimento

### 1. Fork e Clone

```bash
git clone https://github.com/seu-usuario/Speakerbot-local-voice.git
cd Speakerbot-local-voice
git remote add upstream https://github.com/usuario-original/Speakerbot-local-voice.git
```

### 2. Crie uma Branch

```bash
git checkout -b feature/sua-feature
# ou
git checkout -b fix/seu-bug-fix
```

### 3. Faça suas Mudanças

* Escreva código limpo e bem documentado
* Siga o estilo PEP 8
* Adicione testes unitários para novas funcionalidades
* Atualize o README se necessário

### 4. Teste Localmente

```bash
cd xtts-server
python -m pip install -r requirements.txt
python main.py
```

### 5. Commit

```bash
git add .
git commit -m "tipo: descrição breve

Descrição mais detalhada se necessário.

Fixes #123
```

**Tipos de commit:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, sem mudanças de lógica
- `refactor`: Refatoração de código
- `perf`: Melhorias de performance
- `test`: Adição/alteração de testes

### 6. Push e Crie um Pull Request

```bash
git push origin feature/sua-feature
```

Crie um Pull Request no GitHub com uma descrição clara.

## 📝 Guia de Estilo

### Python (PEP 8)

```python
# ✅ Bom
def calculate_audio_length(wav_data: np.ndarray, sample_rate: int) -> float:
    """Calculate audio length in seconds.
    
    Args:
        wav_data: Audio waveform
        sample_rate: Sample rate in Hz
        
    Returns:
        Length in seconds
    """
    return len(wav_data) / sample_rate


# ❌ Evitar
def calc_len(w,sr):
    return len(w)/sr
```

### Commit Messages

```
feat: adicionar suporte para múltiplos modelos TTS

- Refatorar engine para suportar VITS e StyleTTS2
- Adicionar seletor de modelo na UI
- Documentar integração de novos engines

Fixes #42
```

### Docstrings

```python
def synthesize(
    text: str,
    language: str = "pt",
    voice: str = "default"
) -> str:
    """Sintetizar texto para áudio.
    
    Args:
        text: Texto para sintetizar
        language: Código do idioma (ex: 'pt', 'en')
        voice: ID da voz para usar
        
    Returns:
        Caminho do arquivo WAV gerado
        
    Raises:
        ValueError: Se o texto estiver vazio
        RuntimeError: Se a síntese falhar
    """
```

## ✅ Checklist antes de fazer Push

- [ ] Código segue PEP 8
- [ ] Testes locais passando
- [ ] Documentação atualizada
- [ ] Commit message clara
- [ ] Sem arquivos desnecessários (venv, __pycache__, etc)
- [ ] Branch está atualizada com main

## 🤝 Comunidade

* Se você tiver dúvidas, abra uma issue com a label `question`
* Seja respeitoso com outros contribuidores
* Forneça feedback construtivo nas reviews

## 📚 Recursos Úteis

* [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
* [GitHub Flow](https://guides.github.com/introduction/flow/)
* [Conventional Commits](https://www.conventionalcommits.org/)

Obrigado por contribuir! 🎉
