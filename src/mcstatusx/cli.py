"""
mcstatusx CLI — ping Minecraft servers from the terminal.

Usage:
  mcstatusx <host>                         Ping host:25565 (java)
  mcstatusx <host>:<port>                  Ping host:port  (java)
  mcstatusx <host>:<port> -v bedrock       Bedrock edition
  mcstatusx <host>:<port> -g motd          Show only MOTD
  mcstatusx <host>:<port> -g motd players  Show MOTD + player count

Available -g fields:
  motd         Server description
  version      Server version name + protocol
  players      Online/max player count
  playerlist   List of players in sample (if server provides)
  maxplayers   Max player slots
  ping         Latency in ms
  favicon      Whether server has a favicon
  json         Full JSON dump

Examples:
  mcstatusx play.hypixel.net
  mcstatusx eu1.freegamehost.xyz:24299 -g motd playerlist
  mcstatusx eu1.freegamehost.xyz:24299 -g playerlist -v java
  mcstatusx eu1.freegamehost.xyz:27812 -g maxplayers -v bedrock
"""

from __future__ import annotations

import argparse
import sys

from . import ping
from .errors import MCStatusError


# ── ANSI colours ─────────────────────────────────────────────────────────────

def _c(code: str, text: str) -> str:
    """Wrap text in an ANSI colour code (auto-disabled if not a TTY)."""
    if not sys.stdout.isatty():
        return text
    return f"\033[{code}m{text}\033[0m"

GREEN  = lambda t: _c("32", t)
YELLOW = lambda t: _c("33", t)
CYAN   = lambda t: _c("36", t)
RED    = lambda t: _c("31", t)
BOLD   = lambda t: _c("1",  t)
DIM    = lambda t: _c("2",  t)


# ── Field printers ────────────────────────────────────────────────────────────

def _print_all(status, address: str) -> None:
    """Pretty-print everything."""
    print(BOLD(f"\n  {GREEN('●')} {address}  {DIM(f'({status.edition})')}"))
    print(f"  {'MOTD':<12} {status.motd or DIM('(none)')}")
    if status.version:
        ver = status.version.name or "?"
        proto = f"  {DIM(f'protocol {status.version.protocol}')}" if status.version.protocol else ""
        print(f"  {'Version':<12} {ver}{proto}")
    if status.players:
        print(f"  {'Players':<12} {CYAN(str(status.players.online))} / {status.players.max}")
        if status.players.sample:
            names = ", ".join(p.name for p in status.players.sample)
            print(f"  {'Sample':<12} {names}")
    print(f"  {'Ping':<12} {YELLOW(str(status.ping) + ' ms')}")
    fav = GREEN("yes") if status.favicon else DIM("no")
    print(f"  {'Favicon':<12} {fav}")
    print()


def _print_fields(status, fields: list[str]) -> None:
    """Print only the requested fields."""
    for field in fields:
        field = field.strip().lower()
        if field == "motd":
            print(status.motd or "")
        elif field == "version":
            if status.version:
                proto = f" (protocol {status.version.protocol})" if status.version.protocol else ""
                print(f"{status.version.name or '?'}{proto}")
        elif field == "players":
            if status.players:
                print(f"{status.players.online}/{status.players.max}")
        elif field == "playerlist":
            if status.players and status.players.sample:
                for p in status.players.sample:
                    print(p.name)
            else:
                print(DIM("(no sample provided by server)"))
        elif field in ("maxplayers", "maxplayer"):
            if status.players:
                print(status.players.max)
        elif field == "ping":
            print(f"{status.ping} ms")
        elif field == "favicon":
            print("yes" if status.favicon else "no")
        elif field == "json":
            print(status.to_json())
        else:
            print(RED(f"Unknown field: {field!r}"), file=sys.stderr)


# ── Argument parsing ──────────────────────────────────────────────────────────

def _parse_address(addr: str) -> tuple[str, int]:
    """Parse 'host', 'host:port', or 'ip:port' into (host, port)."""
    # Handle IPv6 [::1]:port
    if addr.startswith("["):
        if "]:" in addr:
            host, port_str = addr[1:].split("]:", 1)
            return host, int(port_str)
        return addr[1:addr.index("]")], 25565

    if ":" in addr:
        parts = addr.rsplit(":", 1)
        if parts[1].isdigit():
            return parts[0], int(parts[1])

    return addr, None  # port=None → default by edition


def main():
    parser = argparse.ArgumentParser(
        prog="mcstatusx",
        description="Ping a Minecraft server from the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "address",
        help="Server address, e.g. play.example.com or play.example.com:25565",
    )
    parser.add_argument(
        "-g", "--get",
        nargs="+",
        metavar="FIELD",
        help="Fields to show: motd version players playerlist maxplayers ping favicon json",
    )
    parser.add_argument(
        "-v", "--version-edition",
        dest="edition",
        choices=["java", "bedrock"],
        default="java",
        help="Server edition (default: java)",
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=3.0,
        metavar="SECONDS",
        help="Connection timeout in seconds (default: 3)",
    )
    parser.add_argument(
        "--retries",
        type=int,
        default=1,
        metavar="N",
        help="Retry attempts on timeout (default: 1)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output full status as JSON (overrides -g)",
    )

    args = parser.parse_args()

    host, port = _parse_address(args.address)

    # Default ports
    if port is None:
        port = 19132 if args.edition == "bedrock" else 25565

    address_display = f"{host}:{port}"

    try:
        status = ping(host, port, edition=args.edition, timeout=args.timeout, retries=args.retries)
    except MCStatusError as e:
        print(RED(f"✖  {address_display}  —  {e.message}"), file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(status.to_json())
        return

    if args.get:
        _print_fields(status, args.get)
    else:
        _print_all(status, address_display)


if __name__ == "__main__":
    main()
