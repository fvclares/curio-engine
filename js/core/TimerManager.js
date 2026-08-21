export class TimerManager {
  constructor(duration = 5) {
    this.duration = duration;
    this.remaining = duration;
    this.isRunning = false;
    this.intervalId = null;
    this.listeners = new Map();
  }

  /**
   * Inicia o timer
   */
  start() {
    if (this.isRunning) return;

    this.remaining = this.duration;
    this.isRunning = true;
    this.emit('start');

    this.intervalId = setInterval(() => {
      this.remaining -= 0.1;
      this.emit('update', Math.max(0, this.remaining));

      if (this.remaining <= 0) {
        this.stop();
        this.emit('end');
      }
    }, 100);
  }

  /**
   * Para o timer
   */
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
    this.isRunning = false;
  }

  /**
   * Registra listener para evento
   * @param {string} eventName - Nome do evento
   * @param {Function} callback - Função callback
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

  getRemaining() {
    return Math.max(0, this.remaining);
  }

  getPercentage() {
    return (this.remaining / this.duration) * 100;
  }
}
