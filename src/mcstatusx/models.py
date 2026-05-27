from __future__ import annotations
import json
import re


def _strip_motd(text: str) -> str:
    """Strip Minecraft § color/format codes from MOTD."""
    if not text:
        return text
    return re.sub(r"§[0-9a-fk-or]", "", text, flags=re.IGNORECASE)


def _motd_to_plain(motd) -> str:
    """Convert raw MOTD (str or dict) to plain text."""
    if motd is None:
        return ""
    if isinstance(motd, str):
        return _strip_motd(motd)
    if isinstance(motd, dict):
        # Chat component format: {"text": "...", "extra": [...]}
        parts = []
        if "text" in motd:
            parts.append(motd["text"])
        for extra in motd.get("extra", []):
            if isinstance(extra, dict):
                parts.append(extra.get("text", ""))
            elif isinstance(extra, str):
                parts.append(extra)
        return _strip_motd("".join(parts))
    return str(motd)


class Version:
    def __init__(self, name: str | None = None, protocol: int | None = None):
        self.name = name
        self.protocol = protocol

    def __repr__(self) -> str:
        return f"Version(name={self.name!r}, protocol={self.protocol!r})"

    def to_dict(self) -> dict:
        return {"name": self.name, "protocol": self.protocol}


class Player:
    def __init__(self, name: str, uuid: str | None = None):
        self.name = name
        self.uuid = uuid

    def __repr__(self) -> str:
        return f"Player(name={self.name!r}, uuid={self.uuid!r})"

    def to_dict(self) -> dict:
        return {"name": self.name, "uuid": self.uuid}


class Players:
    def __init__(self, online: int = 0, max: int = 0, sample=None):
        self.online = online
        self.max = max
        # Normalize sample to list of Player objects
        self.sample: list[Player] = []
        if sample:
            for p in sample:
                if isinstance(p, dict):
                    self.sample.append(Player(p.get("name", "?"), p.get("id")))
                elif isinstance(p, Player):
                    self.sample.append(p)

    def __repr__(self) -> str:
        return f"Players(online={self.online}, max={self.max}, sample={self.sample!r})"

    def to_dict(self) -> dict:
        return {
            "online": self.online,
            "max": self.max,
            "sample": [p.to_dict() for p in self.sample],
        }


class Status:
    def __init__(
        self,
        online: bool = False,
        version: Version | None = None,
        players: Players | None = None,
        motd=None,
        ping: int | None = None,
        favicon: str | None = None,
        raw: dict | None = None,
        edition: str = "java",
    ):
        self.online = online
        self.version = version
        self.players = players
        self._raw_motd = motd
        self.motd = _motd_to_plain(motd)
        self.ping = ping
        self.favicon = favicon  # base64 PNG string (if server provides)
        self.raw = raw
        self.edition = edition

    def favicon_bytes(self) -> bytes | None:
        """Decode favicon base64 to raw PNG bytes."""
        if not self.favicon:
            return None
        import base64
        # Format: "data:image/png;base64,<data>"
        if "," in self.favicon:
            data = self.favicon.split(",", 1)[1]
        else:
            data = self.favicon
        return base64.b64decode(data)

    def to_dict(self) -> dict:
        return {
            "online": self.online,
            "edition": self.edition,
            "version": self.version.to_dict() if self.version else None,
            "players": self.players.to_dict() if self.players else None,
            "motd": self.motd,
            "ping": self.ping,
            "favicon": bool(self.favicon),
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)

    def __repr__(self) -> str:
        return (
            f"Status(online={self.online}, edition={self.edition!r}, "
            f"version={self.version!r}, players={self.players!r}, "
            f"motd={self.motd!r}, ping={self.ping}ms)"
        )
