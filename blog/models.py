from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField("分类名", max_length=64, unique=True)
    color = models.CharField("主题色", max_length=24, default="#16a085")

    class Meta:
        verbose_name = "文章分类"
        verbose_name_plural = "文章分类"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField("标签名", max_length=64)
    slug = models.SlugField("链接别名", max_length=100, unique=True, blank=True)
    parent = models.ForeignKey(
        "self",
        verbose_name="上级标签",
        related_name="children",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    color = models.CharField("主题色", max_length=24, default="#2f6df6")

    class Meta:
        verbose_name = "文章标签"
        verbose_name_plural = "文章标签"
        ordering = ["parent__id", "name"]
        unique_together = ("parent", "name")

    def save(self, *args, **kwargs):
        if not self.slug:
            names = [self.name]
            parent = self.parent
            while parent:
                names.insert(0, parent.name)
                parent = parent.parent
            base = slugify("-".join(names), allow_unicode=True) or "tag"
            slug = base
            index = 1
            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    def descendants(self):
        children = list(self.children.all())
        result = []
        for child in children:
            result.append(child)
            result.extend(child.descendants())
        return result

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField("标题", max_length=160)
    slug = models.SlugField("链接别名", max_length=180, unique=True, blank=True)
    summary = models.CharField("摘要", max_length=260)
    content = models.TextField("正文")
    cover = models.URLField("外站封面图链接", blank=True)
    cover_file = models.FileField("本地封面图", upload_to="article_covers/", blank=True)
    category = models.ForeignKey(Category, verbose_name="分类", on_delete=models.PROTECT)
    tags = models.CharField("旧标签文本", max_length=160, blank=True, help_text="兼容旧数据，用逗号分隔")
    tag_nodes = models.ManyToManyField(Tag, verbose_name="多层级标签", blank=True, related_name="articles")
    is_featured = models.BooleanField("首页推荐", default=False)
    is_published = models.BooleanField("发布", default=True)
    views = models.PositiveIntegerField("阅读量", default=0)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        verbose_name = "文章"
        verbose_name_plural = "文章"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "article"
            slug = base
            index = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("article_detail", kwargs={"slug": self.slug})

    @property
    def cover_url(self):
        if self.cover_file:
            return self.cover_file.url
        return self.cover

    def tag_list(self):
        names = [tag.name for tag in self.tag_nodes.all()]
        names.extend(tag.strip() for tag in self.tags.split(",") if tag.strip())
        return list(dict.fromkeys(names))

    def __str__(self):
        return self.title


class Message(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="注册用户",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    parent = models.ForeignKey(
        "self",
        verbose_name="回复对象",
        related_name="replies",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    name = models.CharField("昵称", max_length=48)
    email = models.EmailField("邮箱", blank=True)
    content = models.TextField("留言")
    is_visible = models.BooleanField("前台显示", default=True)
    created_at = models.DateTimeField("留言时间", auto_now_add=True)

    class Meta:
        verbose_name = "留言"
        verbose_name_plural = "留言"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}: {self.content[:24]}"


class BackgroundMusic(models.Model):
    title = models.CharField("曲名", max_length=120)
    audio = models.FileField("音频文件", upload_to="music/")
    is_active = models.BooleanField("启用", default=True)
    sort_order = models.PositiveIntegerField("播放顺序", default=0)
    created_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        verbose_name = "背景音乐"
        verbose_name_plural = "背景音乐"
        ordering = ["sort_order", "created_at"]

    def __str__(self):
        return self.title


class LifeRecord(models.Model):
    photo = models.FileField("照片", upload_to="life/")
    note = models.TextField("当时想说的话")
    taken_at = models.DateField("记录日期")
    is_published = models.BooleanField("前台显示", default=True)
    created_at = models.DateTimeField("上传时间", auto_now_add=True)

    class Meta:
        verbose_name = "生活记录"
        verbose_name_plural = "生活记录"
        ordering = ["-taken_at", "-created_at"]

    def __str__(self):
        return f"{self.taken_at} 生活记录"


class Profile(models.Model):
    name = models.CharField("姓名", max_length=64, default="Qi Zhang")
    headline = models.CharField("一句话介绍", max_length=160)
    bio = models.TextField("关于我")
    email = models.EmailField("联系邮箱", blank=True)
    github = models.URLField("GitHub", blank=True)
    location = models.CharField("所在地", max_length=80, blank=True)

    class Meta:
        verbose_name = "个人资料"
        verbose_name_plural = "个人资料"

    def __str__(self):
        return self.name
