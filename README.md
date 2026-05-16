# Qi Blog

Qi Blog 是一个使用 Django + Vue + MySQL 构建的个人博客项目。项目面向个人长期写作、生活记录和留言互动，包含前台博客页面、Markdown 文章系统、留言板、照片墙、背景音乐播放和 Django 管理后台。

## 功能概览

- 首页：头像星环开场、个人签名、建站贡献热力图、最新文章、生活记录横向展示。
- 文章系统：Markdown 正文渲染、文章详情目录、分类筛选、关键词搜索、日期/日期范围筛选、分页归档。
- 多层级标签：后台支持多级标签，导航栏文章子菜单按标签树展示。
- 留言板：访客留言、注册用户留言、回复展示、弹幕展示。
- 照片墙：后台上传生活照片和文字，前台 3D 球形轨道展示最近照片，列表分页展示生活记录。
- 关于我：后台以 Markdown 方式维护个人介绍。
- 背景音乐：后台上传音乐，前台循环播放歌单。
- 后台管理：文章 Markdown 编辑器、文章批量导入、留言回复、生活记录和音乐管理。
- 用户注册：支持邮箱验证激活。

## 技术栈

- 后端：Python, Django 4.2
- 数据库：MySQL
- 前端：Django Template, Vue 3, CSS
- Markdown：Python-Markdown
- 环境变量：python-dotenv
- MySQL 驱动：PyMySQL

## 项目结构

```text
Blog/
├── blog/                    # 核心应用：模型、视图、后台、导入逻辑
│   ├── management/commands/  # 初始化、文章导入、分类整理命令
│   ├── migrations/           # 数据库迁移
│   ├── admin.py              # Django 后台配置
│   ├── importing.py          # Markdown/Notes 导入工具
│   ├── models.py             # 文章、分类、标签、留言、音乐、生活记录等模型
│   ├── urls.py
│   └── views.py
├── blog_project/             # Django 项目配置
├── static/                   # 前台和后台 CSS/JS
├── templates/                # 前台页面和后台自定义模板
├── media/                    # 本地上传文件，默认不提交 Git
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## 本地运行

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd Blog
```

### 2. 创建虚拟环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

复制示例文件：

```bash
cp .env.example .env
```

然后修改 `.env`：

```env
DJANGO_SECRET_KEY=replace-me
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

MYSQL_DATABASE=blog
MYSQL_USER=root
MYSQL_PASSWORD=your-mysql-password
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306

EMAIL_HOST=smtp.mail.me.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

不要把 `.env` 提交到 GitHub。公开仓库只保留 `.env.example`。

### 4. 准备 MySQL

项目默认连接本机 `127.0.0.1:3306` 的 MySQL。可以使用 Docker 启动 MySQL，也可以使用已有 MySQL 服务。

创建数据库：

```sql
CREATE DATABASE blog CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. 初始化数据库

```bash
python manage.py migrate
```

创建后台账号：

```bash
python manage.py createsuperuser
```

也可以使用项目内置初始化命令生成基础数据：

```bash
export SEED_ADMIN_PASSWORD="your-admin-password"
export SEED_PROFILE_EMAIL="your-email@example.com"
python manage.py seed_blog
```

如果没有设置 `SEED_ADMIN_PASSWORD`，初始化命令会创建一个不可直接登录的 admin 用户，请再使用 `createsuperuser` 或在后台重置密码。

### 6. 启动服务

```bash
python manage.py runserver 127.0.0.1:8000
```

访问地址：

- 前台首页：http://127.0.0.1:8000/
- 登录页：http://127.0.0.1:8000/login/
- 后台管理：http://127.0.0.1:8000/admin/

前台不会展示后台入口，后台需要手动输入 `/admin/` 访问。

## 文章与 Markdown

文章正文使用 Markdown 存储和渲染。后台文章编辑页提供左侧编辑、右侧预览的 Markdown 编辑体验。

支持的常用能力：

- 标题层级自动生成详情页右侧目录。
- 代码块、表格、引用等 Markdown 扩展。
- 文章封面支持本地上传，也支持外站图片链接。
- 文章分类固定用于大方向归档，例如“计算机”和“其他”。
- 多层级标签用于导航菜单和文件夹式组织。

## 批量导入文章

后台文章列表页提供 Markdown 批量导入入口。也可以使用命令行导入 Notes 目录中的 Markdown 文件：

```bash
python manage.py import_notes "/path/to/notes"
```

导入逻辑会尝试：

- 从一级标题或文件名推断文章标题。
- 从正文提取摘要。
- 根据文件夹路径生成多层级标签。
- 根据路径关键词归类到“计算机”或“其他”。

## 照片墙和媒体文件

后台“生活记录”支持上传照片和一段文字，前台照片墙会展示：

- 最近照片的 3D 球形轨道。
- 按日期排序的生活记录列表。
- 列表每页最多 20 条。
- 点击照片可放大并查看文字。

`media/` 目录默认被 `.gitignore` 忽略，因为它通常包含个人照片、音乐和上传文件。部署时请用服务器文件存储或对象存储处理媒体文件。

## 背景音乐

后台“背景音乐”支持上传多首音乐：

- 上传 1 首时单曲循环。
- 上传多首时按排序轮播。
- 页面切换时音乐状态会保存在本地，不会重新从头播放。

音乐文件位于 `media/music/`，默认不提交到公开仓库。

## 留言板

留言板支持：

- 匿名访客留言。
- 登录用户留言。
- 用户或访客回复。
- 后台站长回复。
- 前台弹幕展示留言和回复。

后台可以控制留言是否显示。

## 邮箱验证

用户注册后会发送激活邮件。需要在 `.env` 中配置 SMTP：

```env
EMAIL_HOST=smtp.mail.me.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@example.com
```

建议使用邮箱服务商提供的应用专用密码，不要使用主账号密码。

## 常用命令

```bash
# 检查项目配置
python manage.py check

# 运行测试
python manage.py test

# 数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建管理员
python manage.py createsuperuser

# 导入 Notes Markdown
python manage.py import_notes "/path/to/notes"

# 整理文章分类
python manage.py normalize_article_categories
```

## 部署提示

生产环境至少需要调整：

- `DJANGO_DEBUG=0`
- 设置安全的 `DJANGO_SECRET_KEY`
- 配置真实域名到 `DJANGO_ALLOWED_HOSTS`
- 使用稳定的 MySQL 服务
- 配置静态文件收集和 Web 服务
- 配置媒体文件存储
- 配置 HTTPS
- 不要提交 `.env`、`media/`、`.venv/`、`staticfiles/`

## 公开仓库注意事项

本仓库适合公开展示代码，但不应该提交：

- `.env`
- 数据库密码
- 邮箱授权码
- 个人照片和音乐文件
- 虚拟环境 `.venv/`
- `staticfiles/`

如果不小心提交过敏感信息，请立即重置相关密码或授权码。
