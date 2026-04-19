# TSi MUSIC v2.9.3 — Mini Player Mode

**Data:** 2026-04-19
**Status:** ✅ Deployed
**Acesso:** https://100.86.64.1:8443/

---

## Novo: Mini Player Mode (Desktop)

- **Toggle** no player desktop para alternar entre modo completo e mini
- **Modo Mini**: mostra apenas capa + título/artista + play/pause/anterior/próxima
- **Modo Completo**: timeline, volume, controles estendidos (padrão)
- **Persistência**: preferência salva no localStorage
- **Estilo TSi MUSIC**: glassmorphism + gradiente roxo

## Commits desde v2.9.2

| Hash | Descrição |
|------|-----------|
| `def738a` | feat: add Mini Player Mode toggle for desktop |
| `ba9101f` | docs: update RELEASE-v2.9.2.md with final status |
| `3c5490d` | cleanup: remove unused assets |
| `8f45fb4` | style: fix vue/require-default-prop warnings |
| `c973667` | chore: add npm override for vue-audio-better sub-dep |
| `ed895c6` | chore: security audit fix |
| `fe9d9f4` | TSi MUSIC v2.9.2: Premium theme + pt_BR translations |

## Validação

- ✅ Build: 19.74s, 165 precache entries
- ✅ Deploy: HTTP 200 OK
- ✅ Testes: 127/127 passando
