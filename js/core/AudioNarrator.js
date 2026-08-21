/**
 * AudioNarrator
 *
 * Reproduz os arquivos de narração pré-gerados por
 * `tools/generate_audio.py` (Kokoro TTS). Substitui completamente o antigo
 * VoiceManager baseado em `window.speechSynthesis`.
 *
 * Nenhuma síntese de voz acontece no navegador: este componente apenas toca
 * arquivos .wav já existentes em `assets/audio/`.
 */
export class AudioNarrator {
  /**
   * @param {string} basePath - Pasta base onde os áudios estão salvos.
   */
  constructor(basePath = "./") {
    this.basePath = basePath;
    this.isSpeaking = false;
    this.currentAudio = null;
  }

  /**
   * Toca um arquivo de narração e resolve quando ele termina.
   *
   * @param {string} audioFile - Caminho relativo salvo em questions.json
   *   (ex.: "assets/audio/zoology-001-question.wav"), ou undefined/null se
   *   a pergunta ainda não tiver esse áudio gerado.
   * @param {Object} options
   * @param {number} options.volume - Volume de 0 a 1 (padrão 1).
   * @returns {Promise<void>} Resolve quando o áudio termina (ou imediatamente,
   *   em caso de erro/arquivo ausente, para não travar o quiz).
   */
  play(audioFile, options = {}) {
    if (!audioFile) {
      console.warn("[AudioNarrator] Nenhum arquivo de áudio informado para esta narração.");
      return Promise.resolve();
    }

    return new Promise((resolve) => {
      this.stop();

      const src = this.resolvePath(audioFile);
      const audio = new Audio(src);
      audio.volume = options.volume ?? 1;

      const finish = () => {
        this.isSpeaking = false;
        if (this.currentAudio === audio) {
          this.currentAudio = null;
        }
        resolve();
      };

      audio.addEventListener("ended", finish, { once: true });
      audio.addEventListener("error", (event) => {
        console.error(`[AudioNarrator] Erro ao reproduzir "${src}":`, event);
        finish();
      }, { once: true });

      this.currentAudio = audio;
      this.isSpeaking = true;

      audio.play().catch((error) => {
        console.warn(`[AudioNarrator] Reprodução bloqueada para "${src}":`, error);
        finish();
      });
    });
  }

  /**
   * Monta o caminho final do arquivo, respeitando `basePath` caso o valor
   * salvo no JSON já não seja absoluto/relativo pronto para uso.
   */
  resolvePath(audioFile) {
    if (/^([a-z]+:)?\/\//i.test(audioFile) || audioFile.startsWith("./") || audioFile.startsWith("/")) {
      return audioFile;
    }
    return `${this.basePath}${audioFile}`;
  }

  /** Interrompe qualquer narração em andamento. */
  stop() {
    if (this.currentAudio) {
      this.currentAudio.pause();
      this.currentAudio.currentTime = 0;
      this.currentAudio = null;
    }
    this.isSpeaking = false;
  }

  getSpeaking() {
    return this.isSpeaking;
  }
}
