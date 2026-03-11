#!/usr/bin/env python3
"""
Patch Directus field labels (translations) và notes sang tiếng Việt
Chạy: python3 patch-vi-labels.py
"""

import urllib.request
import json
import time

BASE_URL = "http://localhost:8055"
TOKEN = "E8Y18a5UUP0BMom5IDLfdVSHcmrJuHde"

def patch(collection, field, meta):
    url = f"{BASE_URL}/fields/{collection}/{field}"
    payload = json.dumps({"meta": meta}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        method="PATCH",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json; charset=utf-8",
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status
    except Exception as e:
        return f"ERROR: {e}"

# Format: (collection, field, note, translations_label)
# translations_label = label hiển thị trên UI
FIELDS = [

    # ── POSTS ──────────────────────────────────────────────────────
    ("posts", "status",           "Trạng thái bài viết trong quy trình duyệt",                          "Trạng thái"),
    ("posts", "title",            "Tiêu đề gốc của bài viết (ngôn ngữ chính)",                          "Tiêu đề"),
    ("posts", "slug",             "Đường dẫn URL. Tự động tạo từ tiêu đề nếu để trống",                 "Slug URL"),
    ("posts", "language",         "Ngôn ngữ gốc của bài viết",                                          "Ngôn ngữ"),
    ("posts", "excerpt",          "Tóm tắt ngắn. Dùng làm WP excerpt (tối đa 300 ký tự)",               "Tóm tắt"),
    ("posts", "content",          "Nội dung chính của bài viết",                                         "Nội dung"),
    ("posts", "content_format",   "Định dạng nội dung: HTML (mặc định), Markdown, hoặc Blocks",          "Định dạng nội dung"),
    ("posts", "featured_image",   "Ảnh đại diện bài viết. Lưu trong Directus, n8n sẽ đẩy lên WP",       "Ảnh đại diện"),
    ("posts", "author",           "Tác giả chính của bài viết",                                          "Tác giả"),
    ("posts", "category",         "Danh mục chính (1 danh mục duy nhất)",                                "Danh mục"),
    ("posts", "tags",             "Tags bổ sung (nhiều tags, không giới hạn)",                           "Tags"),
    ("posts", "brands",           "Bài viết thuộc brand nào trong hệ sinh thái TMK",                     "Brands"),
    ("posts", "publish_date",     "Ngày giờ dự kiến đăng bài",                                           "Ngày đăng"),
    ("posts", "wp_post_type",     "Loại bài trên WordPress: Post, Page, hoặc Product",                   "Loại bài WP"),
    ("posts", "wp_comment_status","Cho phép bình luận trên bài hay không",                                "Bình luận WP"),
    ("posts", "target_sites",     "Chọn WP site đích để đẩy bài. Mỗi site có trạng thái publish riêng", "Site đích"),
    ("posts", "content_source",   "Nguồn gốc nội dung: do người viết, AI tạo draft, hay từ agency",      "Nguồn nội dung"),
    ("posts", "assigned_to",      "Người được giao duyệt bài này",                                       "Giao cho"),
    ("posts", "review_deadline",  "Deadline duyệt bài. Quá hạn sẽ cảnh báo",                             "Hạn duyệt"),
    ("posts", "internal_notes",   "Ghi chú nội bộ. Không được publish ra ngoài",                         "Ghi chú nội bộ"),
    ("posts", "ai_prompt_used",   "Prompt AI đã dùng để generate bài này. Lưu để tái sử dụng",           "Prompt AI đã dùng"),
    ("posts", "seo_title",        "Tiêu đề SEO. Map sang rank_math_title trên WP",                       "Tiêu đề SEO"),
    ("posts", "seo_description",  "Mô tả SEO (tối đa 160 ký tự). Map sang rank_math_description",        "Mô tả SEO"),
    ("posts", "seo_focus_keyword","Từ khóa trọng tâm. Map sang rank_math_focus_keyword",                  "Từ khóa trọng tâm"),
    ("posts", "seo_canonical_url","URL canonical nếu bài này là bản copy từ nơi khác",                    "URL Canonical"),
    ("posts", "seo_robots",       "Chỉ thị cho Google: index hay noindex",                                "Robots"),
    ("posts", "schema_type",      "Loại Schema.org. BlogPosting cho bài blog thông thường",               "Schema Type"),
    ("posts", "og_title",         "Tiêu đề khi chia sẻ lên Facebook/Zalo. Nếu trống dùng seo_title",     "Tiêu đề OG"),
    ("posts", "og_description",   "Mô tả khi chia sẻ lên mạng xã hội",                                   "Mô tả OG"),
    ("posts", "og_image",         "Ảnh thumbnail khi chia sẻ lên Facebook/Zalo (tỷ lệ 1200x630)",        "Ảnh OG"),
    ("posts", "date_created",     "Thời điểm tạo bài (tự động)",                                          "Ngày tạo"),
    ("posts", "date_updated",     "Thời điểm cập nhật cuối (tự động)",                                    "Ngày cập nhật"),
    ("posts", "user_created",     "Người tạo bài (tự động)",                                              "Người tạo"),
    ("posts", "user_updated",     "Người cập nhật cuối (tự động)",                                        "Người cập nhật"),

    # ── DIVIDERS (chỉ cần note, label đã có trong options.title) ───
    ("posts", "divider_content",  None, None),
    ("posts", "divider_taxonomy", None, None),
    ("posts", "divider_seo",      None, None),
    ("posts", "divider_publish",  None, None),
    ("posts", "divider_internal", None, None),

    # ── CATEGORIES ─────────────────────────────────────────────────
    ("categories", "name",           "Tên danh mục hiển thị",                                                "Tên danh mục"),
    ("categories", "slug",           "Slug URL của danh mục",                                                 "Slug"),
    ("categories", "description",    "Mô tả danh mục (dùng cho SEO category page)",                          "Mô tả"),
    ("categories", "parent",         "Danh mục cha (để tạo cấu trúc phân cấp)",                              "Danh mục cha"),
    ("categories", "brand",          "Danh mục này thuộc brand nào",                                          "Brand"),
    ("categories", "wp_category_id", "ID danh mục trên từng WP site. Format: {\"ten-site\": 12}",             "WP Category ID"),

    # ── TAGS ───────────────────────────────────────────────────────
    ("tags", "name",       "Tên tag",                                                                "Tên tag"),
    ("tags", "slug",       "Slug URL của tag",                                                        "Slug"),
    ("tags", "wp_tag_id",  "ID tag trên từng WP site. Format: {\"ten-site\": 45}",                   "WP Tag ID"),

    # ── AUTHORS ────────────────────────────────────────────────────
    ("authors", "display_name", "Tên hiển thị của tác giả trên bài viết",                            "Tên hiển thị"),
    ("authors", "email",        "Email liên hệ của tác giả",                                          "Email"),
    ("authors", "bio",          "Tiểu sử ngắn. Hiển thị trong author box trên WP",                    "Tiểu sử"),
    ("authors", "avatar",       "Ảnh đại diện tác giả",                                               "Ảnh đại diện"),
    ("authors", "directus_user","Liên kết với tài khoản Directus tương ứng",                          "Tài khoản Directus"),

    # ── BRANDS ─────────────────────────────────────────────────────
    ("brands", "name",  "Tên brand trong hệ sinh thái TMK Holdings",                                  "Tên brand"),
    ("brands", "slug",  "Slug định danh nội bộ (vd: tecotec-group, ccw)",                             "Slug"),
    ("brands", "color", "Màu chủ đạo của brand (hex code)",                                           "Màu chủ đạo"),
    ("brands", "logo",  "Logo brand. Lưu trong Directus Files",                                       "Logo"),

    # ── SITES ──────────────────────────────────────────────────────
    ("sites", "name",             "Tên hiển thị của WP site",                                         "Tên site"),
    ("sites", "slug",             "Slug định danh nội bộ (vd: tecotec-vn, ccw-vn)",                   "Slug nội bộ"),
    ("sites", "wp_url",           "URL gốc của WP site (không có dấu / cuối)",                        "URL WP"),
    ("sites", "wp_api_user",      "Username dùng cho WP Application Password",                         "WP API User"),
    ("sites", "wp_api_password",  "WP Application Password (tạo trong WP > Users > Application Passwords)", "WP API Password"),
    ("sites", "brand",            "Site này thuộc brand nào",                                          "Brand"),
    ("sites", "default_author_id","ID tác giả mặc định trên WP site này (số nguyên)",                 "Author ID mặc định"),
    ("sites", "active",           "Tắt để tạm ngưng đẩy bài lên site này",                            "Đang hoạt động"),

    # ── LANGUAGES ──────────────────────────────────────────────────
    ("languages", "code",    "Mã ngôn ngữ ISO 639-1 (vd: vi, en)",                                    "Mã ngôn ngữ"),
    ("languages", "name",    "Tên ngôn ngữ (vd: Tiếng Việt, English)",                                "Tên ngôn ngữ"),
    ("languages", "default", "Đánh dấu ngôn ngữ mặc định của hệ thống",                               "Mặc định"),

    # ── POSTS_SITES ────────────────────────────────────────────────
    ("posts_sites", "sites_id",       "WP site đích",                                                  "Site"),
    ("posts_sites", "publish_status", "Trạng thái đẩy bài lên site này",                               "Trạng thái publish"),
    ("posts_sites", "wp_post_id",     "ID bài viết trên WP sau khi đẩy thành công",                    "WP Post ID"),
    ("posts_sites", "wp_post_url",    "URL bài viết trên WP",                                          "URL bài trên WP"),
    ("posts_sites", "published_at",   "Thời điểm đẩy bài thành công",                                  "Thời điểm publish"),
    ("posts_sites", "error_log",      "Log lỗi nếu đẩy bài thất bại. Kiểm tra để debug n8n workflow",  "Log lỗi"),

    # ── POST_TRANSLATIONS ──────────────────────────────────────────
    ("post_translations", "posts_id",        "Bài viết gốc",                                           "Bài viết gốc"),
    ("post_translations", "language",        "Ngôn ngữ của bản dịch này",                              "Ngôn ngữ"),
    ("post_translations", "title",           "Tiêu đề bản dịch",                                       "Tiêu đề"),
    ("post_translations", "slug",            "Slug riêng cho ngôn ngữ này",                             "Slug"),
    ("post_translations", "excerpt",         "Tóm tắt bản dịch",                                       "Tóm tắt"),
    ("post_translations", "content",         "Nội dung bản dịch",                                       "Nội dung"),
    ("post_translations", "seo_title",       "Tiêu đề SEO của bản dịch",                                "Tiêu đề SEO"),
    ("post_translations", "seo_description", "Mô tả SEO của bản dịch",                                  "Mô tả SEO"),
]

total = len([f for f in FIELDS if f[2] or f[3]])
done = 0
errors = []

for collection, field, note, label in FIELDS:
    if not note and not label:
        continue

    meta = {}
    if note:
        meta["note"] = note
    if label:
        meta["translations"] = [{"language": "vi-VN", "translation": label}]

    status = patch(collection, field, meta)
    done += 1

    if str(status).startswith("ERROR"):
        errors.append(f"{collection}.{field}: {status}")
        print(f"  FAIL [{done}/{total}] {collection}.{field} -> {status}")
    else:
        print(f"  OK   [{done}/{total}] {collection}.{field}")

    time.sleep(0.05)  # Tránh rate limit

print(f"\n{'='*50}")
print(f"Hoàn thành: {done - len(errors)}/{total} fields")
if errors:
    print(f"Lỗi ({len(errors)}):")
    for e in errors:
        print(f"  {e}")
else:
    print("Không có lỗi.")
