# ─────────────────────────────────────────────
#  client.py  —  Finestra Pygame del giocatore
#
#  Avvio locale:  python client.py
#  Con Tailscale: python client.py 100.x.x.x
# ─────────────────────────────────────────────

import pygame
import socket
import threading
import json
import sys
import time

from config import *
from hud import draw_hud


def build_fonts() -> dict:
    """Costruisce il dizionario dei font."""
    pygame.font.init()
    mono = "Courier New"
    return {
        "title":  pygame.font.SysFont(mono, 54, bold=True),
        "large":  pygame.font.SysFont(mono, 36, bold=True),
        "med":    pygame.font.SysFont(mono, 22, bold=True),
        "small":  pygame.font.SysFont(mono, 18),
        "tiny":   pygame.font.SysFont(mono, 14),
    }


class GameClient:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host      = host
        self.port      = port
        self.player_id: str | None  = None
        self.state:     dict | None = None
        self.sock       = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running    = True
        self._last_msg: str = ""          # feedback azione
        self._lock      = threading.Lock()

    # ── Connessione ──────────────────────────────────────────────────

    def connect(self):
        print(f"[CLIENT] Connessione a {self.host}:{self.port} ...")
        try:
            self.sock.connect((self.host, self.port))
        except ConnectionRefusedError:
            print("[CLIENT] ✗ Impossibile connettersi. Il server è avviato?")
            sys.exit(1)

        t = threading.Thread(target=self._receive_loop, daemon=True)
        t.start()

        # Aspetta l'assegnazione del player ID
        deadline = time.time() + 10
        while self.player_id is None:
            if time.time() > deadline:
                print("[CLIENT] ✗ Timeout: server non risponde")
                sys.exit(1)
            time.sleep(0.05)
        print(f"[CLIENT] Connesso come {self.player_id}")

    # ── Loop di ricezione (thread) ───────────────────────────────────

    def _receive_loop(self):
        buffer = ""
        while self.running:
            try:
                chunk = self.sock.recv(8192).decode("utf-8", errors="ignore")
                if not chunk:
                    break
                buffer += chunk
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        msg = json.loads(line)
                        self._handle_message(msg)
                    except json.JSONDecodeError:
                        pass
            except (ConnectionResetError, OSError):
                break

    def _handle_message(self, msg: dict):
        mtype = msg.get("type")
        if mtype == "assign":
            self.player_id = msg["player_id"]
        elif mtype == "state":
            with self._lock:
                self.state = msg["data"]
        elif mtype == "action_result":
            self._last_msg = ("✅ " if msg.get("ok") else "❌ ") + msg.get("msg", "")

    # ── Invio azioni ─────────────────────────────────────────────────

    def send_action(self, action: dict):
        try:
            self.sock.sendall((json.dumps(action) + "\n").encode("utf-8"))
        except OSError:
            pass

    # ── Game loop Pygame ─────────────────────────────────────────────

    def run(self):
        pygame.init()
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f"MoneyWars — {self.player_id}")
        clock  = pygame.time.Clock()
        fonts  = build_fonts()

        # Schermata di attesa
        self._waiting_screen(screen, fonts)

        # Loop principale
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self._handle_key(event.key)

            screen.fill(C_BG)

            with self._lock:
                current_state = self.state

            if current_state:
                draw_hud(screen, current_state, self.player_id, fonts)
                self._draw_feedback(screen, fonts)
            else:
                txt = fonts["med"].render("In attesa del server...", True, C_DIM)
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, SCREEN_HEIGHT // 2))

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        self.sock.close()

    def _waiting_screen(self, screen, fonts):
        """Mostra schermata di attesa finché il secondo giocatore non si connette."""
        while True:
            with self._lock:
                st = self.state
            if st and st.get("running"):
                break

            screen.fill(C_BG)
            title = fonts["large"].render("MoneyWars", True, C_GOLD)
            pid   = fonts["med"].render(f"Sei: {self.player_id}", True, _player_color(self.player_id))
            wait  = fonts["small"].render("In attesa dell'altro giocatore...", True, C_DIM)
            screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 200))
            screen.blit(pid,   (SCREEN_WIDTH // 2 - pid.get_width()   // 2, 270))
            screen.blit(wait,  (SCREEN_WIDTH // 2 - wait.get_width()  // 2, 320))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()

            pygame.display.flip()
            pygame.time.wait(100)

    def _draw_feedback(self, screen, fonts):
        if not self._last_msg:
            return
        txt = fonts["tiny"].render(self._last_msg[:60], True, C_TEXT)
        screen.blit(txt, (20, SCREEN_HEIGHT - 220))

    def _handle_key(self, key):
        """Gestisce gli input da tastiera — da espandere con i moduli."""
        # Placeholder: test di azione "earn" per P1 e P2
        if key == pygame.K_t:
            self.send_action({"type": "earn", "amount": 500, "source": "test"})


def _player_color(pid):
    return C_P1 if pid == "P1" else C_P2


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else SERVER_HOST
    c = GameClient(host=host)
    c.connect()
    c.run()
