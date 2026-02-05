# System Setup
## What’s the most reliable way to hook up a home server to a domain with zero (or near-zero) interruption
If you truly mean “no interruption,” you need redundancy (power + internet) and a setup that survives ISP IP changes. Below are practical, vendor-specific options from simplest to most resilient.
### Option A (most reliable for typical home ISPs): Cloudflare DNS + Cloudflare Tunnel (no port forwarding)
This avoids inbound firewall rules, works even behind CGNAT, and keeps services reachable if your public IP changes.
**What to buy / use**
- Domain + DNS: Cloudflare Registrar + Cloudflare DNS (or transfer DNS to Cloudflare)
- Tunnel software: `cloudflared` on the server (or on a small always-on box like a Raspberry Pi)
**To-dos**
1. Buy a domain at Cloudflare (or move your domain’s nameservers to Cloudflare DNS).
2. In Cloudflare Dashboard:
   - Add your zone (domain).
   - Turn on proxy (orange cloud) for your app hostnames (you’ll point them to the tunnel).
3. Install `cloudflared` on the home server (or a dedicated “edge” machine on your LAN).
4. Create a tunnel and map hostnames to internal services:
   - `app.yourdomain.com` → `http://192.168.1.10:8080`
   - `ssh.yourdomain.com` → `ssh://192.168.1.10:22` (or keep SSH off the internet and use Cloudflare Access)
5. Lock it down:
   - Use Cloudflare Access (SSO/OTP) for admin panels.
   - Keep your router ports closed; no public 80/443 forwarding needed.
6. Add external monitoring:
   - UptimeRobot or Better Stack checks for `https://app.yourdomain.com/health`.
### Option B (direct inbound access): Static IP + Cloudflare DNS + reverse proxy
This is straightforward, but reliability depends heavily on your ISP. It’s best with a static IP (business plan).
**What to buy / use**
- Static IP from your ISP (preferably fiber)
- DNS: Cloudflare
- Reverse proxy: Caddy (recommended) or NGINX
- TLS: Let’s Encrypt (via Caddy)
**To-dos**
1. Get a static IP from your ISP (ask specifically: “static IPv4, no CGNAT”).
2. In Cloudflare DNS, create:
   - `A` record: `yourdomain.com` → your static IP
   - `A` record: `app.yourdomain.com` → your static IP
3. On your router/firewall, forward only:
   - TCP 80 → reverse proxy
   - TCP 443 → reverse proxy
4. Run Caddy on the server (or a dedicated reverse proxy VM) to:
   - Terminate TLS
   - Route hostnames to internal services
5. Add basic protections:
   - Fail2ban (if exposing anything other than 80/443)
   - Cloudflare WAF (if proxied through Cloudflare)
### Making it “no interruption”: add redundant internet + redundant power (recommended regardless of A/B)
#### Internet failover (Dual-WAN)
**Reliable vendor picks**
- Peplink: Balance 20X / Balance One (excellent health checks + failover)
- Ubiquiti: UniFi Dream Machine SE (good dual-WAN for many setups)
- Netgate: 6100/8200 running pfSense+ (powerful, flexible)
**To-dos**
1. Add a second ISP with different last-mile tech if possible (fiber + cable is ideal).
2. Use a dual-WAN router (Peplink/Ubiquiti/Netgate) and configure:
   - WAN health checks (ping + DNS + HTTP)
   - Automatic failover (and failback delay to avoid flapping)
3. Optional but strong: add LTE/5G as a third backup:
   - Peplink MAX BR1 (LTE/5G models vary) or Cradlepoint E3000-series
4. Put your tunnel client / reverse proxy on a device that stays up through failovers (same LAN, stable DHCP reservation).
#### Power resiliency (UPS)
**Vendor picks**
- APC Smart-UPS (SMT750/SMT1000/SMT1500)
- CyberPower PFC Sinewave (for budget + sinewave output)
**To-dos**
1. Put modem + router + switch + server on the UPS (not just the server).
2. Configure graceful shutdown:
   - `apcupsd` or NUT (Network UPS Tools)
3. If outages are common, consider a small fanless router + small switch so the network stays up longer than the server.
### Hardware checklist (stable, common, easy to replace)
- Cable modem (if you’re on cable ISP): ARRIS SURFboard S33 or Motorola MB8611
- Router/firewall: Peplink Balance / UDM SE / Netgate (pick one ecosystem)
- Switch: UniFi Switch Lite / Netgear ProSAFE (simple, stable)
- Wi‑Fi (if needed): UniFi APs (U6/U7 series) or TP‑Link Omada APs
- UPS: APC Smart‑UPS SMT series
### Quick “do this and you’re done” (minimum effort, maximum uptime)
1. Cloudflare DNS + Cloudflare Tunnel for all public services.
2. Dual-WAN router (Peplink Balance 20X) with fiber/cable + LTE/5G backup.
3. APC Smart‑UPS powering modem/router/switch/server.
4. External monitoring (UptimeRobot/Better Stack) + a simple `/health` endpoint.
