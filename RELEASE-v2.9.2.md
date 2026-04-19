# TSi MUSIC v2.9.2 — Release Notes

**Data:** 2026-04-19
**Status:** ✅ Deployed & Validated
**Acesso:** https://100.86.64.1:8443/

---

## Resumo

Deploy final do TSi MUSIC v2.9.2 com tema premium completo, traduções pt_BR aprimoradas e auditoria de segurança.

---

## Commits

| Hash | Descrição |
|------|-----------|
| `fe9d9f4` | TSi MUSIC v2.9.2: Premium theme + pt_BR translations + CSS enhancements |
| `ed895c6` | chore: security audit fix - reduced vulnerabilities from 30 to 12 |
| `c973667` | chore: add npm override for vue-audio-better sub-dep |
| `8f45fb4` | style: fix vue/require-default-prop warnings (3) |
| `3c5490d` | cleanup: remove unused assets (logo.png, icon.png, flac_small.png) |

---

## Validação

- ✅ 127/127 testes passando
- ✅ Build funcional (~64ms)
- ✅ Deploy ativo (container up 6+ horas)
- ✅ Monitoramento local ativo
- ✅ 3 systemd timers configurados

## Segurança

- Vulnerabilidades reduzidas de 30 para 10 (todas em devDependencies)
- Override aplicado para vue-audio-better

## Traduções

- pt_BR: 1471/1532 chaves (96%)
- 61 termos técnicos/gêneros mantidos em inglês

## Próximos Passos

1. Configurar GH_TOKEN para push automático ao GitHub
2. Resolver 10 vulnerabilidades restantes em devDependencies
3. Corrigir 3 warnings de lint (vue/require-default-prop)
4. Implementar novas features ou melhorias de UX
