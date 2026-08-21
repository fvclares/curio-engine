import { DataLoader } from "./core/DataLoader.js";
import { Engine } from "./core/Engine.js";
import { AudioNarrator } from "./core/AudioNarrator.js";
import { TimerManager } from "./core/TimerManager.js";
import { AudioManager } from "./core/AudioManager.js"; // <-- 1. Importação do Áudio adicionada!
import { QuestionRenderer } from "./ui/QuestionRenderer.js";
import { TimerRenderer } from "./ui/TimerRenderer.js";
import { ThemeManager } from "./theme/ThemeManager.js";
import { AppContext } from "./app/AppContext.js";
import { EmojiBackground } from "./effects/EmojiBackground.js";

const stageElement = document.querySelector("#quizStage");
const emojiContainer = document.querySelector("#emoji-background-container");
const confettiContainer = document.querySelector("#confetti-container");
const dataLoader = new DataLoader("./data");
const appContext = new AppContext();
const themeManager = new ThemeManager();
const emojiBackground = new EmojiBackground(emojiContainer, confettiContainer);
// Narração 100% pré-gerada (Kokoro TTS, offline). Nada de SpeechSynthesis.
const audioNarrator = new AudioNarrator("./");
const timerManager = new TimerManager(5);
const audioManager = new AudioManager(); // <-- 2. Áudio inicializado!
const renderer = new QuestionRenderer(
    stageElement,
    themeManager,
    emojiBackground
);
const timerRenderer = new TimerRenderer();
const engine = new Engine({ dataLoader, audioNarrator, timerManager });

engine.on("loading", () => {
  console.log('[App] Evento: loading');
  renderer.renderStatus("Loading Curio Engine...");
});

engine.on("question", (question) => {
  console.log('[App] Evento: question');
  renderer.clearExplanation();
  renderer.renderQuestion(question);
});

engine.on("answer", ({ isCorrect, correctAnswer }) => {
  console.log('[App] Evento: answer');

  audioManager.stopTimerSound(); // <-- 3. Para o som do timer se responder antes

  renderer.renderAnswer(isCorrect, correctAnswer);

  if (isCorrect) {
    const question = engine.getCurrentQuestion();
    const theme = themeManager.get(question.category);
    emojiBackground.burst({
      emojis: ["🎉", "✨", "🥳", "⭐", ...theme.floatingEmojis],
      amount: 26,
    });
  }
});

engine.on("explanation", (explanation) => {
  console.log('[App] Evento: explanation');
  renderer.renderExplanation(explanation);
});

engine.on("error", (error) => {
  console.error('[App] Evento: error', error);
  renderer.renderError(error.message);
});

timerManager.on("start", () => {
  console.log('[App] Evento: timer started');

  audioManager.playTimerSound(); // <-- 4. Toca o som de urgência quando o tempo corre

  const timerElement = timerRenderer.create();
  timerRenderer.insertIntoCard();
});

timerManager.on("update", (remaining) => {
  timerRenderer.update(remaining, 5);
});

timerManager.on("end", async () => {
  console.log('[App] Evento: timer ended');

  audioManager.stopTimerSound(); // <-- 5. Para o som quando o tempo esgota

  timerRenderer.remove();
  const currentQuestion = engine.getCurrentQuestion();
  await engine.answerQuestion(true);
});

// Prepara o app (carrega temas) enquanto a tela de início é exibida,
// mas só INICIA o quiz (e o áudio) quando o usuário clicar em "Iniciar".
// Isso dá tempo do usuário ligar a gravação de tela do celular antes.
console.log('[App] Preparando aplicação...');

const startScreen = document.querySelector("#startScreen");
const startButton = document.querySelector("#startButton");

let themesReady = null;

async function prepare() {
  const themes = await dataLoader.loadThemes();
  appContext.setThemes(themes);
  themeManager.setThemes(themes);
}

themesReady = prepare();

startButton.addEventListener(
  "click",
  async () => {
    console.log('[App] Iniciando via tela de início...');
    startButton.disabled = true;

    // Destrava o áudio do navegador: precisa acontecer dentro do gesto de
    // clique do usuário, senão o navegador bloqueia a reprodução automática.
    audioManager.playBackgroundMusic();

    startScreen.classList.add("start-screen--hidden");

    await themesReady;
    engine.start();
  },
  { once: true }
);

// Debug: exponha os objetos globalmente para testes
window.__DEBUG__ = {
  engine,
  audioNarrator,
  timerManager,
  audioManager, // <-- Adicionado ao debug
  testNarration: (audioFile) => audioNarrator.play(audioFile || engine.getCurrentQuestion()?.questionAudio),
};
