from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("articles/", views.articles, name="articles"),
    path("articles/tag/<str:tag_slug>/", views.articles, name="articles_by_tag"),
    path("articles/<str:slug>/", views.article_detail, name="article_detail"),
    path("messages/", views.messages_page, name="messages"),
    path("photos/", views.photos, name="photos"),
    path("about/", views.about, name="about"),
    path("activate/<uidb64>/<token>/", views.activate_view, name="activate"),
    path("api/articles/", views.article_api, name="article_api"),
    path("api/messages/", views.message_api, name="message_api"),
]
