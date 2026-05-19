#!/usr/bin/env python3
# ─────────────────────────────────────────────
#  main.py  —  Launcher MoneyWars
#
#  Modalità:
#    1) Host   → avvia il server + la finestra P1
#               L'amico lancia:  python client.py <tuo_ip>
#
#    2) Join   → solo client, si connette all'host
#               python main.py join <ip_host>
#
#    3) Solo   → avvia server + DUE finestre locali (test)
#               python main.py solo
# ─────────────────────────────────────────────

import subprocess
import threading
import time
import sys
import os

PYTHON = sys.executable
HERE   = os.path.dirname(os.path.abspath(__file__))


def _run(script, *args):
    return subprocess.Popen(
        [PYTHON, os.path.join(HERE, script), *args]
    )


def mode_host():
    print("╔══════════════════════════════════╗")
    print("║       MoneyWars  —  HOST         ║")
    print("╚══════════════════════════════════╝")
    print("Avvio server locale...")
    srv = _run("server.py")
    time.sleep(0.8)
    print("Apertura finestra P1...")
    cli = _run("client.py", "localhost")
    print("\n📡 L'amico può connettersi con:")
    print("    python client.py <tuo_IP>")
    print("    oppure (con Tailscale): python client.py <tuo_IP_Tailscale>\n")
    try:
        cli.wait()
    finally:
        srv.terminate()


def mode_join(host_ip: str):
    print(f"Connessione a {host_ip} ...")
    _run("client.py", host_ip).wait()


def mode_solo():
    """Avvia server + due client locali per testare da soli."""
    print("Modalità SOLO — due finestre locali")
    srv = _run("server.py")
    time.sleep(0.8)
    c1 = _run("client.py", "localhost")
    time.sleep(0.3)
    c2 = _run("client.py", "localhost")
    try:
        c1.wait(); c2.wait()
    finally:
        srv.terminate()


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "host":
        mode_host()
    elif args[0] == "join":
        ip = args[1] if len(args) > 1 else input("IP dell'host: ").strip()
        mode_join(ip)
    elif args[0] == "solo":
        mode_solo()
    else:
        print("Uso:")
        print("  python main.py          → host (server + finestra P1)")
        print("  python main.py join IP  → unisciti a un host")
        print("  python main.py solo     → test locale (2 finestre)")
