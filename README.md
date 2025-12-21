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

## Quick Start (Copy & Run)

# Install (local / dev mode)

```bash
git clone https://github.com/TerAlone6300/MCStatusX.git
cd MCStatusX
pip install -e .

# Basic Ping

```python
from mcstatusx import ping

result = ping("play.example.com", 25565)

print("Online:", result.online)
print("Version:", result.version.name)
print("Players:", result.players.online, "/", result.players.max)
print("Sample:", result.players.sample)

# Using IP with Port (x.x.x.x:port)

```python
from mcstatusx import ping

result = ping("1.2.3.4", 25565)
print(result)

> You may also pass a combined address:

```python
from mcstatusx import ping_address

result = ping_address("1.2.3.4:25565")
print(result)

# Handling Errors Explicitly

```python
from mcstatusx import ping, MCStatusError

try:
    result = ping("invalid.host", 25565)
except MCStatusError as e:
    print("Error type:", e.code)
    print("Reason:", e.message)

> Possible error messages include:
Server is offline
Connection timed out
Failed to resolve hostname
Invalid server response
Protocol handshake failed

# Transparency Demo (Raw Data)

```python
from mcstatusx import ping

result = ping("play.example.com", 25565, debug=True)

print(result.raw_request)
print(result.raw_response)

This proves:
No login packets are sent
Only SLP handshake + status request
All displayed data comes directly from the server

---

### CLI (Optional)

```bash
python -m mcstatusx play.example.com:25565

Example Output 

Status: ONLINE
Version: 1.21.1
Players: 12 / 100
Sample: Not provided by server
Ping: 42ms
