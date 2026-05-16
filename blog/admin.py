from django.contrib import admin, messages
from django.utils.html import format_html
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import path

from .importing import ensure_tag, extract_summary, extract_title, parse_markdown_file, unique_article_slug
from .models import Article, BackgroundMusic, Category, LifeRecord, Message, Profile, Tag


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "color")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "color")
    list_filter = ("parent",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    change_list_template = "admin/blog/article/change_list.html"
    change_form_template = "admin/blog/article/change_form.html"
    list_display = ("title", "category", "is_featured", "is_published", "views", "created_at")
    list_filter = ("category", "is_featured", "is_published", "created_at")
    search_fields = ("title", "summary", "content", "tags")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("views", "created_at", "updated_at")
    exclude = ("tags", "tag_nodes")

    class Media:
        css = {"all": ("css/admin_markdown_editor.css",)}
        js = ("js/admin_markdown_editor.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "import-md/",
                self.admin_site.admin_view(self.import_markdown_view),
                name="blog_article_import_md",
            )
        ]
        return custom_urls + urls

    def import_markdown_view(self, request):
        if request.method == "POST":
            files = request.FILES.getlist("files")
            default_category = Category.objects.first() or Category.objects.create(name="未分类", color="#64748b")
            imported = 0
            used_titles = set(Article.objects.values_list("title", flat=True))
            for file in files:
                raw = file.read().decode("utf-8", errors="ignore")
                meta, content = parse_markdown_file(raw)
                title = meta.get("title") or extract_title(content) or file.name.rsplit(".", 1)[0]
                if title in used_titles:
                    base_title = title
                    index = 2
                    while title in used_titles:
                        title = f"{base_title}-{index}"
                        index += 1
                used_titles.add(title)
                category_name = meta.get("category")
                if not category_name:
                    category_name = default_category.name
                category, _ = Category.objects.get_or_create(name=category_name.strip())
                article = Article.objects.create(
                    title=title,
                    slug=unique_article_slug(title),
                    summary=(meta.get("summary") or extract_summary(content))[:260],
                    content=content.strip() or raw.strip(),
                    category=category,
                    cover=meta.get("cover", ""),
                    is_published=meta.get("published", "true").lower() != "false",
                )
                tag_names = meta.get("tags", "")
                if tag_names:
                    article.tag_nodes.set([ensure_tag(path.strip()) for path in tag_names.split(",") if path.strip()])
                imported += 1
            self.message_user(request, f"成功导入 {imported} 篇 Markdown 文章。", messages.SUCCESS)
            return redirect("..")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "批量导入 Markdown",
        }
        return render(request, "admin/blog/article/import_md.html", context)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "parent", "user", "is_visible", "created_at", "reply_action")
    list_filter = ("is_visible", "created_at", "user")
    search_fields = ("name", "email", "content")

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:message_id>/reply/",
                self.admin_site.admin_view(self.reply_view),
                name="blog_message_reply",
            )
        ]
        return custom_urls + urls

    def reply_action(self, obj):
        if obj.parent_id:
            return "-"
        return format_html('<a class="button" href="{}/reply/">回复</a>', obj.id)

    reply_action.short_description = "站长回复"

    def reply_view(self, request, message_id):
        parent = get_object_or_404(Message, pk=message_id, parent__isnull=True)
        if request.method == "POST":
            content = request.POST.get("content", "").strip()
            if content:
                Message.objects.create(
                    user=request.user,
                    parent=parent,
                    name=request.user.get_username() or "站长",
                    email=getattr(request.user, "email", ""),
                    content=content,
                    is_visible=True,
                )
                self.message_user(request, "回复已发布。", messages.SUCCESS)
                return redirect("../../")

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "title": "回复留言",
            "parent": parent,
        }
        return render(request, "admin/blog/message/reply.html", context)


@admin.register(BackgroundMusic)
class BackgroundMusicAdmin(admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_active", "created_at")
    list_editable = ("sort_order", "is_active")
    list_filter = ("is_active", "created_at")
    search_fields = ("title",)


@admin.register(LifeRecord)
class LifeRecordAdmin(admin.ModelAdmin):
    list_display = ("taken_at", "is_published", "created_at")
    list_filter = ("is_published", "taken_at", "created_at")
    search_fields = ("note",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "headline", "email", "location")

    class Media:
        css = {"all": ("css/admin_markdown_editor.css",)}
        js = ("js/admin_markdown_editor.js",)
