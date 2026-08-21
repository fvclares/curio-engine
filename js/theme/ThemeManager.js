export class ThemeManager {

    constructor(themes = {}) {

        this.themes = themes;

    }


    get(category) {

        const defaultTheme = {

            emoji: "❓",

            primary: "#52d6b5",

            secondary: "#1fb690",

            background: "default",

            floatingEmojis: [
                "⭐"
            ],

            animation: {

                type: "diagonalFloat",

                amount: 8,

                speed: 8

            },

            answerMarkers: [
                "#FF595E",
                "#1982C4",
                "#8AC926",
                "#FFCA3A"
            ]

        };


        return {

            ...defaultTheme,

            ...(this.themes[category] ?? {})

        };

    }


    getFloatingEmojis(category) {

        return this.get(category).floatingEmojis;

    }


    getAnimation(category) {

        return this.get(category).animation;

    }


    setThemes(themes) {

        this.themes = themes;

    }


}