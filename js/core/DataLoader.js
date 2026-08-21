export class DataLoader {
  constructor(basePath = "./data") {
    this.basePath = basePath;
  }

  async loadQuestions() {

      const data =
          await this.loadJson("questions.json");

      return this.validateQuestions(data);

  }


  async loadThemes() {

      return await this.loadJson("themes.json");

  }

  async loadJson(fileName) {

      // cache: "no-store" + timestamp na query string evitam que o navegador
      // (ou o cache do GitHub Pages) sirva uma versão antiga do JSON depois
      // que novas perguntas forem geradas/publicadas.
      const response = await fetch(
          `${this.basePath}/${fileName}?v=${Date.now()}`,
          { cache: "no-store" }
      );

      if (!response.ok){

          throw new Error(
              `Could not load ${fileName}.`
          );

      }

      return await response.json();

  }

  async loadAll() {

      const [questions, themes] = await Promise.all([
          this.loadQuestions(),
          this.loadThemes()
      ]);

      return {
          questions,
          themes
      };

  }


  validateQuestions(data) {
    if (!Array.isArray(data)) {
      throw new Error("Questions JSON must be an array.");
    }

    if (data.length === 0) {
      throw new Error("Questions JSON must include at least one question.");
    }

    data.forEach((question, index) => {
      this.validateQuestion(question, index);
    });

    return data;
  }

  validateQuestion(question, index) {
    const label = `Question ${index + 1}`;

    if (!question || typeof question !== "object") {
      throw new Error(`${label} must be an object.`);
    }

    if (typeof question.category !== "string" || question.category.trim() === "") {
      throw new Error(`${label} must include a category.`);
    }

    if (typeof question.prompt !== "string" || question.prompt.trim() === "") {
      throw new Error(`${label} must include a prompt.`);
    }

    if (!Array.isArray(question.answers) || question.answers.length < 2) {
      throw new Error(`${label} must include at least two answers.`);
    }

    question.answers.forEach((answer, answerIndex) => {
      if (typeof answer.text !== "string" || answer.text.trim() === "") {
        throw new Error(`${label}, answer ${answerIndex + 1} must include text.`);
      }

      if (typeof answer.isCorrect !== "boolean") {
        throw new Error(`${label}, answer ${answerIndex + 1} must include isCorrect.`);
      }
    });

    const correctAnswers = question.answers.filter((answer) => answer.isCorrect);

    if (correctAnswers.length !== 1) {
      throw new Error(`${label} must include exactly one correct answer.`);
    }
  }
}

