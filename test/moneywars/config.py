# ─────────────────────────────────────────────
#  config.py  —  Costanti globali di MoneyWars
# ─────────────────────────────────────────────

# Schermo
SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 650
FPS           = 60

# Partita
GAME_DURATION   = 300   # secondi (5 minuti)
STARTING_MONEY  = 10_000

# Rete  ← cambia SERVER_HOST con IP Tailscale per multiplayer online
SERVER_HOST = "localhost"
SERVER_PORT = 5555

# Colori UI
C_BG         = (13,  17,  35)
C_PANEL      = (25,  30,  55)
C_P1         = (80,  200, 120)   # verde
C_P2         = (220, 90,  90)    # rosso
C_GOLD       = (255, 200, 50)
C_TIMER      = (100, 180, 255)
C_TEXT       = (210, 210, 230)
C_DIM        = (100, 100, 120)
C_WHITE      = (255, 255, 255)
C_WIN_GOLD   = (255, 215, 0)

# Aggiornamenti di rete (al secondo)
NET_TICK = 20
