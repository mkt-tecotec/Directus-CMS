# Directus CMS - TECOTEC Group

Headless CMS trung tâm cho hệ sinh thái đa thương hiệu TMK Holdings.  
Stack: Directus 11 + PostgreSQL 15 + Redis 7 + Nginx + Docker.

## Kiến trúc

```
Directus CMS (cms.tecotec.top)
    └── n8n Workflow (n8n.tecotec.top)
            └── 16 WordPress sites
```

Nội dung được tạo và duyệt tại Directus, n8n tự động publish lên các WP site đích khi trạng thái chuyển sang `approved`.

---

## Cấu trúc repo

```
.
├── schema/
│   └── directus-snapshot.json   # Schema export (source of truth)
├── scripts/
│   └── patch-vi-labels.py       # Patch labels + notes tiếng Việt
├── docker/
│   ├── docker-compose.yml       # Production compose file
│   └── .env.example             # Template biến môi trường
├── nginx/
│   └── directus.conf            # Nginx reverse proxy config
└── docs/
    └── data-model.md            # Tài liệu mô hình dữ liệu đầy đủ
```

---

## Deploy lên production

### Yêu cầu

- Ubuntu 22.04 / 24.04 LTS
- Docker + Docker Compose v2
- Domain trỏ về VPS (A record)

### Bước 1: Clone repo và cấu hình env

```bash
git clone https://github.com/mkt-tecotec/Directus-CMS.git
cd Directus-CMS/docker
cp .env.example .env
nano .env   # Điền các giá trị thật
```

Các biến bắt buộc phải thay trong `.env`:

| Biến | Mô tả |
|------|-------|
| `SECRET` | Random string: `openssl rand -hex 32` |
| `DB_PASSWORD` | Mật khẩu PostgreSQL |
| `ADMIN_EMAIL` | Email admin lần đầu |
| `ADMIN_PASSWORD` | Mật khẩu admin lần đầu |
| `PUBLIC_URL` | URL công khai: `https://cms.tecotec.top` |

> Sau khi đăng nhập lần đầu, xóa `ADMIN_EMAIL` và `ADMIN_PASSWORD` khỏi `.env`.

### Bước 2: Cấu hình Nginx

```bash
sudo cp nginx/directus.conf /etc/nginx/sites-available/directus
# Sửa server_name cho đúng domain
sudo nano /etc/nginx/sites-available/directus
sudo ln -s /etc/nginx/sites-available/directus /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

### Bước 3: SSL với Certbot

```bash
sudo certbot --nginx -d cms.tecotec.top
```

### Bước 4: Khởi động

```bash
cd docker
docker compose up -d
docker compose logs -f directus   # Theo dõi log
```

### Bước 5: Import schema

```bash
TOKEN="<admin_token>"  # Lấy từ Directus > Settings > Access Tokens

# Tạo diff
curl -X POST "https://cms.tecotec.top/schema/diff?force=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @schema/directus-snapshot.json \
  -o /tmp/diff.json

# Extract data và apply
python3 -c "import json,sys; print(json.dumps(json.load(open('/tmp/diff.json'))['data']))" \
  > /tmp/diff-apply.json

curl -X POST "https://cms.tecotec.top/schema/apply?force=true" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @/tmp/diff-apply.json
```

### Bước 6: Fix UUID auto-generate

```bash
TOKEN="<admin_token>"
for col in brands sites authors categories tags posts posts_sites post_translations; do
  curl -s -X PATCH "https://cms.tecotec.top/fields/$col/id" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"meta":{"special":["uuid"],"hidden":true}}' && echo "OK: $col"
done
```

### Bước 7: Patch labels tiếng Việt

```bash
# Sửa BASE_URL và TOKEN trong script trước khi chạy
nano scripts/patch-vi-labels.py
python3 scripts/patch-vi-labels.py
```

### Bước 8: Seed data cơ bản

Tạo Languages (vi, en) và Brands (TECOTEC Group, OES, TUMIKI, CCW) qua Directus UI hoặc API.

---

## Cập nhật schema

Khi thay đổi schema trên môi trường local:

```bash
# Export snapshot mới
curl -s "http://localhost:8055/schema/snapshot" \
  -H "Authorization: Bearer <TOKEN>" | \
  python3 -c "import json,sys; print(json.dumps(json.load(sys.stdin)['data'], indent=2))" \
  > schema/directus-snapshot.json

git add schema/directus-snapshot.json
git commit -m "schema: <mô tả thay đổi>"
git push
```

---

## Tài liệu

- [Mô hình dữ liệu đầy đủ](docs/data-model.md)
- [Directus Docs](https://docs.directus.io)
- [n8n Directus Node](https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.directus/)
