export class AppContext {

    constructor() {

        this.questions = [];

        this.themes = {};

        this.currentTheme = null;

    }

    setQuestions(questions) {

        this.questions = questions;

    }

    setThemes(themes) {

        this.themes = themes;

    }

    setCurrentTheme(theme) {

        this.currentTheme = theme;

    }

}