# MCStatusX v0.2.0

A **transparent, zero-dependency** Python library for checking Minecraft server status —  
Java Edition & Bedrock Edition — with a built-in CLI tool.

> **The server decides what you see. MCStatusX never invents data.**

---

## What's new in 0.2.0

- **Fixed VarInt encoding** — proper SLP handshake, works with all hostnames
- **Fixed Bedrock parsing** — full RakNet `Unconnected Pong` packet parsing (no more raw text decode)
- **Retry support** — `ping(..., retries=2)` on timeout
- **`ping_many()`** — ping a list of servers concurrently (ThreadPoolExecutor)
- **MOTD cleaning** — `§` color/format codes stripped automatically
- **`favicon_bytes()`** — decode server favicon to raw PNG bytes
- **`Status.to_dict()` / `Status.to_json()`** — serialization support
- **`__repr__`** on all models — proper debug output
- **Richer error types** — `PacketError`, `ProtocolError` with clear messages
- **CLI tool** — `mcstatusx` command, use from terminal without writing code

---

## Installation

```bash
git clone https://github.com/TerAlone6300/MCStatusX.git
cd MCStatusX
pip install -e .
```
or
```bash
pip install mcstatusx
```
---

## CLI Usage

After install, `mcstatusx` is available as a terminal command.

```bash
# Full info (java, default port 25565)
mcstatusx play.example.com

# Specific port
mcstatusx play.example.com:24299

# Bedrock edition
mcstatusx play.example.com:19132 -v bedrock

# Get specific fields only
mcstatusx play.example.com:24299 -g motd
mcstatusx play.example.com:24299 -g motd playerlist
mcstatusx play.example.com:24299 -g playerlist -v java
mcstatusx play.example.com:27812 -g maxplayers -v bedrock

# JSON output
mcstatusx play.example.com --json

# Custom timeout + retries
mcstatusx play.example.com -t 5 --retries 3
```

### Available `-g` fields

| Field        | Description                                    |
|--------------|------------------------------------------------|
| `motd`       | Server description (§ codes stripped)          |
| `version`    | Version name + protocol number                 |
| `players`    | `online/max` count                             |
| `playerlist` | Player sample list (if server exposes it)      |
| `maxplayers` | Max player slots only                          |
| `ping`       | Latency in ms                                  |
| `favicon`    | Whether the server has a favicon               |
| `json`       | Full JSON dump                                 |

---

## Python API

### Basic ping

```python
import mcstatusx

# Java Edition
status = mcstatusx.ping("play.example.com", 25565)
print(status.online)           # True
print(status.motd)             # Plain text, § codes stripped
print(status.version.name)     # "Paper 1.21.4"
print(status.version.protocol) # 769
print(status.players.online)   # 42
print(status.players.max)      # 100
for p in status.players.sample:
    print(p.name, p.uuid)
print(status.ping, "ms")       # 34 ms
print(status.favicon)          # base64 PNG string or None

# Bedrock Edition
status = mcstatusx.ping("play.example.com", 19132, edition="bedrock")
print(status.motd)
print(status.players.online, "/", status.players.max)
```

### Retry on timeout

```python
status = mcstatusx.ping("play.example.com", retries=3, timeout=5)
```

### Ping multiple servers at once

```python
targets = [
    "play.example.com:25565",
    "play.mccisland.net",
    ("192.168.1.10", 25565),
]

results = mcstatusx.ping_many(targets)

for address, result in results.items():
    if isinstance(result, mcstatusx.MCStatusError):
        print(f"{address}: OFFLINE — {result.message}")
    else:
        print(f"{address}: {result.players.online}/{result.players.max} players, {result.ping}ms")
```

### Serialization

```python
status = mcstatusx.ping("play.example.com")
print(status.to_dict())   # Python dict
print(status.to_json())   # JSON string (pretty-printed)
```

### Favicon

```python
status = mcstatusx.ping("play.example.com")
if status.favicon:
    png_bytes = status.favicon_bytes()
    with open("server_icon.png", "wb") as f:
        f.write(png_bytes)
```

---

## Error Handling

```python
import mcstatusx

try:
    status = mcstatusx.ping("play.example.com")
except mcstatusx.ResolveError:
    print("Could not resolve hostname")
except mcstatusx.TimeoutError:
    print("Connection timed out")
except mcstatusx.ProtocolError:
    print("Unexpected protocol response")
except mcstatusx.PacketError:
    print("Malformed packet from server")
except mcstatusx.OfflineError:
    print("Server is offline")
except mcstatusx.MCStatusError as e:
    print("Other error:", e.message)
```

---

## What MCStatusX does NOT do

- ❌ Does NOT log into servers
- ❌ Does NOT authenticate players
- ❌ Does NOT bypass online-mode
- ❌ Does NOT generate or guess UUIDs
- ❌ Does NOT scrape Mojang or Microsoft APIs

If a server hides data, MCStatusX respects that.

---

## License

MIT License.
