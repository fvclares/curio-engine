# Curio Engine

## Product Vision

Curio Engine is a modular HTML5 engine for creating autonomous quiz experiences that can later support other interactive formats such as true-or-false, spot-the-difference, memory challenges, simulations, and educational games.

The first product target is a vertical 9:16 quiz experience that can run in a browser with no framework dependency.

## Architecture Principles

- The engine is separate from the user interface.
- The engine never manipulates HTML directly.
- Content always comes from JSON.
- Modules have one responsibility each.
- Rendering, data loading, timing, audio, voice, animation, and state flow must remain independent.
- Future experiences should reuse the same engine contracts whenever possible.

## Development Rules

- Use HTML5, CSS3, and JavaScript ES6.
- Do not use frameworks.
- Use `camelCase` for variables and functions.
- Use `PascalCase` for classes.
- Use `const` whenever possible and `let` only when reassignment is required.
- Keep comments in English.
- Keep files focused and preferably under 300 lines.
- Use JSDoc when it improves clarity.
- Define colors in `:root`.
- Avoid hardcoded questions in JavaScript.

## Roadmap

1. ✅ Foundation: create project structure, load JSON, and render the first question.
2. ✅ Loader: load and validate JSON with friendly errors.
3. ✅ Renderer: draw category, question, and alternatives only.
4. ✅ Engine: expose `start()`, `nextQuestion()`, and `finish()` without knowing HTML.
5. ✅ States: introduce `LOADING`, `QUESTION`, `WAITING`, `ANSWER`, `EXPLANATION`, `NEXT`, and `FINISHED`.
6. ✅ Random questions: choose without repeating and restart when the set ends.
7. ⏳ Shuffle: shuffle questions and alternatives without mutating original JSON.
8. ✅ Timer: add a 5-second circular timer with `START`, `UPDATE`, and `END` events.
9. ✅ Answer: highlight correct answer, gray out wrong answers, and show explanation.
10. ✅ Automatic flow: question, timer, answer, explanation, next question.
11. ✅ Voice: add `VoiceManager` using `SpeechSynthesis` behind `voice.speak(text)`.
12. ⏳ Audio: add `AudioManager` with `play()`, `stop()`, `fade()`, and `loop()`.
13. ⏳ Animations: add `AnimationManager` for fade, zoom, slide, bounce, shake, and pulse.
14. ⏳ Themes: separate engine and theme, starting with `Minimal Dark`.
15. ⏳ Components: add `QuestionCard`, `AnswerCard`, `ProgressBar`, `Timer`, `Overlay`, `Button`, and `Modal`.
16. ⏳ Editor: create a page for adding, editing, deleting, and exporting JSON.
17. ⏳ Marketplace ready: add packs for space, animals, history, movies, and absurd.
18. ⏳ Export options: add auto play, auto loop, fullscreen, mobile mode, vertical mode, and landscape mode.
19. ⏳ Performance: target Lighthouse above 95, no memory leaks, 60 FPS, and lazy loading.
20. ⏳ Commercial MVP: add README, license, documentation, examples, and API docs.

## Quality Criteria

- The project opens with Live Server or any static local server.
- JSON loads correctly.
- The first question renders.
- The browser console has no errors.
- The interface is responsive with priority for vertical mobile screens.
- The code is clean, modular, and compatible with modern browsers.
