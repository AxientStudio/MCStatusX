# MCStatusX

MCStatusX is a **transparent, Python-based Minecraft server status library** inspired by services like mcstatus.io, but built with one clear goal:

> **Show exactly what the Minecraft server sends back — nothing more, nothing hidden.**

No login.  
No fake players.  
No “magic UUID generation”.

Just protocol.

---

## What MCStatusX Does

MCStatusX queries a Minecraft server using the **official Server List Ping (SLP) protocol** and returns the raw information that the server itself provides.

It can retrieve:

- Server online/offline status
- Server version and protocol
- MOTD (raw + formatted)
- Max players / online players
- Player sample list (names + UUIDs **if the server provides them**)
- Ping / latency
- Clear, human-readable error reasons

---

## What MCStatusX Does NOT Do

To avoid any misunderstanding:

- ❌ Does NOT log into the server
- ❌ Does NOT impersonate a player
- ❌ Does NOT brute-force or guess UUIDs
- ❌ Does NOT bypass online-mode or authentication
- ❌ Does NOT exploit server vulnerabilities

If a server hides data, MCStatusX cannot and will not invent it.

---

## Why UUIDs Can Appear (Even on Crack Servers)

MCStatusX does **not** fetch UUIDs from Mojang or external APIs.

UUIDs appear only if:
- The server itself includes them in the SLP response
- Common on:
  - `online-mode=true` servers
  - Some crack servers that generate offline UUIDs
  - Proxies or modified server cores

If the server sends it → MCStatusX shows it  
If the server doesn’t → MCStatusX returns `None`

This is intentional and verifiable.

---

## Transparency First

MCStatusX is designed to be auditable.

- Raw packets can be inspected
- Parsed data maps directly to protocol fields
- No hidden network calls
- No third-party tracking

If you don’t trust it — read the code. That’s the point.

---

## Example Usage

```python
from mcstatusx import ping

result = ping("play.example.com", 25565)

print(result.online)
print(result.version.name)
print(result.players.online)
print(result.players.sample)