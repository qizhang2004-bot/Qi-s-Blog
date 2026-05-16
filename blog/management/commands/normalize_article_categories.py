from django.core.management.base import BaseCommand

from blog.models import Article, Category


COMPUTER_NAMES = {"Django项目", "Docker", "k8s", "培训知识", "计算机笔记", "计算机"}
COMPUTER_KEYWORDS = [
    "计算机",
    "网络",
    "服务器",
    "线路",
    "博客",
    "python",
    "django",
    "docker",
    "k8s",
    "linux",
    "mysql",
    "redis",
    "java",
    "swift",
    "vue",
    "前端",
    "爬虫",
    "数据分析",
    "小程序",
    "intellij",
    "idea",
]


class Command(BaseCommand):
    help = "Normalize article categories to 计算机 and 其他."

    def handle(self, *args, **options):
        computer, _ = Category.objects.get_or_create(name="计算机", defaults={"color": "#2f6df6"})
        other, _ = Category.objects.get_or_create(name="其他", defaults={"color": "#8b5cf6"})
        computer_count = 0
        other_count = 0

        for article in Article.objects.select_related("category").prefetch_related("tag_nodes"):
            text = " ".join(
                [
                    article.title,
                    article.summary,
                    article.content[:300],
                    article.category.name,
                    " ".join(article.tag_list()),
                ]
            ).lower()
            is_computer = article.category.name in COMPUTER_NAMES or any(keyword in text for keyword in COMPUTER_KEYWORDS)
            article.category = computer if is_computer else other
            article.save(update_fields=["category"])
            if is_computer:
                computer_count += 1
            else:
                other_count += 1

        Category.objects.exclude(name__in=["计算机", "其他"]).delete()
        self.stdout.write(self.style.SUCCESS(f"Done: 计算机 {computer_count}, 其他 {other_count}"))
