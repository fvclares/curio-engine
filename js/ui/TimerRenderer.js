export class TimerRenderer {
  constructor() {
    this.element = null;
  }

  create() {
    const progressBar = document.createElement("div");
    progressBar.className = "timer-bar-progress";
    progressBar.id = "timerProgress";

    this.element = progressBar;
    return progressBar;
  }

  insertIntoCard() {
    const timerPlaceholder = document.querySelector("#timerPlaceholder");
    if (timerPlaceholder && this.element) {
      timerPlaceholder.replaceChildren(this.element);
    }
  }

  update(remaining, total) {
    if (!this.element) return;

    const percentage = (remaining / total) * 100;
    this.element.style.width = `${percentage}%`;
  }

  remove() {
    const timerPlaceholder = document.querySelector("#timerPlaceholder");
    if (timerPlaceholder) {
      timerPlaceholder.replaceChildren();
    }
  }
}
