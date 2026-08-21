export const STATES = {
  LOADING: 'LOADING',
  QUESTION: 'QUESTION',
  SPEAKING_QUESTION: 'SPEAKING_QUESTION',
  WAITING: 'WAITING',
  ANSWER: 'ANSWER',
  SPEAKING_ANSWER: 'SPEAKING_ANSWER',
  EXPLANATION: 'EXPLANATION',
  SPEAKING_EXPLANATION: 'SPEAKING_EXPLANATION',
  NEXT: 'NEXT',
  FINISHED: 'FINISHED',
};

export class StateManager {
  constructor() {
    this.currentState = STATES.LOADING;
    this.listeners = new Map();
  }

  /**
   * Transiciona para novo estado
   */
  transition(newState) {
    const oldState = this.currentState;
    this.currentState = newState;
    this.emit('stateChange', { oldState, newState });
  }

  /**
   * Registra listener para eventos de estado
   */
  on(eventName, callback) {
    if (!this.listeners.has(eventName)) {
      this.listeners.set(eventName, new Set());
    }
    this.listeners.get(eventName).add(callback);
  }

  /**
   * Emite evento
   */
  emit(eventName, payload) {
    const callbacks = this.listeners.get(eventName) ?? [];
    callbacks.forEach((callback) => {
      callback(payload);
    });
  }

  getState() {
    return this.currentState;
  }

  isIn(state) {
    return this.currentState === state;
  }
}
