# Directus CMS - TECOTEC Group MarCom

Content hub trung tâm cho hệ sinh thái 20+ brands và 16 WP sites của TMK Holdings.

**Stack:** Directus 11.x | PostgreSQL 15 | Redis 7 | Cloudflare Tunnel | Docker Compose
**Domain production:** https://cms.tecotec.top
**VPS:** Hostinger - Ubuntu 24.04 LTS - 4 vCPU - 16GB RAM

---

## Cấu trúc repo

```
├── schema/
│   └── directus-snapshot-deploy.json   # Schema chuẩn để import
├── scripts/
│   └── patch-vi-labels.py              # Viet hoa labels va notes
├── docker/
│   ├── docker-compose.yml
│   └── .env.example
├── cloudflare/
│   ├── tunnel-config.yml               # Config Cloudflare Tunnel
│   └── README.md                       # Huong dan 2 cach setup tunnel
└── docs/
    └── data-model.md                   # Mo ta mo hinh du lieu
```

---

## Kiến trúc networking

```
Internet --> Cloudflare (SSL/TLS) --> Tunnel --> localhost:8055 (Directus)
```

SSL do Cloudflare xu ly. Khong can Nginx, khong can Certbot.

Xem chi tiet: [cloudflare/README.md](cloudflare/README.md)

---

## Deploy từ đầu

### 1. Chuẩn bị server

```bash
apt update && apt upgrade -y
apt install -y curl wget git ufw
```

### 2. Cài Docker

```bash
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
apt update && apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
systemctl enable docker && systemctl start docker
```

### 3. Clone repo

```bash
cd /opt
git clone https://github.com/mkt-tecotec/Directus-CMS directus
cd /opt/directus
mkdir -p data/database data/uploads data/extensions
cp docker/.env.example .env
nano .env   # Dien day du cac gia tri CHANGE_ME
```

Tao SECRET: `openssl rand -hex 32`

### 4. Setup Cloudflare Tunnel

Xem [cloudflare/README.md](cloudflare/README.md) - co 2 option (systemd hoac Docker).

### 5. Start Directus

```bash
cd /opt/directus/docker
docker compose up -d
docker compose logs -f directus
# Doi thay: "Server started at http://0.0.0.0:8055"
```

### 6. Firewall

```bash
ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp && ufw --force enable
```

### 7. Import schema

Dang nhap Directus > My Profile > Token > Generate > Save token.

```bash
TOKEN="<STATIC_TOKEN>"

curl -X POST "https://cms.tecotec.top/schema/diff?force=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/opt/directus/schema/directus-snapshot-deploy.json \
  -o /tmp/diff-output.json

python3 -c "import json,sys; print(json.dumps(json.load(open('/tmp/diff-output.json'))['data']))" > /tmp/diff-apply.json

curl -X POST "https://cms.tecotec.top/schema/apply?force=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/diff-apply.json
```

### 8. Fix UUID fields (bat buoc sau import)

```bash
for col in brands sites authors categories tags posts posts_sites post_translations; do
  curl -s -X PATCH "https://cms.tecotec.top/fields/$col/id" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"meta":{"special":["uuid"],"hidden":true}}' && echo "OK: $col"
done
```

### 9. Viet hoa labels

```bash
nano /opt/directus/scripts/patch-vi-labels.py
# Chinh TOKEN va BASE_URL
python3 /opt/directus/scripts/patch-vi-labels.py
```

### 10. Seed data

Tao theo thu tu trong Directus admin:

1. Languages: `vi` (default=true), `en`
2. Brands: TECOTEC Group, OES, TUMIKI, CCW
3. Sites: 16 WP sites (wp_url, wp_api_user, wp_api_password)
4. Authors: Mapping thanh vien MarCom team

---

## Backup

```bash
cat > /opt/directus/backup.sh << 'SCRIPT'
#!/bin/bash
DIR=/opt/directus/backups
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $DIR
docker exec directus-db pg_dump -U directus directus | gzip > $DIR/db_$DATE.sql.gz
tar -czf $DIR/uploads_$DATE.tar.gz /opt/directus/data/uploads
find $DIR -name '*.gz' -mtime +30 -delete
SCRIPT
chmod +x /opt/directus/backup.sh
(crontab -l; echo "0 2 * * * /opt/directus/backup.sh >> /var/log/directus-backup.log 2>&1") | crontab -
```

---

## Update schema

```bash
curl -s "https://cms.tecotec.top/schema/snapshot" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['data'], indent=2))" \
  > schema/directus-snapshot-deploy.json

git add schema/ && git commit -m "chore: update schema snapshot" && git push
```

---

## Troubleshooting

| Van de | Lenh |
|---|---|
| Xem logs Directus | `docker compose logs -f directus` |
| Directus khong start | `docker compose logs database` |
| Tunnel khong hoat dong | `systemctl status cloudflared` hoac `docker compose logs cloudflared` |
| Restart | `docker compose restart` |
| Disk space | `df -h && docker system df` |

**Fix FORBIDDEN sau import schema:**

```bash
docker exec -it directus-db psql -U directus -d directus -c "
INSERT INTO directus_access (id, role, user, policy, sort)
VALUES (gen_random_uuid(), '<ADMIN_ROLE_ID>', NULL, '<ADMIN_POLICY_ID>', 1)
ON CONFLICT DO NOTHING;"
```

---

## Tai lieu

- [Mo hinh du lieu](docs/data-model.md)
- [Cloudflare Tunnel setup](cloudflare/README.md)
- [Directus v11 Docs](https://docs.directus.io)
