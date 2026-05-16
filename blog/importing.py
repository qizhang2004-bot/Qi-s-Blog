from pathlib import Path

from django.utils.text import slugify

from .models import Article, Category, Tag


SKIP_PARTS = {".git", ".obsidian", ".MWebMetaData", "assets", "__pycache__"}


def iter_markdown_files(root):
    root = Path(root).expanduser()
    for path in root.rglob("*.md"):
        if any(part in SKIP_PARTS for part in path.relative_to(root).parts):
            continue
        yield path


def parse_markdown_file(raw):
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip().lower()] = value.strip().strip('"')
    return meta, parts[2]


def extract_title(content):
    for line in content.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def extract_summary(content):
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("```") or line.startswith("---"):
            continue
        return line.replace("**", "").replace("`", "")[:260]
    return "这是一篇从 Notes 导入的 Markdown 文章。"


def ensure_tag(path_text):
    parent = None
    tag = None
    for name in [part.strip() for part in path_text.split("/") if part.strip()]:
        tag, _ = Tag.objects.get_or_create(parent=parent, name=name)
        parent = tag
    return tag


def unique_article_slug(title):
    base = slugify(title, allow_unicode=True) or "article"
    slug = base
    index = 1
    while Article.objects.filter(slug=slug).exists():
        index += 1
        slug = f"{base}-{index}"
    return slug


def category_for_path(root, path):
    relative = path.relative_to(root)
    text = "/".join(relative.parts).lower()
    computer_keywords = [
        "docker",
        "k8s",
        "django",
        "计算机",
        "python",
        "java",
        "swift",
        "vue",
        "前端",
        "网络",
        "服务器",
        "linux",
        "mysql",
        "redis",
        "爬虫",
        "数据分析",
        "小程序",
        "intellij",
        "idea",
        "博客",
    ]
    if any(keyword in text for keyword in computer_keywords):
        return "计算机"
    return "其他"


def tag_paths_for_path(root, path):
    relative = path.relative_to(root)
    folders = list(relative.parts[:-1])
    if not folders:
        return ["随笔"]
    return ["/".join(folders[: index + 1]) for index in range(len(folders))]


def title_for_path(path, content, meta, used_titles):
    title = meta.get("title") or extract_title(content) or path.stem
    if title not in used_titles:
        used_titles.add(title)
        return title
    parent = path.parent.name
    titled = f"{title}（{parent}）"
    index = 2
    while titled in used_titles:
        titled = f"{title}（{parent}-{index}）"
        index += 1
    used_titles.add(titled)
    return titled


def import_markdown_path(path, root, used_titles=None):
    root = Path(root).expanduser()
    path = Path(path)
    raw = path.read_text(encoding="utf-8", errors="ignore")
    meta, content = parse_markdown_file(raw)
    used_titles = used_titles if used_titles is not None else set(Article.objects.values_list("title", flat=True))
    title = title_for_path(path, content, meta, used_titles)
    category_name = meta.get("category") or category_for_path(root, path)
    category, _ = Category.objects.get_or_create(name=category_name.strip(), defaults={"color": "#2f6df6"})
    article = Article.objects.create(
        title=title,
        slug=unique_article_slug(title),
        summary=(meta.get("summary") or extract_summary(content))[:260],
        content=content.strip() or raw.strip(),
        category=category,
        cover=meta.get("cover", ""),
        is_published=meta.get("published", "true").lower() != "false",
    )

    tag_paths = []
    if meta.get("tags"):
        tag_paths.extend(path.strip() for path in meta["tags"].split(",") if path.strip())
    tag_paths.extend(tag_paths_for_path(root, path))
    article.tag_nodes.set([ensure_tag(tag_path) for tag_path in dict.fromkeys(tag_paths)])
    return article
