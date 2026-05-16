from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from blog.importing import import_markdown_path, iter_markdown_files
from blog.models import Article, Category, Tag


class Command(BaseCommand):
    help = "Import a Notes markdown directory into blog articles."

    def add_arguments(self, parser):
        parser.add_argument("path", help="Notes directory path")
        parser.add_argument("--clear", action="store_true", help="Delete existing articles, tags and categories first")

    def handle(self, *args, **options):
        root = Path(options["path"]).expanduser()
        if not root.exists():
            raise CommandError(f"Notes path does not exist: {root}")

        if options["clear"]:
            Article.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()

        files = list(iter_markdown_files(root))
        used_titles = set(Article.objects.values_list("title", flat=True))
        imported = 0
        for path in files:
            import_markdown_path(path, root, used_titles)
            imported += 1

        self.stdout.write(self.style.SUCCESS(f"Imported {imported} markdown articles from {root}"))
