# Curio Engine — Documentação

## 1. O que é

Curio Engine é um **motor de quiz em HTML5** construído sem frameworks (JavaScript puro, ES6), pensado para rodar como um vídeo/experiência vertical (formato 9:16, estilo Reels/Shorts) totalmente **autônoma**: as perguntas aparecem, são narradas por voz, o tempo passa, a resposta certa é revelada e explicada, e o quiz avança sozinho para a próxima pergunta — sem precisar de nenhuma interação do usuário.

O conteúdo (perguntas, respostas, explicações, imagens, categorias) fica inteiramente separado do código, em um arquivo `data/questions.json`. Isso significa que trocar o "assunto" do quiz é só trocar o JSON — o motor (engine) é genérico e reutilizável.

## 2. O que ele faz

### 2.1 Experiência do quiz (o que roda no navegador)

Ciclo automático de cada pergunta:

1. **Load** — carrega e valida `data/questions.json`.
2. **Question** — mostra a pergunta e a narra por voz.
3. **Wait** — timer circular de 5 segundos.
4. **Answer** — destaca a resposta certa, apaga as erradas, narra a resposta.
5. **Explanation** — mostra e narra a explicação da resposta.
6. **Next** — avança automaticamente (2s de espera) para a próxima pergunta.
7. **Loop** — repete até o fim do conjunto de perguntas.
8. **Finished** — estado final quando o quiz termina.

### 2.2 Arquitetura (separação de responsabilidades)

| Módulo | Responsabilidade |
|---|---|
| `js/core/DataLoader.js` | Carrega e valida o JSON de perguntas |
| `js/core/Engine.js` | Orquestra o fluxo do quiz (`start()`, `nextQuestion()`, `finish()`) sem tocar em HTML |
| `js/core/StateManager.js` | Máquina de estados (`LOADING`, `QUESTION`, `WAITING`, `ANSWER`, `EXPLANATION`, `NEXT`, `FINISHED`) |
| `js/core/TimerManager.js` | Timer de 5s com eventos `START`/`UPDATE`/`END` |
| `js/core/AudioNarrator.js` / `AudioManager.js` | Narração e trilha/efeitos sonoros |
| `js/ui/QuestionRenderer.js` | Desenha pergunta, respostas e texto da explicação na tela |
| `js/ui/TimerRenderer.js` | Desenha o timer circular |
| `js/theme/ThemeManager.js` | Tema visual (Minimal Dark) |
| `PRODUCT.md` | Fonte de verdade do produto: visão, regras de desenvolvimento e roadmap |

O motor **nunca manipula HTML diretamente** e **nunca tem perguntas escritas no código** — tudo vem do JSON. Isso deixa aberto o caminho do roadmap para outros formatos (verdadeiro/falso, jogo da memória, achar a diferença etc.) reaproveitando o mesmo motor.

### 2.3 Ferramenta de conteúdo (roda fora do navegador, em build-time)

Essa ferramenta **não faz parte do site publicado** — é um script que você roda para preparar o áudio antes de publicar.

**Gerador de áudio** (`tools/generate_audio.py`, Python + Kokoro TTS)
- Lê as perguntas em `data/questions.json` e gera os `.wav` de narração em português (voz `pf_dora`, feminina, pt-BR) usando o modelo **Kokoro TTS local** — sem depender de nenhuma API paga de voz.
- O modelo é baixado e cacheado automaticamente na primeira execução; depende também do binário `espeak-ng`.

> O projeto não busca nem inclui imagens — a tela de explicação mostra apenas o texto de `question.explanation`, mantendo o fluxo mais simples e sem dependência de bancos de imagem externos.

## 3. Estado atual do projeto (`PRODUCT.md`)

Já concluído: estrutura do projeto, carregamento/validação de JSON, sorteio de perguntas sem repetição, timer de 5s, fluxo automático completo, narração por voz (Web Speech API / Kokoro), destaque de resposta certa/errada e explicação.

Ainda no roadmap: embaralhar alternativas, `AnimationManager` (fade/zoom/slide/shake), separar temas do motor, editor visual de perguntas, pacotes de conteúdo prontos (espaço, animais, história, filmes), modos de exportação (fullscreen, loop automático, mobile/vertical), metas de performance (Lighthouse 95+, 60 FPS) e a versão comercial (README, licença, docs, exemplos).

## 4. Como rodar 100% online e gratuito, via GitHub

O projeto é **puro front-end estático** (HTML/CSS/JS, sem backend), então qualquer hospedagem estática serve — e o repositório já vem com dois workflows do **GitHub Actions** prontos:

- `.github/workflows/generate-audio.yml` — gera o áudio de narração na nuvem do GitHub (sem usar seu notebook).
- `.github/workflows/deploy-pages.yml` — publica o site automaticamente no GitHub Pages a cada push.

### Passo a passo

1. **Suba o projeto para um repositório novo no GitHub**
   ```bash
   cd CurioEngine
   git init
   git add .
   git commit -m "Curio Engine: setup inicial"
   git branch -M main
   git remote add origin https://github.com/SEU_USUARIO/curio-engine.git
   git push -u origin main
   ```
   Pode ser repositório público ou privado — ambos funcionam no plano gratuito.

2. **Ative o GitHub Pages com origem "GitHub Actions"**
   No repositório: `Settings` → `Pages` → em **Source**, escolha **GitHub Actions** (não "Deploy from a branch"). O workflow `deploy-pages.yml` já cuida do resto.

3. **Rode a geração de áudio pela aba Actions**
   Vá em `Actions` → **"Gerar áudio"** → **Run workflow**. Marque "forçar regeneração" se quiser refazer os áudios já existentes, ou deixe desmarcado para gerar só o que falta. Isso roda inteiramente nos servidores do GitHub.

4. **Aguarde o commit automático**
   Ao final da execução, o workflow commita direto no repositório os arquivos gerados: `assets/audio/` e o `data/questions.json` atualizado.

5. **O site republica sozinho**
   Esse commit dispara automaticamente o `deploy-pages.yml`, que republica o site em:
   ```
   https://SEU_USUARIO.github.io/curio-engine
   ```

### Limites do plano gratuito a considerar

- **GitHub Actions**: 2.000 minutos/mês grátis em repositório privado; em repositório público os minutos não são cobrados. A geração de áudio (Kokoro) é leve para poucas perguntas — se o catálogo crescer muito, rode em lotes ou use repositório público.
- **GitHub Pages**: sem custo para sites estáticos dentro dos limites normais de uso (repositórios até 1 GB, banda razoável).
