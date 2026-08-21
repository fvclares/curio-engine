# 🔴 TRAVA: Loading Curio Engine...

## Diagnóstico Passo a Passo

### 1. **Abra o Console do Navegador**
- Pressione **F12** ou **Ctrl+Shift+I**
- Vá para a aba **Console**

### 2. **Recarregue a página**
- Pressione **Ctrl+F5** (força o reload sem cache)

### 3. **Procure pelos logs**

#### ✅ Sequência Normal (sem trava):
```
[App] SpeechSynthesis suportado: true
[VoiceManager] 5 vozes disponíveis
[VoiceManager] Voz pt-BR encontrada: Google Português Brasil
[App] Iniciando aplicação...
[Engine] Iniciando...
[Engine] 5 perguntas carregadas
[Engine] Exibindo pergunta 1: Qual planeta...
[App] Evento: question
[QuestionRenderer] Renderizando pergunta: Qual planeta...
[QuestionRenderer] Pergunta renderizada com sucesso
[Engine] Falando pergunta...
[VoiceManager] Iniciando síntese de voz...
[VoiceManager] Enviando para speechSynthesis...
[VoiceManager] Síntese iniciada: Qual planeta...
```

#### ❌ Se travar, veja qual foi o último log:

**Se o último log foi `[App] Iniciando aplicação...`**
- Problema: Erro ao iniciar o Engine
- Verificar: JSON está correto?

**Se o último log foi `[Engine] Iniciando...`**
- Problema: Erro ao carregar perguntas
- Verificar: Arquivo `data/questions.json` existe?
- Solução: Abra DevTools → Network → procure por `questions.json` e veja o status

**Se o último log foi `[Engine] 5 perguntas carregadas` mas não exibe a pergunta**
- Problema: Erro ao exibir primeira pergunta
- Verificar: Console mostra erro vermelho?

**Se o último log foi `[App] Evento: question` mas não renderiza**
- Problema: Erro no renderizador
- Verificar: Há um erro vermelho no console?

**Se o último log foi `[Engine] Falando pergunta...`**
- Problema: Síntese de voz está travando
- Solução: Desabilitar voice:
  ```javascript
  window.__DEBUG__.engine.isAutomatic = false
  ```
  Depois recarrege a página

### 4. **Teste Rápido de Voice**
No console, execute:
```javascript
window.__DEBUG__.testSpeak()
```

Você deve ouvir: "Teste de síntese de voz em português"

Se não ouvir:
- Volume do sistema está em mudo?
- Speakers/fones estão conectados?
- Tente em outro navegador (Chrome/Edge funcionam melhor)

### 5. **Desabilitar Voice Temporariamente**
Para testar se é problema de voice, desabilite:
```javascript
window.__DEBUG__.engine.isAutomatic = false
```

Recarrege a página (Ctrl+F5). Se funcionar, é problema de síntese de voz.

### 6. **Erros Comuns**

#### ❌ "Cannot read property 'prompt' of undefined"
- Causa: Nenhuma pergunta foi carregada
- Solução: Verificar se `data/questions.json` é um array válido

#### ❌ "Unexpected token in JSON"
- Causa: JSON com sintaxe inválida
- Solução: Validar JSON em https://jsonlint.com/

#### ❌ "Failed to fetch"
- Causa: Arquivo `questions.json` não encontrado
- Solução: Verificar caminho relativo do arquivo

#### ❌ "TypeError: renderer.playFlipAnimation is not a function"
- Causa: Renderer não tem o método de flip
- Solução: Verificar se arquivo `QuestionRenderer.js` foi atualizado corretamente

### 7. **Limpar Cache e Recarregar**
```
1. Pressione Ctrl+Shift+Delete (ou Cmd+Shift+Delete no Mac)
2. Selecione "Cookies e dados de site armazenados"
3. Clique "Limpar dados"
4. Recarregue a página
```

## Exportar Logs para Análise

Se ainda não funcionar, copie todos os logs do console:
1. Clique no console
2. Pressione Ctrl+A para selecionar tudo
3. Pressione Ctrl+C para copiar
4. Cole em um arquivo de texto

Isso ajudará a diagnosticar o problema mais rapidamente!
