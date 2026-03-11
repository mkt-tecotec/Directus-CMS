# Cloudflare Tunnel - Directus CMS

SSL và domain routing do Cloudflare xử lý. Không cần Nginx, không cần Certbot.

```
Internet --> Cloudflare (SSL) --> Tunnel --> localhost:8055 (Directus)
```

---

## Option A: cloudflared chạy systemd trên VPS (phổ biến hơn)

```bash
# Cài cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cloudflared.deb
dpkg -i cloudflared.deb

# Đăng nhập và tạo tunnel
cloudflared tunnel login
cloudflared tunnel create directus-cms

# Copy config
mkdir -p ~/.cloudflared
cp /opt/directus/cloudflare/tunnel-config.yml ~/.cloudflared/config.yml
# Chỉnh TUNNEL_ID trong file config

# Tạo DNS record (tự động)
cloudflared tunnel route dns directus-cms cms.tecotec.top

# Chạy như service
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
systemctl status cloudflared
```

---

## Option B: cloudflared chạy trong Docker Compose

Bỏ comment phần `cloudflared` trong `docker/docker-compose.yml`, sau đó thêm vào `.env`:

```
CLOUDFLARE_TUNNEL_TOKEN=<TOKEN_TỪ_CLOUDFLARE_DASHBOARD>
```

Lấy token: Cloudflare Dashboard > Zero Trust > Networks > Tunnels > Create tunnel > chọn Docker > copy token.

Trong Tunnel config trên dashboard, set service là: `http://directus:8055`  
(dùng tên container thay vì localhost vì cùng Docker network)

---

## Kiểm tra tunnel hoạt động

```bash
# Option A
systemctl status cloudflared
cloudflared tunnel info directus-cms

# Option B
docker compose logs cloudflared
```

Truy cập https://cms.tecotec.top - nếu thấy Directus login page là OK.
