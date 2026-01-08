# MCStatusX

MCStatusX is a **transparent Python library** for checking Minecraft server status  
(Java Edition & Bedrock Edition), built with one simple rule:

> **The server decides what you see. MCStatusX never invents data.**

No login.  
No UUID guessing.  
No external APIs.

Just protocol-level status queries.

---

## Features

### Java Edition
- Server online / offline
- Version name & protocol
- MOTD (raw server response)
- Online players / max players
- Player sample list **if the server provides it**
- Ping (latency)

### Bedrock Edition (MCPE)
Uses the official UDP ping protocol and retrieves **only what Bedrock servers expose**:
- MOTD
- Version string
- Online players / max players
- Ping

If Bedrock does not provide a field, MCStatusX does not fake it.

---

## What MCStatusX Does NOT Do

To avoid any misunderstanding:

- ❌ Does NOT log into servers
- ❌ Does NOT authenticate players
- ❌ Does NOT bypass online-mode
- ❌ Does NOT generate or guess UUIDs
- ❌ Does NOT scrape Mojang or Microsoft APIs

If a server hides data, MCStatusX respects that.

---

## Installation

Local / development install:

```bash
git clone https://github.com/TerAlone6300/MCStatusX.git
cd MCStatusX
pip install -e .
```

---

## Quick Start

### Java Edition

```python
import mcstatusx

status = mcstatusx.ping("play.example.com", 25565)

print(status.online)
print(status.version.name)
print(status.players.online, "/", status.players.max)
print(status.players.sample)
print(status.ping, "ms")
```

---

### Bedrock Edition (MCPE)

```python
import mcstatusx

status = mcstatusx.ping("play.example.com", 19132, edition="bedrock")

print(status.motd)
print(status.players.online, "/", status.players.max)
print(status.ping, "ms")
```

---

## Error Handling

All errors are exposed directly via the mcstatusx namespace.

```python
import mcstatusx

try:
    mcstatusx.ping("invalid.host")
except mcstatusx.ResolveError:
    print("Failed to resolve hostname")
except mcstatusx.TimeoutError:
    print("Connection timed out")
except mcstatusx.MCStatusError as e:
    print(e)
```

Common errors:
- Failed to resolve hostname
- Connection timed out
- Server is offline
- Protocol handshake failed

---

## Transparency Guarantee

MCStatusX:
- Sends only status handshake packets
- Never logs in or authenticates
- Never fabricates UUIDs or player data
- Displays exactly what the server returns

If you doubt it — read the source.

---

## License

MIT License.

---

## Disclaimer

MCStatusX is a **status query tool**, not a hacking utility.

Any misuse of this software is not supported and is the responsibility of the user.
