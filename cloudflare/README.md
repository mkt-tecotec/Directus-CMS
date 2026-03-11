# Cloudflare Tunnel - Directus CMS

SSL va domain routing do Cloudflare xu ly. Khong can Nginx, khong can Certbot.

```
Internet --> Cloudflare (SSL) --> Tunnel --> localhost:8055 (Directus)
```

---

## Option A: cloudflared chay systemd tren VPS (pho bien hon)

```bash
# Cai cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
dpkg -i cloudflared.deb

# Dang nhap va tao tunnel
cloudflared tunnel login
cloudflared tunnel create directus-cms

# Copy config
mkdir -p ~/.cloudflared
cp tunnel-config.yml ~/.cloudflared/config.yml
# Chinh TUNNEL_ID trong file config

# Tao DNS record (tu dong)
cloudflared tunnel route dns directus-cms cms.tecotec.top

# Chay nhu service
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
systemctl status cloudflared
```

---

## Option B: cloudflared chay trong Docker Compose

Them vao docker/docker-compose.yml:

```yaml
  cloudflared:
    image: cloudflare/cloudflared:latest
    container_name: directus-cloudflared
    restart: unless-stopped
    command: tunnel --no-autoupdate run --token ${CLOUDFLARE_TUNNEL_TOKEN}
    depends_on:
      - directus
    networks:
      - directus-net
```

Them vao .env:
```
CLOUDFLARE_TUNNEL_TOKEN=<TOKEN_TU_CLOUDFLARE_DASHBOARD>
```

Lay token: Cloudflare Dashboard > Zero Trust > Networks > Tunnels > Create tunnel > chon Docker > copy token.

Trong Tunnel config tren dashboard, set service la: `http://directus:8055`
(dung ten container thay vi localhost vi cung network Docker)

---

## Kiem tra tunnel hoat dong

```bash
# Option A
systemctl status cloudflared
cloudflared tunnel info directus-cms

# Option B
docker compose logs cloudflared
```

Truy cap https://cms.tecotec.top - neu thay Directus login page la OK.
