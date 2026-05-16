from django.test import TestCase
from django.urls import reverse

from .models import Article, Category


class BlogPageTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name="Python")
        Article.objects.create(
            title="Hello Django",
            summary="A short intro",
            content="Content",
            category=category,
            is_published=True,
        )

    def test_home_page_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hello Django")

    def test_article_api_returns_articles(self):
        response = self.client.get(reverse("article_api"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["articles"][0]["title"], "Hello Django")
