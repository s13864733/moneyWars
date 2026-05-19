# ─────────────────────────────────────────────
#  game_state.py  —  Stato e logica di gioco
#  Nessuna dipendenza da rete o rendering.
#  Tutto ciò che modifica soldi/assets passa
#  da qui → facile da estendere con nuovi moduli.
# ─────────────────────────────────────────────

import time
import copy
from config import STARTING_MONEY, GAME_DURATION


def _empty_player(name: str) -> dict:
    return {
        "name":       name,
        "money":      float(STARTING_MONEY),
        "portfolio":  {},          # { "AAPL": qty, ... }
        "businesses": [],          # lista di business posseduti
        "debt":       0.0,         # prestiti da restituire
        "history":    [],          # log azioni per statistiche finali
    }


class GameState:
    def __init__(self):
        self.players = {
            "P1": _empty_player("P1"),
            "P2": _empty_player("P2"),
        }
        self.start_time:  float | None = None
        self.duration:    float = GAME_DURATION
        self.running:     bool  = False
        self.events:      list  = []   # eventi globali recenti
        self.month:       int   = 1    # mese di gioco (1 mese = 10 sec reali)

    # ── Controllo partita ───────────────────────────────────────────

    def start(self):
        self.start_time = time.time()
        self.running    = True
        self._add_event("🏁 La partita è iniziata! Avete 5 minuti.")

    def time_remaining(self) -> float:
        if not self.start_time:
            return self.duration
        elapsed = time.time() - self.start_time
        return max(0.0, self.duration - elapsed)

    def is_over(self) -> bool:
        return self.running and self.time_remaining() <= 0

    # ── Azioni dei giocatori ────────────────────────────────────────

    def apply_action(self, player_id: str, action: dict) -> dict:
        """
        Applica un'azione e restituisce {"ok": bool, "msg": str}.
        Ogni modulo aggiunge i propri tipi di azione qui sotto.
        """
        if player_id not in self.players:
            return {"ok": False, "msg": "Giocatore non trovato"}
        if not self.running:
            return {"ok": False, "msg": "La partita non è ancora iniziata"}

        p = self.players[player_id]
        t = action.get("type", "")

        # ── GENERICO: trasferimento diretto (usato dai moduli) ──────
        if t == "earn":
            amount = float(action.get("amount", 0))
            p["money"] += amount
            msg = f"+${amount:,.0f} ({action.get('source','?')})"
            p["history"].append(msg)
            return {"ok": True, "msg": msg}

        if t == "spend":
            amount = float(action.get("amount", 0))
            if p["money"] < amount:
                return {"ok": False, "msg": "Fondi insufficienti"}
            p["money"] -= amount
            msg = f"-${amount:,.0f} ({action.get('source','?')})"
            p["history"].append(msg)
            return {"ok": True, "msg": msg}

        # ── BORSA: compra/vendi azioni ──────────────────────────────
        if t == "buy_stock":
            stock = action.get("stock")
            qty   = int(action.get("qty", 1))
            price = float(action.get("price", 0))
            cost  = price * qty
            if p["money"] < cost:
                return {"ok": False, "msg": "Fondi insufficienti"}
            p["money"] -= cost
            p["portfolio"][stock] = p["portfolio"].get(stock, 0) + qty
            msg = f"Comprato {qty}x {stock} @ ${price:.2f}"
            p["history"].append(msg)
            return {"ok": True, "msg": msg}

        if t == "sell_stock":
            stock = action.get("stock")
            qty   = int(action.get("qty", 1))
            price = float(action.get("price", 0))
            owned = p["portfolio"].get(stock, 0)
            if owned < qty:
                return {"ok": False, "msg": f"Hai solo {owned} azioni di {stock}"}
            p["portfolio"][stock] -= qty
            if p["portfolio"][stock] == 0:
                del p["portfolio"][stock]
            p["money"] += price * qty
            msg = f"Venduto {qty}x {stock} @ ${price:.2f}"
            p["history"].append(msg)
            return {"ok": True, "msg": msg}

        # ── IMPRENDITORIA: apri business ────────────────────────────
        if t == "open_business":
            biz = action.get("business")
            cost = float(action.get("cost", 0))
            if p["money"] < cost:
                return {"ok": False, "msg": "Fondi insufficienti"}
            p["money"] -= cost
            p["businesses"].append({"name": biz, "level": 1, "opened_month": self.month})
            msg = f"Aperto: {biz}"
            p["history"].append(msg)
            return {"ok": True, "msg": msg}

        return {"ok": False, "msg": f"Azione sconosciuta: {t}"}

    # ── Tick mensile (chiamato dal server ogni 10 sec) ──────────────

    def monthly_tick(self):
        """Incassa rendite dai business, avanza il mese, genera eventi."""
        self.month += 1
        for pid, p in self.players.items():
            income = sum(self._business_income(b) for b in p["businesses"])
            if income > 0:
                p["money"] += income
                p["history"].append(f"📈 Rendita mensile: +${income:,.0f}")

    def _business_income(self, biz: dict) -> float:
        from modules.business import BUSINESS_CATALOG
        data = BUSINESS_CATALOG.get(biz["name"], {})
        return data.get("monthly_revenue", 0) * biz.get("level", 1)

    # ── Utilità ─────────────────────────────────────────────────────

    def _add_event(self, msg: str):
        self.events.append(msg)
        if len(self.events) > 6:   # tieni solo gli ultimi 6
            self.events.pop(0)

    def winner(self) -> str | None:
        """Restituisce l'id del vincitore o None se pareggio."""
        if not self.is_over():
            return None
        m1 = self.players["P1"]["money"]
        m2 = self.players["P2"]["money"]
        if m1 > m2:   return "P1"
        if m2 > m1:   return "P2"
        return "PAREGGIO"

    def to_dict(self) -> dict:
        """Snapshot serializzabile inviato ai client."""
        return {
            "players":        copy.deepcopy(self.players),
            "time_remaining": self.time_remaining(),
            "month":          self.month,
            "running":        self.running,
            "events":         list(self.events),
            "game_over":      self.is_over(),
            "winner":         self.winner(),
        }
