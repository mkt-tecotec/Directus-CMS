# Mô hình dữ liệu - Directus CMS

**TECOTEC Group MarCom Content Repository**
Directus v11.16.1 | PostgreSQL 15 | 11 collections | 97 fields | 20 relations

---

## Kiến trúc tổng quan

Directus đóng vai trò **content hub trung tâm**: soạn thảo 1 lần, n8n tự động đẩy lên 16 WP sites đích.

```
[Editor / AI draft]
        |
        v
[Directus CMS - cms.tecotec.top]
  - Quy trình duyệt: draft > review > approved > published
  - Media hub: ảnh lưu tập trung, n8n upload lên từng WP
  - SEO fields: RankMath-compatible
        |
        v
[n8n Workflow]
        |
        +---> tecotec.vn
        +---> tecostore.vn
        +---> oes.vn
        +---> tumiki.vn
        +---> ccw.vn
        +---> ... (16 sites tổng)
```

---

## Sơ đồ quan hệ

```
languages <──────── posts ──────────> categories ──> brands
                      |    └──────> authors
                      |    └──────> directus_files (featured_image)
                      |    └──────> directus_files (og_image)
                      |    └──────> directus_users (assigned_to)
                      |
                      +── posts_tags ────────────> tags
                      +── posts_brands ──────────> brands
                      +── posts_sites ───────────> sites ──> brands
                      └── post_translations ─────> languages

categories.parent -> categories  (phân cấp đệ quy)
authors.avatar -> directus_files
authors.directus_user -> directus_users
brands.logo -> directus_files
```

---

## Collection: `posts` (40 fields)

Collection chính. Mỗi record là 1 bài viết hoàn chỉnh.

**Nội dung**

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key, tự động tạo |
| `status` | string | Trạng thái quy trình duyệt (xem workflow bên dưới) |
| `title` | string | Tiêu đề gốc (ngôn ngữ chính) |
| `slug` | string | URL slug. Tự động tạo từ tiêu đề nếu để trống |
| `language` | string (FK) | Ngôn ngữ gốc -> `languages.code` |
| `excerpt` | text | Tóm tắt ngắn, map sang WP excerpt (tối đa 300 ký tự) |
| `content` | text | Nội dung chính (HTML) |
| `content_format` | string | `html` / `markdown` / `blocks` |
| `featured_image` | uuid (FK) | Ảnh đại diện -> `directus_files`. n8n đẩy lên WP |

**Taxonomy**

| Field | Type | Ghi chú |
|---|---|---|
| `author` | uuid (FK) | Tác giả -> `authors.id` |
| `category` | uuid (FK) | Danh mục chính (1 danh mục) -> `categories.id` |
| `tags` | M2M | Nhiều tags -> qua `posts_tags` |
| `brands` | M2M | Thuộc brand nào -> qua `posts_brands` |

**SEO (RankMath mapping)**

| Field | Type | WP meta key |
|---|---|---|
| `seo_title` | string | `rank_math_title` |
| `seo_description` | text | `rank_math_description` (tối đa 160 ký tự) |
| `seo_focus_keyword` | string | `rank_math_focus_keyword` |
| `seo_canonical_url` | string | `rank_math_canonical_url` |
| `seo_robots` | string | `rank_math_robots` |
| `schema_type` | string | `BlogPosting` / `Article` / `NewsArticle` / `HowTo` |
| `og_title` | string | `rank_math_facebook_title` |
| `og_description` | text | `rank_math_facebook_description` |
| `og_image` | uuid (FK) | `rank_math_facebook_image` |

**Publish settings**

| Field | Type | Ghi chú |
|---|---|---|
| `publish_date` | dateTime | Ngày giờ dự kiến đăng bài |
| `wp_post_type` | string | `post` / `page` / `product` |
| `wp_comment_status` | string | `open` / `closed` |
| `target_sites` | M2M | WP sites đích -> qua `posts_sites` |

**Internal / workflow**

| Field | Type | Ghi chú |
|---|---|---|
| `content_source` | string | `human` / `ai_draft` / `agency` |
| `assigned_to` | uuid (FK) | Người duyệt -> `directus_users` |
| `review_deadline` | dateTime | Deadline duyệt bài |
| `internal_notes` | text | Ghi chú nội bộ, không publish |
| `ai_prompt_used` | text | Prompt AI đã dùng, lưu để tái sử dụng |
| `date_created` | timestamp | Tự động |
| `date_updated` | timestamp | Tự động |
| `user_created` | uuid | Tự động |
| `user_updated` | uuid | Tự động |

**Status workflow:**
```
draft --> review --> approved --> published --> archived
             |
             v
          rejected --> draft
```

---

## Collection: `categories` (7 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `name` | string | Tên danh mục hiển thị |
| `slug` | string | Slug URL |
| `description` | text | Mô tả (dùng cho SEO category page) |
| `parent` | uuid (FK) | Danh mục cha - self-referential, tạo cấu trúc cây |
| `brand` | uuid (FK) | Thuộc brand -> `brands.id` |
| `wp_category_id` | json | ID trên từng WP site: `{"tecotec-vn": 12, "ccw-vn": 5}` |

---

## Collection: `tags` (4 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `name` | string | Tên tag |
| `slug` | string | Slug URL |
| `wp_tag_id` | json | ID trên từng WP site: `{"tecotec-vn": 45}` |

---

## Collection: `authors` (6 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `display_name` | string | Tên hiển thị trên bài viết |
| `email` | string | Email liên hệ |
| `bio` | text | Tiểu sử ngắn. Hiển thị trong author box trên WP |
| `avatar` | uuid (FK) | Ảnh đại diện -> `directus_files` |
| `directus_user` | uuid (FK) | Liên kết tài khoản Directus -> `directus_users` |

---

## Collection: `brands` (5 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `name` | string | Tên brand |
| `slug` | string | Slug nội bộ |
| `color` | string | Màu chủ đạo (hex) |
| `logo` | uuid (FK) | Logo -> `directus_files` |

Brands hiện tại: TECOTEC Group (`tecotec-group`), OES (`oes`), TUMIKI (`tumiki`), CCW (`ccw`).

---

## Collection: `sites` (9 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `name` | string | Tên hiển thị |
| `slug` | string | Slug nội bộ (vd: `tecotec-vn`) |
| `wp_url` | string | Base URL không có dấu `/` cuối |
| `wp_api_user` | string | Username WP Application Password |
| `wp_api_password` | string | WP Application Password |
| `brand` | uuid (FK) | Thuộc brand -> `brands.id` |
| `default_author_id` | integer | Author ID mặc định trên WP |
| `active` | boolean | Tắt để ngưng đẩy bài |

---

## Collection: `languages` (3 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `code` | string (PK) | ISO 639-1: `vi`, `en` |
| `name` | string | `Tiếng Việt`, `English` |
| `default` | boolean | Ngôn ngữ mặc định |

---

## Collection: `post_translations` (9 fields)

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `posts_id` | uuid (FK) | Bài viết gốc -> `posts.id` |
| `language` | string (FK) | Ngôn ngữ -> `languages.code` |
| `title` | string | Tiêu đề bản dịch |
| `slug` | string | Slug riêng cho ngôn ngữ này |
| `excerpt` | text | Tóm tắt bản dịch |
| `content` | text | Nội dung bản dịch |
| `seo_title` | string | SEO title bản dịch |
| `seo_description` | text | SEO description bản dịch |

---

## Collection: `posts_sites` - Junction Posts x Sites (8 fields)

Bảng trung gian đặc biệt: lưu trạng thái publish riêng từng site. **n8n đọc bảng này để biết cần push bài nào đến site nào.**

| Field | Type | Ghi chú |
|---|---|---|
| `id` | uuid | Primary key |
| `posts_id` | uuid (FK) | -> `posts.id` |
| `sites_id` | uuid (FK) | -> `sites.id` |
| `publish_status` | string | `pending` / `published` / `failed` / `skipped` |
| `wp_post_id` | integer | ID bài trên WP sau khi push thành công |
| `wp_post_url` | string | URL bài trên WP |
| `published_at` | dateTime | Thời điểm push thành công |
| `error_log` | text | Log lỗi nếu push thất bại |

---

## Collection: `posts_tags` (3 fields)

| Field | Type |
|---|---|
| `id` | integer (auto) |
| `posts_id` | uuid (FK) -> `posts` |
| `tags_id` | uuid (FK) -> `tags` |

## Collection: `posts_brands` (3 fields)

| Field | Type |
|---|---|
| `id` | integer (auto) |
| `posts_id` | uuid (FK) -> `posts` |
| `brands_id` | uuid (FK) -> `brands` |

---

## n8n Push Workflow Logic

Trigger: `posts_sites.publish_status = "pending"`

```
1. Đọc post data từ Directus API (kèm relations)
2. Download featured_image từ /assets/{id}
3. Upload ảnh lên WP: POST /wp-json/wp/v2/media -> attachment_id
4. Map wp_category_id / wp_tag_id từ JSON field theo site slug
5. Map SEO fields sang RankMath meta keys
6. Tạo bài: POST /wp-json/wp/v2/posts
7. Cập nhật posts_sites:
   publish_status = "published", wp_post_id, wp_post_url, published_at
8. Nếu lỗi: publish_status = "failed", error_log = message
```

---

## Seed data sau khi deploy

Thứ tự tạo (do quan hệ phụ thuộc):

1. Languages: `vi` (default=true), `en`
2. Brands: TECOTEC Group, OES, TUMIKI, CCW
3. Sites: 16 WP sites với đủ `wp_url`, `wp_api_user`, `wp_api_password`
4. Authors: Mapping thành viên MarCom team với Directus users

---

*TECOTEC Group MarCom - Tài liệu nội bộ*
