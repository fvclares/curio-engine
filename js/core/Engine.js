import { StateManager, STATES } from "./StateManager.js";

export class Engine {
  constructor({ dataLoader, audioNarrator, timerManager }) {
    this.dataLoader = dataLoader;
    this.audioNarrator = audioNarrator;
    this.timerManager = timerManager;
    this.stateManager = new StateManager();

    this.questions = [];
    this.currentQuestionIndex = 0;
    this.listeners = new Map();
    this.isAutomatic = true;
  }

  on(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }

    this.listeners.get(eventName).add(callback);
  }

  async start() {
    console.log('[Engine] Iniciando...');
    this.stateManager.transition(STATES.LOADING);
    this.emit("loading");

    try {
      this.questions = await this.dataLoader.loadQuestions();
      console.log(`[Engine] ${this.questions.length} perguntas carregadas`);
      this.currentQuestionIndex = 0;
      await this.showQuestion();
    } catch (error) {
      console.error('[Engine] Erro ao carregar:', error);
      this.emit("error", error);
    }
  }

  async showQuestion() {
    const question = this.getCurrentQuestion();
    console.log(`[Engine] Exibindo pergunta ${this.currentQuestionIndex + 1}:`, question.prompt.substring(0, 50) + '...');
    this.stateManager.transition(STATES.QUESTION);
    this.emit("question", question);

    if (this.isAutomatic) {
      await this.speakQuestion(question);
    }
  }

  async speakQuestion(question) {
    console.log('[Engine] Narrando pergunta...');
    this.stateManager.transition(STATES.SPEAKING_QUESTION);
    await this.audioNarrator.play(question.questionAudio);

    console.log('[Engine] Iniciando timer...');
    this.stateManager.transition(STATES.WAITING);
    this.timerManager.start();
  }

  async answerQuestion(isCorrect) {
    console.log('[Engine] Respondendo pergunta...');
    this.timerManager.stop();

    const question = this.getCurrentQuestion();
    const correctAnswer = question.answers.find((a) => a.isCorrect);

    this.stateManager.transition(STATES.ANSWER);
    this.emit("answer", { isCorrect, correctAnswer });

    if (this.isAutomatic) {
      await this.speakAnswer(question, correctAnswer);
    }
  }

  async speakAnswer(question, correctAnswer) {
    console.log('[Engine] Narrando resposta correta:', correctAnswer.text);
    this.stateManager.transition(STATES.SPEAKING_ANSWER);
    await this.audioNarrator.play(question.answerAudio);

    this.stateManager.transition(STATES.EXPLANATION);
    this.emit("explanation", question.explanation);

    await this.speakExplanation(question);
  }

  async speakExplanation(question) {
    console.log('[Engine] Narrando explicação...');
    this.stateManager.transition(STATES.SPEAKING_EXPLANATION);
    await this.audioNarrator.play(question.explanationAudio);

    await this.advanceToNext();
  }

  async advanceToNext() {
    console.log('[Engine] Aguardando 2 segundos antes de próxima pergunta...');
    this.stateManager.transition(STATES.NEXT);

    await new Promise((resolve) => setTimeout(resolve, 2000));

    if (this.questions.length === 0) {
      this.stateManager.transition(STATES.FINISHED);
      this.emit("finished");
      return;
    }

    this.currentQuestionIndex = (this.currentQuestionIndex + 1) % this.questions.length;
    await this.showQuestion();
  }

  nextQuestion() {
    if (this.questions.length === 0) {
      this.emit("error", new Error("No questions are available."));
      return;
    }

    this.currentQuestionIndex = (this.currentQuestionIndex + 1) % this.questions.length;
    this.emit("question", this.getCurrentQuestion());
  }

  finish() {
    console.log('[Engine] Quiz finalizado');
    this.timerManager.stop();
    this.audioNarrator.stop();
    this.stateManager.transition(STATES.FINISHED);
    this.emit("finished");
  }

  getCurrentQuestion() {
    return this.questions[this.currentQuestionIndex];
  }

  emit(eventName, payload) {
    const callbacks = this.listeners.get(eventName) ?? [];

    callbacks.forEach((callback) => {
      callback(payload);
    });
  }

  getState() {
    return this.stateManager.getState();
  }
}
