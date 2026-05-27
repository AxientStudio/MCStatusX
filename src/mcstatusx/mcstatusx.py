from __future__ import annotations

import socket
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from .client import ping_java
from .bedrock import ping_bedrock
from .models import Status, Version, Players
from .errors import (
    MCStatusError, ResolveError, TimeoutError,
    OfflineError, ProtocolError, PacketError
)


def ping(
    host: str,
    port: int = 25565,
    edition: str = "java",
    timeout: float = 3,
    retries: int = 1,
) -> Status:
    """
    Ping a Minecraft server and return a Status object.

    Args:
        host:     Server hostname or IP.
        port:     Server port (default 25565 Java / 19132 Bedrock).
        edition:  "java" or "bedrock".
        timeout:  Socket timeout in seconds.
        retries:  Number of retry attempts on timeout (default 1 = no retry).

    Returns:
        Status object with server information.

    Raises:
        ResolveError, TimeoutError, OfflineError, ProtocolError, PacketError
    """
    last_exc: Exception | None = None

    for attempt in range(max(1, retries)):
        try:
            if edition == "bedrock":
                if port == 25565:
                    port = 19132
                data = ping_bedrock(host, port, timeout)
                return Status(
                    online=True,
                    edition="bedrock",
                    motd=data.get("motd"),
                    version=Version(
                        name=data.get("version"),
                        protocol=data.get("protocol"),
                    ),
                    players=Players(
                        online=data.get("players", 0),
                        max=data.get("max_players", 0),
                    ),
                    ping=data.get("ping"),
                    raw=data,
                )

            # Java Edition
            raw, ping_ms = ping_java(host, port, timeout)
            players_raw = raw.get("players", {})
            return Status(
                online=True,
                edition="java",
                version=Version(**raw.get("version", {})),
                players=Players(
                    online=players_raw.get("online", 0),
                    max=players_raw.get("max", 0),
                    sample=players_raw.get("sample"),
                ),
                motd=raw.get("description"),
                ping=ping_ms,
                favicon=raw.get("favicon"),
                raw=raw,
            )

        except socket.gaierror:
            raise ResolveError()
        except (socket.timeout, TimeoutError):
            last_exc = TimeoutError()
        except (ProtocolError, PacketError) as e:
            raise
        except Exception as e:
            last_exc = OfflineError()

    raise last_exc or OfflineError()


def ping_many(
    targets: List[str | tuple],
    edition: str = "java",
    timeout: float = 3,
    max_workers: int = 16,
) -> dict[str, Status | MCStatusError]:
    """
    Ping multiple servers concurrently.

    Args:
        targets:  List of "host:port" strings, or (host, port) tuples, or bare "host".
        edition:  Default edition if not specified per-target.
        timeout:  Socket timeout per server.
        max_workers: Thread pool size.

    Returns:
        Dict mapping "host:port" → Status or MCStatusError.
    """
    def _resolve(target) -> tuple[str, int, str]:
        if isinstance(target, (list, tuple)) and len(target) >= 2:
            return str(target[0]), int(target[1]), edition
        s = str(target)
        if ":" in s:
            h, p = s.rsplit(":", 1)
            return h, int(p), edition
        return s, 25565 if edition == "java" else 19132, edition

    results: dict[str, Status | MCStatusError] = {}

    def _ping(target):
        h, p, ed = _resolve(target)
        key = f"{h}:{p}"
        try:
            return key, ping(h, p, edition=ed, timeout=timeout)
        except MCStatusError as e:
            return key, e

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_ping, t): t for t in targets}
        for future in as_completed(futures):
            key, result = future.result()
            results[key] = result

    return results
