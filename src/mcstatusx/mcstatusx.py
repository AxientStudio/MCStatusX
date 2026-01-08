import socket
from .client import ping_java
from .bedrock import ping_bedrock
from .models import *
from .errors import *


def ping(host, port=25565, edition="java", timeout=3):
    try:
        if edition == "bedrock":
            data = ping_bedrock(host, port, timeout)
            return Status(
                online=True,
                motd=data["motd"],
                version=Version(data["version"]),
                players=Players(data["players"], data["max_players"]),
                ping=data["ping"],
                raw=data,
            )

        raw, ping_ms = ping_java(host, port, timeout)
        players = raw.get("players", {})
        return Status(
            online=True,
            version=Version(**raw.get("version", {})),
            players=Players(
                players.get("online", 0),
                players.get("max", 0),
                players.get("sample"),
            ),
            motd=raw.get("description"),
            ping=ping_ms,
            raw=raw,
        )

    except socket.gaierror:
        raise ResolveError()
    except socket.timeout:
        raise TimeoutError()
    except Exception:
        raise OfflineError()