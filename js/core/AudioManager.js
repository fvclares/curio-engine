export class AudioManager {
  constructor() {
    // Caminhos relativos ao arquivo index.html (raiz do projeto)
    this.bgMusic = new Audio('./assets/sons/bg-music.mp3');
    this.bgMusic.loop = true; // Mantém a música tocando em loop
    this.bgMusic.volume = 0.08; // 8% de volume para não ofuscar a leitura da tela

    this.timerSound = new Audio('./assets/sons/timer-5s.mp3');
    this.timerSound.volume = 0.5; // 50% de volume para dar senso de urgência
  }

  playBackgroundMusic() {
    // O .catch é essencial aqui para evitar erros vermelhos no console 
    // caso o navegador bloqueie o áudio antes do usuário clicar na tela
    this.bgMusic.play().catch(error => {
      console.warn("Autoplay bloqueado. O áudio iniciará após interação na tela.", error);
    });
  }

  stopBackgroundMusic() {
    this.bgMusic.pause();
    this.bgMusic.currentTime = 0; // Reinicia a faixa
  }

  pauseBackgroundMusic() {
    this.bgMusic.pause(); // Apenas pausa, útil se você tiver um botão de "Mudo"
  }

  playTimerSound() {
    this.timerSound.currentTime = 0; // Garante que o som comece sempre do zero
    this.timerSound.play().catch(error => {
      console.warn("Erro ao tocar efeito sonoro do timer:", error);
    });
  }

  stopTimerSound() {
    this.timerSound.pause();
    this.timerSound.currentTime = 0;
  }
}