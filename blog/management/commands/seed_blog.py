import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from blog.models import Article, Category, Message, Profile, Tag


class Command(BaseCommand):
    help = "Create initial blog data and an admin account."

    def handle(self, *args, **options):
        life, _ = Category.objects.get_or_create(name="生活记录", defaults={"color": "#f97316"})
        tech, _ = Category.objects.get_or_create(name="技术札记", defaults={"color": "#0f766e"})
        thought, _ = Category.objects.get_or_create(name="随笔", defaults={"color": "#7c3aed"})

        profile, _ = Profile.objects.get_or_create(pk=1)
        profile.name = "Qi Zhang"
        profile.headline = "后端开发者 / 独立开发者 / 生活爱好者 / 工作排斥者 / 懒癌晚期患者"
        profile.bio = (
            "男，22 岁，目前在晋能控股装备制造集团从事煤矿井下作业，同时持续学习和实践后端开发。\n\n"
            "技术方向集中在 Django、Jinja2、MySQL、Redis、Docker、Linux 运维，以及 Python 自动化和数据采集。"
            "也在探索 YOLO、OpenCV 等计算机视觉技术，希望把机械、煤矿装备智能化和软件开发结合起来。\n\n"
            "做过 LinkedIn 数据采集系统、社区管理界面后端、响应式数据展示网站，也用 AutoCAD 和 SolidWorks 做过机械产品 3D 建模。"
            "我的技术风格偏实践派：边做边学，遇到问题就地解决，喜欢把真实需求拆成可以跑起来的系统。"
        )
        profile.email = os.getenv("SEED_PROFILE_EMAIL", "")
        profile.github = "https://github.com/"
        profile.location = "晋城 / China"
        profile.save()

        tag_paths = [
            "技术/Python",
            "技术/Django",
            "技术/Vue",
            "技术/MySQL",
            "技术/Docker",
            "技术/AI/YOLO",
            "生活/日常",
            "写作/思考",
            "项目/独立开发",
        ]
        created_tags = {path: ensure_tag(path) for path in tag_paths}

        articles = [
            {
                "title": "用 Django 和 Vue 打造自己的博客",
                "summary": "从数据模型、后台管理到前端交互，搭一个属于自己的内容系统。",
                "content": """# 起点

这篇文章记录博客系统的第一版设计：Django 负责稳定的数据和后台，Vue 负责轻盈的页面交互。

## 后端

后端先处理文章、分类、留言和个人资料，让数据结构稳定下来。

## 前端

前端不急着复杂化，先把首页、文章列表和留言板做顺手。

## 下一步

继续补 Markdown、弹幕留言、日夜主题和更细的后台管理。""",
                "category": tech,
                "tags": "Django,Vue,Python",
                "tag_paths": ["技术/Django", "技术/Vue", "技术/Python", "项目/独立开发"],
                "is_featured": True,
                "cover": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "写作是一种低速的编程",
                "summary": "文字也有结构、重构、调试和发布，只是反馈更安静。",
                "content": """# 文字的结构

写博客不是为了立刻变得响亮，而是给思考留下可回看的形状。

## 像写代码一样写作

文字也有变量、结构、重构和发布。每一次修改，都是把模糊的想法整理成稳定接口。

## 慢一点

慢并不是低效，它只是让判断变得更清楚。""",
                "category": thought,
                "tags": "写作,思考",
                "tag_paths": ["写作/思考"],
                "cover": "https://images.unsplash.com/photo-1455390582262-044cdead277a?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "今天也要给生活留一点余白",
                "summary": "在学习和开发之外，也记录天气、散步、音乐和一些小小的开心。",
                "content": """# 留白

个人博客最迷人的地方，是它允许一个人完整地出现。

## 技术之外

技术文章之外，天气、散步、音乐和一些小小的开心，也值得被认真保存。

## 日常也有版本

当生活被记录下来，它就有了可以回看的版本历史。""",
                "category": life,
                "tags": "生活,日常",
                "tag_paths": ["生活/日常"],
                "cover": "https://images.unsplash.com/photo-1490730141103-6cac27aaab94?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Django Admin 其实很适合个人内容管理",
                "summary": "不用一开始就造完整 CMS，先把后台变成可靠的写作工作台。",
                "content": """# 先用起来

Django Admin 的价值在于稳定、清楚、够用。

## 管理内容

文章、分类、留言和个人资料都能快速管理，先把写作流程跑顺。

## 慢慢增强

后续再补 Markdown、图片上传和统计面板，比一开始造完整 CMS 更稳。""",
                "category": tech,
                "tags": "Django,后台,CMS",
                "tag_paths": ["技术/Django", "项目/独立开发"],
                "cover": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Vue 放在 Django 里可以很轻",
                "summary": "不是每个页面都需要复杂工程化，合适的小交互能让页面更灵动。",
                "content": """# 轻量 Vue

这版博客采用渐进式 Vue：Django 负责模板与数据，Vue 接管文章筛选和留言提交。

## 适合小站

不是所有页面都需要完整前端工程。小而明确的交互，反而更容易维护。

## 保留扩展空间

以后如果复杂度上来，再拆成独立前端也不晚。""",
                "category": tech,
                "tags": "Vue,前端,Django",
                "tag_paths": ["技术/Vue", "技术/Django"],
                "cover": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "给博客设计一套安静的视觉语言",
                "summary": "好看的页面不一定要用力，留白、层次和色彩克制更重要。",
                "content": """# 安静的界面

个人站点需要表达性，但不需要喧闹。

## 视觉原则

淡色背景、玻璃质感、清晰排版和温和动效，能让读者把注意力放回文字本身。

## 黑夜模式

夜间阅读时降低亮度，让内容仍然清楚，但不刺眼。""",
                "category": thought,
                "tags": "设计,前端,审美",
                "tag_paths": ["写作/思考", "技术/Vue"],
                "cover": "https://images.unsplash.com/photo-1497215728101-856f4ea42174?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "把 MySQL 跑在 Docker 里",
                "summary": "本机开发环境保持干净，数据库服务交给容器管理。",
                "content": """# 容器里的数据库

Docker 中运行 MySQL，可以减少系统环境污染。

## Django 连接

Django 只需要连接到 `127.0.0.1:3306`，就能完成迁移、测试和数据初始化。

## 开发习惯

数据库服务交给容器，项目依赖交给虚拟环境。""",
                "category": tech,
                "tags": "MySQL,Docker,数据库",
                "tag_paths": ["技术/MySQL", "技术/Docker"],
                "cover": "https://images.unsplash.com/photo-1605745341112-85968b19335b?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "为什么要保留留言板",
                "summary": "社交平台很快，留言板很慢，但慢的东西有自己的温度。",
                "content": """# 小客厅

留言板像一个小客厅，读者可以留下问候、建议或一个问题。

## 弹幕墙

弹幕让留言在页面上流动起来，读者一进来就能感到这里有人来过。

## 回复

访客可以直接回复，注册用户也可以用固定身份参与讨论。""",
                "category": life,
                "tags": "留言板,博客,交流",
                "tag_paths": ["生活/日常", "项目/独立开发"],
                "cover": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "从第一篇文章开始维护长期项目",
                "summary": "长期项目不是一开始就完美，而是在一次次小更新里站稳。",
                "content": """# 长期项目

博客也是项目。先把架构跑通，再补内容、优化样式、调整后台体验。

## 小步更新

每一次小修改都会让它更像自己的地方。

## 留下痕迹

贡献图、文章记录和留言，都是长期维护的可视化证据。""",
                "category": thought,
                "tags": "长期主义,项目,写作",
                "tag_paths": ["写作/思考", "项目/独立开发"],
                "cover": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?q=80&w=1200&auto=format&fit=crop",
            },
            {
                "title": "Python 项目的虚拟环境习惯",
                "summary": "每个项目独立依赖，是最朴素也最有效的工程卫生。",
                "content": """# 独立环境

每个 Python 项目都应该有自己的虚拟环境。

## 基本流程

把虚拟环境放在项目目录下，依赖写入 `requirements.txt`，启动前先执行 `source .venv/bin/activate`。

## 长期收益

简单的约定会节省很多未来排查问题的时间。""",
                "category": tech,
                "tags": "Python,虚拟环境,工程化",
                "tag_paths": ["技术/Python", "技术/Docker"],
                "cover": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?q=80&w=1200&auto=format&fit=crop",
            },
        ]
        for data in articles:
            tag_path_values = data.pop("tag_paths", [])
            article, created = Article.objects.get_or_create(title=data["title"], defaults=data)
            if created or not article.content.lstrip().startswith("#"):
                for field, value in data.items():
                    setattr(article, field, value)
                article.save()
            article.tag_nodes.set([created_tags[path] for path in tag_path_values])

        Message.objects.get_or_create(
            name="第一位访客",
            defaults={"content": "博客上线快乐，愿这里一直有新鲜的文字。"},
        )

        User = get_user_model()
        user, created = User.objects.get_or_create(username="admin", defaults={"is_staff": True, "is_superuser": True})
        user.is_staff = True
        user.is_superuser = True
        admin_password = os.getenv("SEED_ADMIN_PASSWORD")
        if admin_password:
            user.set_password(admin_password)
        elif created:
            user.set_unusable_password()
        user.save()

        status = "created" if created else "updated"
        self.stdout.write(self.style.SUCCESS(f"Seed data ready; admin user {status}: admin"))
        if not admin_password:
            self.stdout.write(self.style.WARNING("Set SEED_ADMIN_PASSWORD before running seed_blog if you want a usable admin password."))


def ensure_tag(path_text):
    parent = None
    tag = None
    for name in [part.strip() for part in path_text.split("/") if part.strip()]:
        tag, _ = Tag.objects.get_or_create(parent=parent, name=name)
        parent = tag
    return tag
