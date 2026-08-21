# Curio Engine

Curio Engine is a framework-free HTML5 quiz engine foundation built with modular JavaScript, JSON content, and a responsive vertical-first interface.

## How to Run

Open this folder with Live Server or any local static server. The app uses `fetch()` to load `data/questions.json`, so opening `index.html` directly from the file system may be blocked by the browser.

## Current Scope

- Project structure created.
- JSON questions loaded from `data/questions.json`.
- JSON validated by `DataLoader`.
- **Quiz runs autonomously** with automatic flow.
- **Voice engine**: reads question, correct answer, and explanation.
- **5-second timer**: circular visual timer during waiting period.
- **Answer feedback**: highlights correct answer, grays out wrong answers.
- **Explanation display**: shows and reads explanation automatically.
- **Auto-advance**: moves to next question after explanation.

## Content Enrichment: Audio Generation

Curio Engine includes a build-time tool that generates the spoken narration
(question, correct answer, explanation) for every question as `.wav` files,
using the local Kokoro TTS model — no paid API required. It runs with
Python, separately from the browser app. See `tools/README.md` for full
documentation.

## Main Files

- `PRODUCT.md`: product and architecture source of truth.
- `index.html`: application entry point.
- `css/style.css`: responsive Minimal Dark foundation with timer and feedback styles.
- `js/app.js`: composition root and event orchestration.
- `js/core/DataLoader.js`: JSON loading and validation.
- `js/core/Engine.js`: quiz flow with states and automatic progression.
- `js/core/VoiceManager.js`: text-to-speech using Web Speech API.
- `js/core/TimerManager.js`: 5-second countdown timer with events.
- `js/core/StateManager.js`: state machine for quiz flow.
- `js/ui/QuestionRenderer.js`: renders question, answers, and explanations.
- `js/ui/TimerRenderer.js`: renders circular timer visualization.
- `data/questions.json`: quiz content with explanations.

## Autonomous Flow

1. **Load** → Display loading message
2. **Question** → Render question, speak question
3. **Wait** → Show 5-second timer, wait for timeout
4. **Answer** → Highlight correct answer, speak it
5. **Explanation** → Display explanation, speak it
6. **Next** → Auto-advance to next question (2s delay)
7. **Loop** → Return to Question step
8. **Finish** → Show finished state when quiz ends
