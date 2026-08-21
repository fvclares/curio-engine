# 🔧 Guia de Diagnóstico - Áudio não funciona

## Checklist de Verificação

### 1. **Verificar no Console do Navegador (F12)**
```
- Abra Developer Tools (F12)
- Vá em Console
- Procure por logs com [VoiceManager] e [Engine]
```

### 2. **Verificar Suporte de Voice Synthesis**
No console do navegador, execute:
```javascript
window.__DEBUG__.listVoices()
```

Você deve ver algo como:
```
[VoiceManager] Vozes disponíveis:
  0: Google US English (en-US)
  1: Google Português Brasil (pt-BR)
  ...
```

### 3. **Testar Fala Manualmente**
No console, execute:
```javascript
window.__DEBUG__.testSpeak()
```

Você deve ouvir: "Teste de síntese de voz em português"

### 4. **Problemas Comuns**

#### ❌ Problema: Nenhuma voz pt-BR
**Causa**: Navegador não tem voz portuguesa
**Solução**: 
- Chrome: Adicionar voz pt-BR em settings
- Firefox: Verificar extensões de voz
- Fallback automático para voz padrão do navegador (já implementado)

#### ❌ Problema: "Falando..." mas sem som
**Causa**: Volume do sistema em mudo, speaker não funcionando
**Solução**:
- Verificar volume do sistema
- Testar som em outro site (YouTube)
- Verificar se speakers estão conectados

#### ❌ Problema: Console mostra erro "speech synthesis error"
**Causa**: Bug na síntese de voz do navegador
**Solução**:
- Atualizar navegador
- Desabilitar extensões
- Testar em outro navegador

#### ❌ Problema: Timer aparece mas pergunta não é falada
**Causa**: Voice manager não está recebendo a pergunta
**Solução**:
- Verificar se `question.prompt` tem texto
- Recarregar a página
- Limpar cache do navegador

### 5. **Verificar Estado do Engine**
No console, execute:
```javascript
window.__DEBUG__.engine.getState()
```

Sequência esperada:
- LOADING → QUESTION → SPEAKING_QUESTION → WAITING → ANSWER → SPEAKING_ANSWER → EXPLANATION → SPEAKING_EXPLANATION → NEXT → QUESTION (loop)

### 6. **Logs de Debug Completos**
O console agora mostra:
```
[App] SpeechSynthesis suportado: true
[VoiceManager] 10 vozes disponíveis
[VoiceManager] Voz pt-BR encontrada: Google Português Brasil
[App] Iniciando aplicação...
[Engine] Iniciando...
[Engine] 5 perguntas carregadas
[Engine] Exibindo pergunta 1: Which planet is known as the Red Planet?...
[Engine] Falando pergunta...
[VoiceManager] Iniciando síntese: Which planet is known as the Red Planet?...
[VoiceManager] Síntese concluída
[Engine] Iniciando timer...
[App] Evento: timer started
...
```

## Navegadores Testados

| Navegador | Suporte | Status |
|-----------|---------|--------|
| Chrome | ✅ Excelente | Melhor suporte, várias vozes |
| Edge | ✅ Excelente | Baseado em Chromium |
| Firefox | ✅ Bom | Suporte básico, menos vozes |
| Safari | ✅ Bom | Principalmente vozes en-US |
| Opera | ✅ Excelente | Mesmo do Chrome |

## Solução Rápida

Se o áudio ainda não funcionar:

1. **Recarregar página** (Ctrl+F5 ou Cmd+Shift+R)
2. **Fechar outras abas com áudio** (podem bloquear síntese)
3. **Testar em navegador diferente** (Chrome ou Edge)
4. **Verificar volume do sistema**
5. **Desabilitar extensões de navegador** (podem bloquear áudio)

## Alternativa: Desabilitar Voice (temporariamente)

Se precisar desabilitar a síntese de voz para debug, no console:
```javascript
window.__DEBUG__.engine.isAutomatic = false
```

Assim o quiz funciona sem tentar falar.
