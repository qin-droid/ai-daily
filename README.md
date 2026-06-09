# 🤖 AI 日报

> 每日 AI 资讯 + GitHub 趋势，自动汇总发布。

## 🚀 快速开始

这是一个完全静态的博客站点，托管在 GitHub Pages，零成本。

### 本地预览

```bash
# 直接用浏览器打开
open index.html
# 或启动简易服务器
python -m http.server 8080
```

### 部署到 GitHub Pages

1. 创建 GitHub 仓库 `ai-daily`
2. 推送代码：
```bash
git init
git add .
git commit -m "feat: initial blog setup"
git branch -M main
git remote add origin https://github.com/<你的用户名>/ai-daily.git
git push -u origin main
```
3. 在仓库 Settings → Pages 中启用：
   - Source: Deploy from a branch
   - Branch: `main`
   - Folder: `/ (root)`
4. 等待 2 分钟，访问 `https://<你的用户名>.github.io/ai-daily/`

### 自动发布

```bash
# 手动运行
python auto_publish.py

# 或者设置 cron（每日 8:00 自动发布）
# Linux/Mac: crontab -e
# Windows: 任务计划程序
```

## 📂 目录结构

```
ai-daily/
├── index.html          # 首页（博客文章列表）
├── articles.json       # 文章数据（自动更新）
├── feed.xml            # RSS 订阅
├── auto_publish.py     # 自动发布脚本
├── README.md           # 本文件
└── articles/           # 文章详情页
    ├── 2026-06-09-ai-news.html
    └── 2026-06-09-github-trending.html
```

## 🔄 自动更新流程

```
7:00  cron → 每日AI资讯 → 桌面/每日AI资讯/YYYY-MM-DD.md
7:30  cron → GitHub趋势 → 桌面/GitHub趋势日报/YYYY-MM-DD.md
8:00  cron → auto_publish.py → 转换 → 推送到 GitHub Pages
```

## 📡 RSS 订阅

`https://<你的用户名>.github.io/ai-daily/feed.xml`

## 🛠️ 技术栈

- 纯静态 HTML/CSS/JS（零依赖）
- 自动暗色模式 (prefers-color-scheme)
- RSS 2.0
- JSON 数据驱动
- GitHub Pages 托管（免费）

## 📝 License

MIT
