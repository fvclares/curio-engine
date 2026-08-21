export class EmojiBackground {
    constructor(container, burstContainer = container) {
        this.container = container;
        this.burstContainer = burstContainer;
        this.elements = [];
        this.interval = null;
    }

    start(config = {}) {
        this.clear();

        const {
            emojis = ["⭐"],
            amount = 50, // Recomendo já deixar um padrão mais alto aqui caso o JSON falhe
            speed = 8
        } = config;

        // Nossa roleta de animações criadas no CSS
        const animations = ['floatStraight', 'floatLeft', 'floatRight', 'zigzagFloat'];

        // Cria todos os emojis de uma vez e deixa eles em loop infinito
        for (let i = 0; i < amount; i++) {
            const emoji = emojis[Math.floor(Math.random() * emojis.length)];
            const element = document.createElement("div");
            
            element.className = "floating-emoji";
            element.textContent = emoji;

            // 1. Sorteia a trajetória (reto, esquerda, direita, zigue-zague)
            const randomAnim = animations[Math.floor(Math.random() * animations.length)];
            
            // 2. Sorteia o tamanho (entre 30px e 65px para dar profundidade)
            const randomSize = Math.floor(Math.random() * 35) + 30;
            
            // 3. Sorteia a posição horizontal (de 0% a 100% da tela)
            const randomLeft = Math.floor(Math.random() * 100);
            
            // 4. Cria uma variação de velocidade para não subirem em bloco
            const randomDuration = speed + (Math.random() * 4 - 2); 
            
            // 5. Atraso aleatório para que o fluxo pareça contínuo
            const randomDelay = Math.random() * speed; 

            // Aplica as regras sorteadas
            element.style.animationName = randomAnim;
            element.style.animationDuration = `${randomDuration}s`;
            element.style.animationDelay = `${randomDelay}s`;
            element.style.animationIterationCount = "infinite"; // Faz a mágica do loop acontecer!
            element.style.left = `${randomLeft}vw`;
            element.style.fontSize = `${randomSize}px`;

            this.container.appendChild(element);
            this.elements.push(element);
        }
    }

    clear() {
        if(this.interval){
            clearInterval(this.interval);
            this.interval = null;
        }

        this.elements.forEach(element => {
            element.remove();
        });

        this.elements = [];
    }

    /**
     * Dispara uma explosão comemorativa de emojis a partir do centro da tela.
     * Usada quando o quiz revela a resposta correta.
     * @param {Object} config
     * @param {string[]} config.emojis - Emojis a sortear para a explosão
     * @param {number} config.amount - Quantidade de emojis na explosão
     */
    burst(config = {}) {
        const {
            emojis = ["🎉", "✨", "🥳", "⭐"],
            amount = 24
        } = config;

        for (let i = 0; i < amount; i++) {
            const emoji = emojis[Math.floor(Math.random() * emojis.length)];
            const element = document.createElement("div");

            element.className = "burst-emoji";
            element.textContent = emoji;

            // Direção e distância aleatórias para cada emoji se espalhar
            const angle = Math.random() * 360;
            const distance = 110 + Math.random() * 190;
            const dx = Math.cos((angle * Math.PI) / 180) * distance;
            const dy = Math.sin((angle * Math.PI) / 180) * distance;
            const duration = 0.7 + Math.random() * 0.5;
            const delay = Math.random() * 0.15;

            element.style.setProperty("--dx", `${dx}px`);
            element.style.setProperty("--dy", `${dy}px`);
            element.style.animationDuration = `${duration}s`;
            element.style.animationDelay = `${delay}s`;

            // Remove o elemento sozinho assim que a animação da explosão termina
            element.addEventListener("animationend", () => element.remove());

            this.burstContainer.appendChild(element);
        }
    }
}