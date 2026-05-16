import json
import calendar
from datetime import timedelta

import markdown
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_http_methods
from markdown.extensions.toc import TocExtension, slugify_unicode

from .forms import EmailUserCreationForm
from .models import Article, BackgroundMusic, Category, LifeRecord, Message, Profile, Tag


def build_contribution_days():
    today = timezone.localdate()
    start = today - timedelta(days=83)
    counts = {}
    article_dates = Article.objects.filter(is_published=True, created_at__date__gte=start).values_list("created_at", flat=True)
    for created_at in article_dates:
        day = timezone.localtime(created_at).date()
        counts[day] = counts.get(day, 0) + 1

    max_count = max(counts.values(), default=0)
    days = []
    for index in range(84):
        day = start + timedelta(days=index)
        count = counts.get(day, 0)
        if count == 0:
            level = 0
        elif max_count <= 1:
            level = 2
        else:
            level = min(4, max(1, round((count / max_count) * 4)))
        days.append({"date": day, "count": count, "level": level})
    return days


def site_context():
    profile = Profile.objects.first()
    background_playlist = list(BackgroundMusic.objects.filter(is_active=True))
    return {
        "profile": profile,
        "featured": Article.objects.filter(is_published=True, is_featured=True).first(),
        "categories": Category.objects.all(),
        "tag_roots": Tag.objects.filter(parent__isnull=True).prefetch_related("children__children__children"),
        "background_music": background_playlist[0] if background_playlist else None,
        "background_playlist": [
            {"title": item.title, "url": item.audio.url}
            for item in background_playlist
            if item.audio
        ],
    }


def home(request):
    latest = Article.objects.filter(is_published=True).order_by("-created_at")[:10]
    recent_messages = (
        Message.objects.filter(parent__isnull=True, is_visible=True)
        .select_related("user")
        .prefetch_related("replies")
        [:12]
    )
    life_records = LifeRecord.objects.filter(is_published=True).order_by("-taken_at", "-created_at")[:8]
    contribution_days = build_contribution_days()
    return render(
        request,
        "home.html",
        {
            **site_context(),
            "latest_articles": latest,
            "recent_messages": recent_messages,
            "life_records": life_records,
            "contribution_days": contribution_days,
            "contribution_total": sum(day["count"] for day in contribution_days),
        },
    )


def articles(request, tag_slug=None):
    selected_category = request.GET.get("category", "")
    search_query = request.GET.get("q", "").strip()
    start_date = parse_date(request.GET.get("start", ""))
    end_date = parse_date(request.GET.get("end", ""))
    articles_qs = Article.objects.filter(is_published=True).select_related("category").prefetch_related("tag_nodes")
    if search_query:
        articles_qs = articles_qs.filter(Q(title__icontains=search_query) | Q(summary__icontains=search_query))
    if selected_category:
        articles_qs = articles_qs.filter(category__name=selected_category)
    if start_date:
        articles_qs = articles_qs.filter(created_at__date__gte=start_date)
    if end_date:
        articles_qs = articles_qs.filter(created_at__date__lte=end_date)
    selected_tag = None
    if tag_slug:
        selected_tag = get_object_or_404(Tag, slug=tag_slug)
        tag_ids = [selected_tag.id] + [child.id for child in selected_tag.descendants()]
        articles_qs = articles_qs.filter(tag_nodes__id__in=tag_ids).distinct()

    requested_month = request.GET.get("month", "")
    today = timezone.localdate()
    month_date = parse_date(f"{requested_month}-01") if requested_month else None
    if not month_date:
        month_date = start_date.replace(day=1) if start_date else today.replace(day=1)
    previous_month = (month_date.replace(day=1) - timedelta(days=1)).replace(day=1)
    next_month = (month_date.replace(day=28) + timedelta(days=4)).replace(day=1)
    month_weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(month_date.year, month_date.month)
    month_start = month_date
    month_end = next_month - timedelta(days=1)
    article_days = set(
        timezone.localtime(item).date()
        for item in Article.objects.filter(
            is_published=True,
            created_at__date__gte=month_start,
            created_at__date__lte=month_end,
        ).values_list("created_at", flat=True)
    )

    paginator = Paginator(articles_qs, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    query_params = request.GET.copy()
    query_params.pop("page", None)
    calendar_query = request.GET.copy()
    calendar_query.pop("page", None)
    calendar_query.pop("month", None)
    calendar_query.pop("start", None)
    calendar_query.pop("end", None)
    return render(
        request,
        "articles.html",
        {
            **site_context(),
            "selected_category": selected_category,
            "selected_tag": selected_tag,
            "search_query": search_query,
            "articles_list": page_obj.object_list,
            "page_obj": page_obj,
            "query_string": query_params.urlencode(),
            "start_date": start_date,
            "end_date": end_date,
            "calendar_month": month_date,
            "previous_month": previous_month,
            "next_month": next_month,
            "month_weeks": month_weeks,
            "article_days": article_days,
            "calendar_query": calendar_query.urlencode(),
        },
    )


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    Article.objects.filter(pk=article.pk).update(views=article.views + 1)
    md = markdown.Markdown(
        extensions=[
            "extra",
            "fenced_code",
            "tables",
            TocExtension(permalink=False, slugify=slugify_unicode),
        ]
    )
    article_html = mark_safe(md.convert(article.content))
    article_toc = mark_safe(md.toc)
    return render(
        request,
        "article_detail.html",
        {**site_context(), "article": article, "article_html": article_html, "article_toc": article_toc},
    )


def messages_page(request):
    return render(request, "messages.html", site_context())


def about(request):
    context = site_context()
    profile = context.get("profile")
    about_html = ""
    if profile:
        md = markdown.Markdown(extensions=["extra", "fenced_code", "tables"])
        about_html = mark_safe(md.convert(profile.bio))
    return render(request, "about.html", {**context, "about_html": about_html})


def photos(request):
    life_records_qs = LifeRecord.objects.filter(is_published=True).order_by("-taken_at", "-created_at")
    life_records = list(life_records_qs)
    orbit_records = []
    orbit_count = min(len(life_records), 10)
    ring_tilts = [0, 58, -58]
    ring_durations = [42, 50, 56]
    if orbit_count:
        for index, record in enumerate(life_records[:orbit_count]):
            ring = index % 3
            start_angle = round((360 / orbit_count) * index + ring * 16, 3)
            orbit_records.append(
                {
                    "record": record,
                    "ring": ring,
                    "tilt": ring_tilts[ring],
                    "start_angle": start_angle,
                    "duration": ring_durations[ring],
                    "depth": 1 + (index % 2),
                }
            )
    return render(
        request,
        "photos.html",
        {
            **site_context(),
            "life_records": Paginator(life_records_qs, 20).get_page(request.GET.get("page")),
            "orbit_records": orbit_records,
        },
    )


@require_http_methods(["GET"])
def article_api(request):
    category = request.GET.get("category")
    tag_slug = request.GET.get("tag")
    articles_qs = Article.objects.filter(is_published=True).select_related("category").prefetch_related("tag_nodes")
    if category:
        articles_qs = articles_qs.filter(category__name=category)
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        tag_ids = [tag.id] + [child.id for child in tag.descendants()]
        articles_qs = articles_qs.filter(tag_nodes__id__in=tag_ids).distinct()
    data = [
        {
            "title": article.title,
            "slug": article.slug,
            "summary": article.summary,
            "cover": article.cover_url,
            "category": article.category.name,
            "categoryColor": article.category.color,
            "tags": article.tag_list(),
            "views": article.views,
            "createdAt": article.created_at.strftime("%Y-%m-%d"),
            "url": article.get_absolute_url(),
        }
        for article in articles_qs
    ]
    return JsonResponse({"articles": data})


@require_http_methods(["GET", "POST"])
def message_api(request):
    if request.method == "POST":
        payload = json.loads(request.body.decode("utf-8"))
        parent = None
        parent_id = payload.get("parentId")
        if parent_id:
            parent = Message.objects.filter(pk=parent_id, is_visible=True).first()
        if request.user.is_authenticated:
            name = request.user.username
            email = request.user.email
            user = request.user
        else:
            name = payload.get("name", "匿名访客")[:48] or "匿名访客"
            email = payload.get("email", "")
            user = None
        message = Message.objects.create(
            user=user,
            parent=parent,
            name=name,
            email=email,
            content=payload.get("content", "")[:1200],
        )
        return JsonResponse({"message": serialize_message(message)}, status=201)

    data = [
        serialize_message(item)
        for item in Message.objects.filter(parent__isnull=True, is_visible=True)
        .prefetch_related("replies")
        .select_related("user")[:30]
    ]
    return JsonResponse({"messages": data})


def serialize_message(message):
    return {
        "id": message.id,
        "name": message.name,
        "content": message.content,
        "createdAt": message.created_at.strftime("%Y-%m-%d %H:%M"),
        "isRegistered": bool(message.user_id),
        "replies": [
            {
                "id": reply.id,
                "name": reply.name,
                "content": reply.content,
                "createdAt": reply.created_at.strftime("%Y-%m-%d %H:%M"),
                "isRegistered": bool(reply.user_id),
            }
            for reply in message.replies.filter(is_visible=True).select_related("user")
        ],
    }


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect("/admin/")
        return redirect("messages")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            return redirect("/admin/")
        if user is not None:
            login(request, user)
            return redirect("messages")
        inactive_user = User.objects.filter(username=username, is_active=False).first()
        if inactive_user:
            messages.error(request, "账号还没有完成邮箱验证，请先查看邮箱中的验证链接。")
        else:
            messages.error(request, "账号或密码不正确。")

    return render(request, "login.html", site_context())


def register_view(request):
    if request.method == "POST":
        form = EmailUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            send_activation_email(request, user)
            return render(request, "activation_sent.html", {**site_context(), "email": user.email})
    else:
        form = EmailUserCreationForm()
    return render(request, "register.html", {**site_context(), "form": form})


def send_activation_email(request, user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    activation_url = request.build_absolute_uri(reverse("activate", kwargs={"uidb64": uid, "token": token}))
    subject = "验证你的 Qi Blog 账号"
    message = render_to_string("emails/activation_email.txt", {"user": user, "activation_url": activation_url})
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email], fail_silently=False)


def activate_view(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save(update_fields=["is_active"])
        login(request, user)
        messages.success(request, "邮箱验证完成，可以留言和回复了。")
        return redirect("messages")

    return render(request, "activation_invalid.html", site_context(), status=400)


@login_required
def logout_view(request):
    logout(request)
    return redirect("home")
