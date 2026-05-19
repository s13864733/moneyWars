# ─────────────────────────────────────────────
#  hud.py  —  Rendering HUD della finestra
# ─────────────────────────────────────────────

import pygame
from config import *


def _panel(screen: pygame.Surface, x, y, w, h,
           color=C_PANEL, alpha=210, radius=10):
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    pygame.draw.rect(surf, (*color, alpha), (0, 0, w, h), border_radius=radius)
    screen.blit(surf, (x, y))


def _player_color(pid: str) -> tuple:
    return C_P1 if pid == "P1" else C_P2


# ── HUD principale ───────────────────────────────────────────────────

def draw_hud(screen: pygame.Surface, state: dict, my_pid: str, fonts: dict):
    players        = state.get("players", {})
    time_remaining = state.get("time_remaining", 0)
    events         = state.get("events", [])
    month          = state.get("month", 1)
    game_over      = state.get("game_over", False)
    winner         = state.get("winner")

    if game_over:
        _draw_game_over(screen, winner, players, my_pid, fonts)
        return

    _draw_background(screen)
    _draw_timer(screen, time_remaining, month, fonts)
    _draw_player_panel(screen, players.get("P1", {}), "P1", my_pid, fonts)
    _draw_player_panel(screen, players.get("P2", {}), "P2", my_pid, fonts)
    _draw_event_log(screen, events, fonts)
    _draw_menu(screen, my_pid, fonts)


def _draw_background(screen: pygame.Surface):
    screen.fill(C_BG)
    # Linea divisoria decorativa
    pygame.draw.line(screen, (*C_DIM, 80), (0, 60), (SCREEN_WIDTH, 60), 1)


def _draw_timer(screen, time_remaining, month, fonts):
    mins = int(time_remaining // 60)
    secs = int(time_remaining % 60)
    txt  = fonts["large"].render(f"{mins:02d}:{secs:02d}", True, C_TIMER)
    x    = SCREEN_WIDTH // 2 - txt.get_width() // 2
    screen.blit(txt, (x, 8))
    month_txt = fonts["small"].render(f"Mese {month}", True, C_DIM)
    screen.blit(month_txt, (SCREEN_WIDTH // 2 - month_txt.get_width() // 2, 42))


def _draw_player_panel(screen, pdata, pid, my_pid, fonts):
    is_me = pid == my_pid
    color = _player_color(pid)
    x     = 20 if pid == "P1" else SCREEN_WIDTH - 300 - 20
    y     = 75

    _panel(screen, x, y, 300, 140, radius=12)

    # Badge YOU / AVVERSARIO
    badge = "◀ YOU" if is_me else "AVVERSARIO ▶"
    badge_txt = fonts["tiny"].render(badge, True, color)
    screen.blit(badge_txt, (x + 12, y + 10))

    # Nome
    name_txt = fonts["med"].render(pid, True, color)
    screen.blit(name_txt, (x + 12, y + 28))

    # Soldi
    money = pdata.get("money", 0)
    m_str = f"${money:,.0f}"
    m_txt = fonts["large"].render(m_str, True, C_GOLD)
    screen.blit(m_txt, (x + 12, y + 60))

    # Portafoglio & business (sommario)
    port  = pdata.get("portfolio", {})
    biz   = pdata.get("businesses", [])
    info  = []
    if port:
        info.append(f"📈 {len(port)} titoli")
    if biz:
        info.append(f"🏢 {len(biz)} business")
    if not info:
        info.append("Nessun asset")
    summary = fonts["tiny"].render("  ".join(info), True, C_DIM)
    screen.blit(summary, (x + 12, y + 110))


def _draw_event_log(screen, events, fonts):
    x, y, w, h = SCREEN_WIDTH // 2 - 180, 80, 360, 140
    _panel(screen, x, y, w, h, radius=10)
    title = fonts["tiny"].render("📰 EVENTI", True, C_DIM)
    screen.blit(title, (x + 10, y + 8))
    for i, ev in enumerate(reversed(events[-5:])):
        alpha  = 255 - i * 40
        color  = (max(0, C_TEXT[0] - i*30), max(0, C_TEXT[1] - i*30), max(0, C_TEXT[2] - i*30))
        ev_txt = fonts["tiny"].render(ev[:40], True, color)
        screen.blit(ev_txt, (x + 10, y + 25 + i * 22))


def _draw_menu(screen, my_pid, fonts):
    """Menu azioni con tasti — verrà espanso modulo per modulo."""
    x, y, w, h = 20, SCREEN_HEIGHT - 200, SCREEN_WIDTH - 40, 180
    _panel(screen, x, y, w, h, radius=12)

    title = fonts["med"].render("AZIONI DISPONIBILI", True, _player_color(my_pid))
    screen.blit(title, (x + 20, y + 12))

    actions = [
        ("[C]", "Casinò",         "(prossimamente)"),
        ("[B]", "Borsa",          "(prossimamente)"),
        ("[I]", "Imprenditoria",  "(prossimamente)"),
        ("[X]", "Crypto",         "(prossimamente)"),
    ]
    col_w = (w - 40) // 4
    for i, (key, label, note) in enumerate(actions):
        cx = x + 20 + i * col_w
        k_txt = fonts["med"].render(key, True, C_GOLD)
        l_txt = fonts["small"].render(label, True, C_TEXT)
        n_txt = fonts["tiny"].render(note, True, C_DIM)
        screen.blit(k_txt, (cx, y + 45))
        screen.blit(l_txt, (cx, y + 75))
        screen.blit(n_txt, (cx, y + 105))


# ── Game Over ────────────────────────────────────────────────────────

def _draw_game_over(screen, winner, players, my_pid, fonts):
    screen.fill((8, 8, 20))

    title = fonts["title"].render("FINE PARTITA", True, C_GOLD)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80))

    if winner == "PAREGGIO":
        sub = fonts["large"].render("🤝 PAREGGIO!", True, C_WHITE)
    elif winner == my_pid:
        sub = fonts["large"].render("🏆 HAI VINTO!", True, C_P1)
    else:
        sub = fonts["large"].render("💀 HAI PERSO!", True, C_P2)
    screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, 160))

    # Risultati
    y = 250
    for pid, pdata in players.items():
        color = _player_color(pid)
        label = "(TU)" if pid == my_pid else ""
        line  = fonts["med"].render(
            f"{pid} {label}  →  ${pdata.get('money', 0):,.0f}", True, color
        )
        screen.blit(line, (SCREEN_WIDTH // 2 - line.get_width() // 2, y))
        y += 50

    hint = fonts["small"].render("Chiudi la finestra per uscire", True, C_DIM)
    screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60))
