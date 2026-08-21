# CurioEngine — Gerador de Narração (Kokoro TTS)

Este utilitário gera **toda a narração do quiz previamente**, como arquivos
`.wav`, usando o [Kokoro TTS](https://github.com/hexgrad/kokoro) rodando
localmente. Depois de gerados, o `index.html` apenas **reproduz** esses
arquivos — o navegador não sintetiza mais nenhuma voz em tempo real, e o
`SpeechSynthesis` do navegador não é mais usado em nenhum lugar do projeto.

Funciona 100% offline após a primeira execução (que baixa o modelo) e não
depende do navegador, do sistema operacional ter vozes instaladas, ou de
qualquer serviço de nuvem.

---

## 1. Pré-requisitos

- **Python 3.9+** (Windows, macOS ou Linux)
- **espeak-ng** — o Kokoro usa o `espeak-ng` como apoio de fonetização para
  português (e outros idiomas além do inglês).

### Instalar o espeak-ng

**Windows:**
1. Baixe o instalador em:
   https://github.com/espeak-ng/espeak-ng/releases
   (arquivo `espeak-ng-X.X.X-x64.msi` ou similar)
2. Execute o instalador (padrão instala em `C:\Program Files\eSpeak NG`).
3. Adicione a pasta de instalação ao `PATH` do Windows, se o instalador não
   fizer isso automaticamente (Painel de Controle → Variáveis de Ambiente).
4. Confirme no PowerShell/CMD:
   ```
   espeak-ng --version
   ```

**macOS:**
```bash
brew install espeak-ng
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get install espeak-ng
```

---

## 2. Instalar as dependências Python

Na raiz do projeto (`CURIOENGINE/`):

```bash
python -m venv .venv
```

Ativar o ambiente virtual:

- Windows (PowerShell): `.venv\Scripts\Activate.ps1`
- Windows (CMD): `.venv\Scripts\activate.bat`
- macOS/Linux: `source .venv/bin/activate`

Instalar as dependências:

```bash
pip install -r tools/requirements.txt
```

---

## 3. Baixar o modelo Kokoro

Você **não precisa baixar nada manualmente** na primeira vez: assim que o
script roda pela primeira vez, o pacote `kokoro` baixa automaticamente os
pesos do modelo (~327 MB) e os arquivos de voz do Hugging Face Hub
(`hexgrad/Kokoro-82M`) e os guarda em cache local
(`~/.cache/huggingface` no Linux/macOS, `%USERPROFILE%\.cache\huggingface`
no Windows). Isso requer internet **apenas na primeira execução**.

Se preferir baixar/verificar o cache antecipadamente (por exemplo, para
preparar uma máquina sem internet depois), rode:

```bash
python -c "from kokoro import KPipeline; KPipeline(lang_code='p')"
```

Esse comando força o download e a inicialização do modelo sem gerar
nenhum áudio. Depois disso, o script funciona totalmente offline.

---

## 4. Executar

Gerar apenas os áudios que ainda não existem:

```bash
python tools/generate_audio.py
```

Regenerar **todos** os áudios (sobrescrevendo os existentes):

```bash
python tools/generate_audio.py --force
```

### Opções disponíveis

| Opção         | Padrão                    | Descrição                                             |
|---------------|---------------------------|---------------------------------------------------------|
| `--force`     | desativado                | Regenera todos os áudios, mesmo os já existentes        |
| `--questions` | `data/questions.json`     | Caminho alternativo para o arquivo de perguntas          |
| `--output`    | `assets/audio`            | Pasta de saída dos áudios                                |
| `--voice`     | `pf_dora`                 | Voz do Kokoro (feminina, pt-BR, é a recomendada)         |
| `--speed`     | `0.9`                     | Velocidade da fala (1.0 = normal, <1.0 = mais lenta)     |

Exemplo com opções customizadas:

```bash
python tools/generate_audio.py --voice pf_dora --speed 0.85 --force
```

---

## 5. Estrutura de pastas

```
CURIOENGINE/
  assets/
    audio/
      zoology-001-question.wav
      zoology-001-answer.wav
      zoology-001-explanation.wav
      ...
  data/
    questions.json          <- atualizado automaticamente com os campos *Audio
  tools/
    generate_audio.py       <- ponto de entrada (CLI)
    requirements.txt
    README.md               <- este arquivo
    lib/
      __init__.py
      base_generator.py     <- classes reaproveitáveis (repositório + loop de geração)
      audio_generator.py    <- AudioGenerator (Kokoro)
      kokoro_backend.py     <- wrapper isolado do pacote `kokoro`
      text_processing.py    <- normalização de texto para narração natural
      audio_utils.py        <- resample, normalização, padding, salvamento .wav
```

`questions.json` passa a ter, em cada pergunta:

```json
{
  "id": "zoology-001",
  "prompt": "Qual é o animal terrestre mais rápido do mundo?",
  "questionAudio": "assets/audio/zoology-001-question.wav",
  "answers": [
    { "text": "Guepardo", "isCorrect": true }
  ],
  "answerAudio": "assets/audio/zoology-001-answer.wav",
  "explanation": "O guepardo pode atingir velocidades superiores a 100 km/h...",
  "explanationAudio": "assets/audio/zoology-001-explanation.wav"
}
```

---

## 6. Exemplo de saída no terminal

```
=== AUDIO GENERATOR - 9 pergunta(s) ===

[1/9] zoology-001
  ✔ pergunta
  ✔ resposta
  ✔ explicação
[2/9] geography-005
  ↷ pergunta (já existe, pulando)
  ↷ resposta (já existe, pulando)
  ↷ explicação (já existe, pulando)
...

Audio concluído com sucesso. data/questions.json atualizado.
```

---

## 7. Qualidade de áudio

- Voz padrão: **pf_dora** (feminina, português brasileiro).
- Ritmo levemente mais lento que o normal (`speed=0.9`) para maior clareza.
- Texto pré-processado antes da síntese (`lib/text_processing.py`):
  expande abreviações comuns (`km/h`, `%`, `Sr.`, etc.), normaliza espaços
  e garante pontuação final para uma entonação de encerramento natural.
- Pós-processamento (`lib/audio_utils.py`):
  - Normalização de pico (-3 dBFS) para volume consistente entre arquivos.
  - Resample para **44.1 kHz**, taxa de amostragem padrão do projeto.
  - Pequeno silêncio no início/fim de cada clipe para evitar cortes bruscos.

---

## 8. Arquitetura preparada para crescer

`lib/base_generator.py` define uma classe abstrata `BaseGenerator` (com o
loop de iteração, checagem de arquivos existentes, logs e persistência do
JSON) e um `QuestionRepository` para carregar/salvar `questions.json`.

`AudioGenerator` é apenas *uma* implementação dessa base. No futuro,
`ImageGenerator`, `SubtitleGenerator` e `VideoGenerator` podem ser criados
como novas classes que também estendem `BaseGenerator`, reaproveitando todo
o carregamento/iteração/gravação do JSON **sem precisar alterar
`AudioGenerator` ou `audio_generator.py`**.

---

## 9. Erros comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `O pacote 'kokoro' não está instalado` | Dependências não instaladas | `pip install -r tools/requirements.txt` |
| `Falha ao inicializar o Kokoro (KPipeline)` | `espeak-ng` ausente do PATH, ou primeira execução sem internet | Instale o `espeak-ng` (seção 1) e garanta internet na primeira execução |
| `texto vazio para narrar` | Pergunta sem `prompt`/`explanation`, ou sem resposta marcada `isCorrect: true` | Corrija a pergunta em `data/questions.json` |
| Áudio não atualiza mesmo rodando o script | Arquivo `.wav` já existe | Use `--force` para regenerar |
