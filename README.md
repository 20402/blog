# 茶猫小栈 🐱

一杯茶，一只猫，一整个世界。

---

## 🚀 启动

```bash
cd backend && bash run.sh
```

第一次启动会自动构建前端，之后打开 **http://localhost:8000/** 就能看到博客啦~

---

## 📖 使用指南

### 🌐 博客前端
| 地址 | 说明 |
|---|---|
| `http://localhost:8000/` | 首页 |
| `http://localhost:8000/about/` | 关于 |
| `http://localhost:8000/links/` | 友链 |
| `http://localhost:8000/comment/` | 留言板 |

### 🔧 管理后台
**地址：** `http://localhost:8000/admin/`

**密码：** `cat123`（可通过环境变量 `BLOG_ADMIN_PASSWORD` 修改）

管理后台可以：
- 📝 **写文章** — Markdown 编辑器，实时预览
- ✏️ **编辑/删除文章** — 文章列表直接操作
- ⚙️ **设置** — 修改头像、名字、简介、GitHub 链接、友链、关于页面内容

> 在管理后台保存后，前端会自动重新构建，刷新博客即可看到更新。

### 💬 评论 API
| 方法 | 地址 | 说明 |
|---|---|---|
| `GET` | `/api/comments` | 获取所有评论 |
| `POST` | `/api/comments` | 发表评论 |
| `DELETE` | `/api/comments/{id}` | 删除评论 |

### 🔌 API 文档
`http://localhost:8000/docs` — Swagger 交互式文档

---

## 🖼️ 更换背景

直接把图片放到 `frontend/src/assets/images/` 目录下，然后修改 `frontend/src/config.ts` 第 27 行的文件名：

```ts
src: "assets/images/你的图片文件名",
```

记得图片名不要有空格喵~改完重启 `bash run.sh` 就生效了！

---

## 🛠️ 常用命令

```bash
# 启动博客
cd backend && bash run.sh

# 杀掉占用 8000 端口的进程
cd backend && bash run.sh kill

# 单独构建前端
cd frontend && pnpm run build

# 单独启动后端 API（不构建前端）
cd backend && .venv/bin/python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 前端开发模式（热更新）
cd frontend && pnpm run dev
```

---

## 🏗️ 项目结构

```
blog/
├── backend/              # 后端 (FastAPI + SQLite)
│   ├── main.py           # 应用入口，统一托管前端+API
│   ├── admin.py          # 管理后台 API（文章 CRUD + 配置 + 重建）
│   ├── run.sh            # 一键启动脚本
│   └── .venv/            # Python 虚拟环境
│
└── frontend/             # 前端 (Astro + Fuwari 主题)
    ├── src/
    │   ├── config.ts     # 博客配置（标题、导航、主题）
    │   ├── config.json   # 管理后台可编辑的配置（头像、简介、友链等）
    │   ├── pages/        # 页面
    │   ├── components/   # 组件
    │   │   └── admin/
    │   │       └── AdminApp.svelte  # 管理后台 SPA
    │   └── content/      # 文章 (Markdown)
    ├── dist/             # 构建产物（由 pnpm build 生成）
    └── package.json
```

---

## 🔑 技术栈

- **前端：** Astro + Fuwari 主题 (TypeScript / Svelte / Tailwind)
- **后端：** FastAPI + SQLite (Python)
- **包管理：** pnpm (前端) / uv (后端)
