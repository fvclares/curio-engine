export class QuestionRenderer {
  constructor(rootElement, themeManager = null, emojiBackground = null) {
      this.rootElement = rootElement;
      this.themeManager = themeManager;
      this.emojiBackground = emojiBackground;
      this.currentAnswerElements = [];
  }

  renderStatus(message) {
    this.rootElement.replaceChildren(this.createText("p", "status-text", message));
  }

  renderError(message) {
    this.rootElement.replaceChildren(this.createText("p", "status-text error-text", message));
  }

  renderQuestion(question) {
    const card = document.createElement("article");
    card.className = "question-card";
    
    const timerPlaceholder = document.createElement("div");
    timerPlaceholder.className = "timer-placeholder";
    timerPlaceholder.id = "timerPlaceholder";

    const theme = this.themeManager
            ? this.themeManager.get(question.category)
            : null;

        if(this.emojiBackground && theme){
        this.emojiBackground.start({
            emojis: theme.floatingEmojis,
            amount: theme.animation.amount,
            speed: theme.animation.speed
        });
    }

    const primaryColor =
        theme?.primary ?? "#52d6b5";

    const categoryEmojiStart = document.createElement("div");
    categoryEmojiStart.className = "category-emoji";
    categoryEmojiStart.textContent = theme?.emoji ?? "❓";

    const category = this.createText("p", "question-category", question.category);
    category.style.backgroundColor = primaryColor;

    const categoryEmojiEnd = categoryEmojiStart.cloneNode(true);

    const categoryHeader = document.createElement("div");
    categoryHeader.className = "category-header";

    categoryHeader.append(
        categoryEmojiStart,
        category,
        categoryEmojiEnd
    );

    const answerArea = document.createElement("div");
    answerArea.className = "answer-area";

    const cardInner = document.createElement("div");
    cardInner.className = "card-inner";

    const front = document.createElement("div");
    front.className = "card-front";

    const back = document.createElement("div");
    back.className = "card-back";

    const explanationBox = document.createElement("div");
    explanationBox.className = "explanation-box";

    const explanationText = this.createText("p", "explanation-text", question.explanation ?? "");
    explanationBox.append(explanationText);

    const answerList = document.createElement("ul");
    answerList.className = "answer-list";

    this.currentAnswerElements = [];
    const shuffledAnswers = this.shuffle(question.answers);
    shuffledAnswers.forEach((answer) => {
      const answerItem = this.createText("li", "answer-card", answer.text);
      answerItem.dataset.correct = answer.isCorrect;
      this.currentAnswerElements.push(answerItem);
      answerList.append(answerItem);
    });

    front.append(answerList);
    back.append(explanationBox);
    cardInner.append(front, back);
    answerArea.append(cardInner);

    const title = this.createText("h2", "question-title", question.prompt);

    card.append(
        timerPlaceholder,
        categoryHeader,
        title,
        answerArea
    );
    this.rootElement.replaceChildren(card);
  }

  renderAnswer(isCorrect, correctAnswer) {
    this.currentAnswerElements.forEach((element) => {
      if (element.dataset.correct === "true") {
        element.classList.add("answer-correct");
      } else {
        element.classList.add("answer-wrong");
      }
    });
  }

  renderExplanation(explanation) {
      // Função atualizada apenas para virar o card, sem mexer em texto
      const cardInner =
          this.rootElement.querySelector(".card-inner");

      if (!cardInner) return;

      cardInner.classList.add("flipped");
  }

  clearExplanation() {
      // Função antiga de texto comentada
      /*
      const explanationText =
          this.rootElement.querySelector(".explanation-text");

      if (explanationText){
          explanationText.textContent="";
      }
      */

      const cardInner =
          this.rootElement.querySelector(".card-inner");

      if(cardInner){
          cardInner.classList.remove("flipped");
      }
  }

  // Retorna uma cópia embaralhada (Fisher-Yates) do array de respostas,
  // sem alterar o array original — assim a resposta correta não fica
  // sempre na mesma posição.
  shuffle(answers) {
    const shuffled = [...answers];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  createText(tagName, className, text) {
    const element = document.createElement(tagName);
    element.className = className;
    element.textContent = text;
    return element;
  }

  getCorrectAnswerText(question) {
    const correct = question.answers.find((answer) => answer.isCorrect);
    return correct ? correct.text : question.prompt;
  }
}