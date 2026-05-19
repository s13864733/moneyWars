# ─────────────────────────────────────────────
#  server.py  —  Server di gioco
#
#  - Aspetta 2 client (P1 e P2)
#  - Gestisce lo stato autoritativo
#  - Manda aggiornamenti a 20 tick/sec
#  - Tick mensile ogni 10 secondi reali
#
#  Avvio: python server.py
#  Multiplayer Tailscale: nessuna modifica necessaria,
#  basta che i client usino l'IP Tailscale del server.
# ─────────────────────────────────────────────

import socket
import threading
import json
import time
import sys

from config import SERVER_HOST, SERVER_PORT, NET_TICK
from game_state import GameState

MONTH_INTERVAL = 10   # secondi reali per mese di gioco


class GameServer:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT):
        self.host    = host
        self.port    = port
        self.state   = GameState()
        self.clients: dict[str, socket.socket] = {}
        self.lock    = threading.Lock()

    # ── Avvio ────────────────────────────────────────────────────────

    def start(self):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((self.host, self.port))
        srv.listen(2)
        print(f"[SERVER] In ascolto su {self.host}:{self.port} — attendo 2 giocatori...")

        player_ids = ["P1", "P2"]
        accepted   = 0

        while accepted < 2:
            conn, addr = srv.accept()
            pid = player_ids[accepted]
            self.clients[pid] = conn
            # Informa il client del suo ID
            self._send(conn, {"type": "assign", "player_id": pid})
            print(f"[SERVER] {pid} connesso da {addr}")
            t = threading.Thread(target=self._handle_client, args=(conn, pid), daemon=True)
            t.start()
            accepted += 1

        print("[SERVER] Tutti connessi! Partita in corso...")
        self.state.start()
        self._broadcast_loop()

    # ── Ricezione azioni dai client ──────────────────────────────────

    def _handle_client(self, conn: socket.socket, pid: str):
        buffer = ""
        while True:
            try:
                chunk = conn.recv(4096).decode("utf-8", errors="ignore")
                if not chunk:
                    break
                buffer += chunk
                # Un messaggio per riga
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        action = json.loads(line)
                        with self.lock:
                            result = self.state.apply_action(pid, action)
                        # Manda il risultato solo al mittente
                        self._send(conn, {"type": "action_result", **result})
                    except json.JSONDecodeError:
                        pass
            except (ConnectionResetError, BrokenPipeError, OSError):
                break
        print(f"[SERVER] {pid} disconnesso")

    # ── Broadcast dello stato ────────────────────────────────────────

    def _broadcast_loop(self):
        last_month_tick = time.time()
        tick_interval   = 1.0 / NET_TICK

        while not self.state.is_over():
            # Tick mensile
            now = time.time()
            if now - last_month_tick >= MONTH_INTERVAL:
                with self.lock:
                    self.state.monthly_tick()
                last_month_tick = now

            # Snapshot → tutti i client
            with self.lock:
                snapshot = self.state.to_dict()
            for pid, conn in list(self.clients.items()):
                self._send(conn, {"type": "state", "data": snapshot})

            time.sleep(tick_interval)

        # Stato finale
        with self.lock:
            final = self.state.to_dict()
        for conn in self.clients.values():
            self._send(conn, {"type": "state", "data": final})
        print(f"[SERVER] Partita terminata! Vincitore: {final.get('winner')}")

    # ── Utilità ──────────────────────────────────────────────────────

    @staticmethod
    def _send(conn: socket.socket, payload: dict):
        try:
            conn.sendall((json.dumps(payload) + "\n").encode("utf-8"))
        except (BrokenPipeError, OSError):
            pass


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else SERVER_HOST
    GameServer(host=host).start()
