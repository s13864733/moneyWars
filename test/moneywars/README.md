# MoneyWars 💰

Gioco multiplayer 2D: chi accumula più soldi in 5 minuti vince.

## Requisiti

```bash
pip install pygame pandas numpy
```

## Avvio

### Test locale (2 finestre sullo stesso PC)
```bash
python main.py solo
```

### Giocare in LAN
```bash
# PC 1 (host)
python main.py

# PC 2 (join)
python main.py join 192.168.1.X
```

### Giocare online con Tailscale
```bash
# Entrambi installano Tailscale (tailscale.com) e fanno login

# PC 1 (host)
python main.py

# PC 2 (join) — usa l'IP Tailscale del PC 1 (es. 100.x.x.x)
python main.py join 100.x.x.x
```

## Struttura

```
moneywars/
├── main.py          ← launcher
├── server.py        ← stato autoritativo del gioco
├── client.py        ← finestra Pygame del giocatore
├── game_state.py    ← logica pura (no rete, no rendering)
├── hud.py           ← rendering HUD
├── config.py        ← costanti
└── modules/
    ├── business.py  ← imprenditoria (WIP)
    ├── casino.py    ← casinò (TODO)
    ├── stocks.py    ← borsa (TODO)
    └── crypto.py    ← crypto (TODO)
```

## Prossimi moduli
- [ ] Casinò (Roulette, Blackjack)
- [ ] Borsa azionaria (grafici con pandas/numpy)
- [ ] Crypto (volatilità estrema)
- [ ] Imprenditoria completa
- [ ] Prestiti & eventi casuali
