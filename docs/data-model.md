# Mô hình dữ liệu - Directus CMS TECOTEC Group

> Phiên bản: Directus 11.x | Database: PostgreSQL 15 | Cập nhật: 2026-03

## Tổng quan

Directus CMS là kho bài viết trung tâm (headless CMS) phục vụ hệ sinh thái đa thương hiệu TMK Holdings. Nội dung được tạo và duyệt tại đây, sau đó n8n tự động đẩy lên 16 WP sites đích.

```
Directus CMS
    └── n8n Workflow
            ├── tecotec.vn (TECOTEC Group)
            ├── oes.vn (OES)
            ├── tumiki.vn (TUMIKI)
            ├── clevelandcyclewerks.vn (CCW)
            └── ... (16 sites tổng)
```

---

## Sơ đồ quan hệ

```
languages ──────── posts ──────────── categories (self-ref)
                    │  │                    │
                    │  ├── authors           └── brands
                    │  ├── tags (M2M via posts_tags)
                    │  ├── brands (M2M via posts_brands)
                    │  ├── sites (M2M via posts_sites)
                    │  └── post_translations
                    │
                   sites ──── brands
```

---

## Collections

### 1. posts

Kho bài viết trung tâm. Đây là collection chính của toàn hệ thống.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key, tự động tạo |
| status | string | Trạng thái | Quy trình duyệt: `draft` / `review` / `approved` / `published` / `archived` / `rejected` |
| title | string | Tiêu đề | Tiêu đề gốc (ngôn ngữ chính) |
| slug | string | Slug URL | Tự động tạo từ tiêu đề nếu để trống |
| language | string | Ngôn ngữ | FK tới `languages.code` |
| excerpt | text | Tóm tắt | Tối đa 300 ký tự, dùng làm WP excerpt |
| content | text | Nội dung | Nội dung chính (HTML/Markdown/Blocks) |
| content_format | string | Định dạng nội dung | `html` / `markdown` / `blocks` |
| featured_image | uuid | Ảnh đại diện | FK tới `directus_files` |
| author | uuid | Tác giả | FK tới `authors.id` |
| category | uuid | Danh mục | FK tới `categories.id` (1 danh mục chính) |
| tags | alias | Tags | M2M qua `posts_tags` |
| brands | alias | Brands | M2M qua `posts_brands` |
| target_sites | alias | Site đích | M2M qua `posts_sites` |
| publish_date | dateTime | Ngày đăng | Ngày giờ dự kiến đăng bài |
| wp_post_type | string | Loại bài WP | `post` / `page` / `product` |
| wp_comment_status | string | Bình luận WP | `open` / `closed` |
| seo_title | string | Tiêu đề SEO | Map sang `rank_math_title` trên WP |
| seo_description | text | Mô tả SEO | Tối đa 160 ký tự, map sang `rank_math_description` |
| seo_focus_keyword | string | Từ khóa trọng tâm | Map sang `rank_math_focus_keyword` |
| seo_canonical_url | string | URL Canonical | Dùng khi bài là bản syndicate từ nơi khác |
| seo_robots | string | Robots | `index,follow` / `noindex,nofollow` |
| schema_type | string | Schema Type | `BlogPosting` / `Article` / `NewsArticle` |
| og_title | string | Tiêu đề OG | Tiêu đề khi chia sẻ Facebook/Zalo |
| og_description | text | Mô tả OG | Mô tả khi chia sẻ mạng xã hội |
| og_image | uuid | Ảnh OG | Tỷ lệ khuyến nghị 1200x630px |
| content_source | string | Nguồn nội dung | `human` / `ai_draft` / `agency` |
| assigned_to | uuid | Giao cho | FK tới `directus_users` |
| review_deadline | dateTime | Hạn duyệt | Quá hạn sẽ cảnh báo |
| internal_notes | text | Ghi chú nội bộ | Không publish ra ngoài |
| ai_prompt_used | text | Prompt AI đã dùng | Lưu để tái sử dụng |
| date_created | timestamp | Ngày tạo | Tự động |
| date_updated | timestamp | Ngày cập nhật | Tự động |
| user_created | uuid | Người tạo | Tự động |
| user_updated | uuid | Người cập nhật | Tự động |

**Quy trình duyệt (status workflow):**
```
draft → review → approved → published
                          → rejected → draft (sửa lại)
published → archived
```

---

### 2. categories

Danh mục phân cấp. Hỗ trợ nested không giới hạn cấp.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| name | string | Tên danh mục | Tên hiển thị |
| slug | string | Slug | Slug URL |
| description | text | Mô tả | Dùng cho SEO category page |
| parent | uuid | Danh mục cha | Self-referential FK (null = root) |
| brand | uuid | Brand | FK tới `brands.id` |
| wp_category_id | json | WP Category ID | Map ID theo từng site: `{"tecotec-vn": 12, "oes-vn": 5}` |

---

### 3. tags

Tags gắn vào bài viết (M2M).

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| name | string | Tên tag | Tên tag |
| slug | string | Slug | Slug URL |
| wp_tag_id | json | WP Tag ID | Map ID theo từng site: `{"tecotec-vn": 45}` |

---

### 4. authors

Tác giả bài viết. Liên kết với tài khoản Directus.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| display_name | string | Tên hiển thị | Tên hiển thị trên bài viết |
| email | string | Email | Email liên hệ |
| bio | text | Tiểu sử | Hiển thị trong author box trên WP |
| avatar | uuid | Ảnh đại diện | FK tới `directus_files` |
| directus_user | uuid | Tài khoản Directus | FK tới `directus_users` |

---

### 5. brands

4 brands trong hệ sinh thái TMK Holdings.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| name | string | Tên brand | Ví dụ: TECOTEC Group |
| slug | string | Slug | Định danh nội bộ: `tecotec-group`, `ccw`, `oes`, `tumiki` |
| color | string | Màu chủ đạo | Hex code: `#003087` |
| logo | uuid | Logo | FK tới `directus_files` |

**Seed data:**

| name | slug |
|------|------|
| TECOTEC Group | tecotec-group |
| OES | oes |
| TUMIKI | tumiki |
| Cleveland CycleWerks Vietnam | ccw |

---

### 6. sites

16 WP sites đích. Lưu thông tin kết nối API.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| name | string | Tên site | Tên hiển thị |
| slug | string | Slug nội bộ | Định danh: `tecotec-vn`, `ccw-vn` |
| wp_url | string | URL WP | URL gốc, không có `/` cuối |
| wp_api_user | string | WP API User | Username cho Application Password |
| wp_api_password | string | WP API Password | WP Application Password |
| brand | uuid | Brand | FK tới `brands.id` |
| default_author_id | integer | Author ID mặc định | Author ID trên WP site đó |
| active | boolean | Đang hoạt động | Tắt để tạm ngưng đẩy bài |

---

### 7. languages

Ngôn ngữ hỗ trợ. Hiện tại: Tiếng Việt (mặc định) và English.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| code | string | Mã ngôn ngữ | ISO 639-1: `vi`, `en` |
| name | string | Tên ngôn ngữ | `Tiếng Việt`, `English` |
| default | boolean | Mặc định | Chỉ 1 ngôn ngữ được đánh dấu default |

---

### 8. posts_sites (Junction)

Theo dõi trạng thái publish của từng bài trên từng site.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| posts_id | uuid | - | FK tới `posts.id` |
| sites_id | uuid | Site | FK tới `sites.id` |
| publish_status | string | Trạng thái publish | `pending` / `published` / `failed` / `skipped` |
| wp_post_id | integer | WP Post ID | ID bài trên WP sau khi đẩy thành công |
| wp_post_url | string | URL bài trên WP | URL đầy đủ bài viết trên WP |
| published_at | dateTime | Thời điểm publish | Timestamp đẩy thành công |
| error_log | text | Log lỗi | Chi tiết lỗi nếu n8n workflow thất bại |

---

### 9. posts_tags (Junction)

Quan hệ M2M giữa bài viết và tags.

| Field | Type | Mô tả |
|-------|------|-------|
| id | integer | Primary key |
| posts_id | uuid | FK tới `posts.id` |
| tags_id | uuid | FK tới `tags.id` |

---

### 10. posts_brands (Junction)

Quan hệ M2M giữa bài viết và brands.

| Field | Type | Mô tả |
|-------|------|-------|
| id | integer | Primary key |
| posts_id | uuid | FK tới `posts.id` |
| brands_id | uuid | FK tới `brands.id` |

---

### 11. post_translations

Bản dịch của bài viết sang ngôn ngữ khác.

| Field | Type | Label | Mô tả |
|-------|------|-------|-------|
| id | uuid | - | Primary key |
| posts_id | uuid | Bài viết gốc | FK tới `posts.id` |
| language | string | Ngôn ngữ | FK tới `languages.code` |
| title | string | Tiêu đề | Tiêu đề bản dịch |
| slug | string | Slug | Slug riêng cho ngôn ngữ này |
| excerpt | text | Tóm tắt | Tóm tắt bản dịch |
| content | text | Nội dung | Nội dung bản dịch |
| seo_title | string | Tiêu đề SEO | SEO title của bản dịch |
| seo_description | text | Mô tả SEO | SEO description của bản dịch |

---

## Mapping SEO sang RankMath (WP)

Khi n8n đẩy bài lên WP, các field SEO được map vào post meta của RankMath:

| Directus field | WP post meta key |
|----------------|-----------------|
| seo_title | `rank_math_title` |
| seo_description | `rank_math_description` |
| seo_focus_keyword | `rank_math_focus_keyword` |
| seo_canonical_url | `rank_math_canonical_url` |
| seo_robots | `rank_math_robots` |
| schema_type | `rank_math_schema_type` |
| og_title | `rank_math_facebook_title` |
| og_description | `rank_math_facebook_description` |
| og_image | `rank_math_facebook_image` |

---

## n8n Workflow Logic

```
Trigger: posts_sites.publish_status = "pending"
    │
    ├── Lấy post data từ Directus API
    ├── Lấy site credentials (wp_url, wp_api_user, wp_api_password)
    ├── Upload featured_image lên WP Media
    ├── POST /wp-json/wp/v2/posts
    │       body: title, content, excerpt, slug, status, categories, tags
    │       meta: rank_math_* fields
    │
    ├── Thành công → PATCH posts_sites:
    │       publish_status = "published"
    │       wp_post_id = <id>
    │       wp_post_url = <link>
    │       published_at = <now>
    │
    └── Thất bại → PATCH posts_sites:
            publish_status = "failed"
            error_log = <error message>
```
