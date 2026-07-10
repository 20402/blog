"""
茶猫小栈 - 博客管理 API
纯 API 路由，管理界面在前端~
"""

import os
import re
import secrets
from datetime import date
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

# 文章存放路径
POSTS_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "content" / "posts"
POSTS_DIR.mkdir(parents=True, exist_ok=True)

# 管理员密码（可通过环境变量设置）
ADMIN_PASSWORD = os.environ.get("BLOG_ADMIN_PASSWORD", "cat123")

# 简单 token 存储
_tokens: set[str] = set()

router = APIRouter(prefix="/api/admin", tags=["管理后台"])


def _verify_token(token: str) -> bool:
    return token in _tokens


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """解析 Markdown frontmatter，返回 (元数据, 正文)"""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", text, re.DOTALL)
    if not m:
        return {}, text.strip()

    meta = {}
    for line in m.group(1).strip().split("\n"):
        if ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith("[") and val.endswith("]"):
                val = [v.strip().strip('"').strip("'") for v in val[1:-1].split(",") if v.strip()]
            meta[key] = val
    return meta, m.group(2).strip()


def _build_frontmatter(meta: dict) -> str:
    """生成 frontmatter 字符串"""
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            items = ", ".join(f'"{i}"' for i in v)
            lines.append(f"{k}: [{items}]")
        elif isinstance(v, bool):
            lines.append(f"{k}: {str(v).lower()}")
        else:
            lines.append(f'{k}: "{v}"')
    lines.append("---")
    return "\n".join(lines)


def _slugify(title: str) -> str:
    """从标题生成 slug"""
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s)
    return s.strip("-") or "untitled"


def _list_posts():
    """列出所有文章"""
    posts = []
    for f in sorted(POSTS_DIR.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True):
        content = f.read_text(encoding="utf-8")
        meta, body = _parse_frontmatter(content)
        slug = f.stem
        posts.append({
            "slug": slug,
            "title": meta.get("title", slug),
            "published": str(meta.get("published", "")),
            "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
            "category": meta.get("category", ""),
            "draft": meta.get("draft", False) in (True, "true", "True"),
            "description": meta.get("description", ""),
            "word_count": len(body),
        })
    return posts


# ---------- 鉴权依赖 ----------

async def require_token(request: Request):
    token = request.headers.get("X-Admin-Token", "")
    if not _verify_token(token):
        raise HTTPException(status_code=401, detail="请先登录喵~")


# ---------- API ----------

class LoginBody(BaseModel):
    password: str


@router.post("/login")
def login(body: LoginBody):
    if body.password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="密码不对哟喵~")
    token = secrets.token_hex(32)
    _tokens.add(token)
    return {"token": token}


@router.get("/posts", dependencies=[Depends(require_token)])
def list_posts():
    return _list_posts()


@router.get("/posts/{slug}", dependencies=[Depends(require_token)])
def get_post(slug: str):
    fp = POSTS_DIR / f"{slug}.md"
    if not fp.exists():
        dir_fp = POSTS_DIR / slug / "index.md"
        if dir_fp.exists():
            fp = dir_fp
        else:
            raise HTTPException(status_code=404, detail="文章不见啦喵~")
    content = fp.read_text(encoding="utf-8")
    meta, body = _parse_frontmatter(content)
    return {
        "slug": slug,
        "title": meta.get("title", slug),
        "published": str(meta.get("published", "")),
        "tags": meta.get("tags", []) if isinstance(meta.get("tags"), list) else [],
        "category": meta.get("category", ""),
        "draft": meta.get("draft", False) in (True, "true", "True"),
        "description": meta.get("description", ""),
        "body": body,
    }


class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    published: str = ""
    tags: list[str] = []
    category: str = ""
    draft: bool = True
    description: str = ""
    body: str = ""


class PostUpdate(PostCreate):
    slug: Optional[str] = None


@router.post("/posts", status_code=201, dependencies=[Depends(require_token)])
def create_post(data: PostCreate):
    slug = _slugify(data.title)
    fp = POSTS_DIR / f"{slug}.md"
    if fp.exists():
        i = 2
        while fp.exists():
            fp = POSTS_DIR / f"{slug}-{i}.md"
            i += 1
        slug = fp.stem

    meta = {
        "title": data.title,
        "published": data.published or date.today().isoformat(),
        "description": data.description,
        "tags": data.tags,
        "category": data.category,
        "draft": data.draft,
    }

    frontmatter = _build_frontmatter(meta)
    content = f"{frontmatter}\n\n{data.body.strip()}\n"
    fp.write_text(content, encoding="utf-8")
    return {"slug": slug, "message": f"文章《{data.title}》创建成功喵~"}


@router.put("/posts/{slug}", dependencies=[Depends(require_token)])
def update_post(slug: str, data: PostUpdate):
    fp = POSTS_DIR / f"{slug}.md"
    if not fp.exists():
        dir_fp = POSTS_DIR / slug / "index.md"
        if dir_fp.exists():
            fp = dir_fp
        else:
            raise HTTPException(status_code=404, detail="文章不见啦喵~")

    meta = {
        "title": data.title,
        "published": data.published or date.today().isoformat(),
        "description": data.description,
        "tags": data.tags,
        "category": data.category,
        "draft": data.draft,
    }
    frontmatter = _build_frontmatter(meta)
    content = f"{frontmatter}\n\n{data.body.strip()}\n"
    fp.write_text(content, encoding="utf-8")

    new_slug = data.slug if data.slug else slug
    if new_slug != slug:
        new_fp = POSTS_DIR / f"{new_slug}.md"
        if new_fp.exists():
            raise HTTPException(status_code=409, detail="新 slug 已被占用喵~")
        fp.rename(new_fp)

    return {"slug": new_slug, "message": f"文章《{data.title}》更新成功喵~"}


@router.delete("/posts/{slug}", status_code=204, dependencies=[Depends(require_token)])
def delete_post(slug: str):
    fp = POSTS_DIR / f"{slug}.md"
    if fp.exists():
        fp.unlink()
        return
    dir_fp = POSTS_DIR / slug / "index.md"
    if dir_fp.exists():
        dir_fp.unlink()
        (POSTS_DIR / slug).rmdir()
        return
    raise HTTPException(status_code=404, detail="文章不见啦喵~")


# ---------- 博客配置 ----------

import json

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"
CONFIG_PATH = FRONTEND_DIR / "src" / "config.json"


@router.get("/config", dependencies=[Depends(require_token)])
def get_config():
    if not CONFIG_PATH.exists():
        return {"profile": {}, "friends": [], "about": ""}
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


class FriendLink(BaseModel):
    name: str = ""
    url: str = ""
    avatar: str = ""


class ProfileConfig(BaseModel):
    avatar: str = ""
    name: str = ""
    bio: str = ""
    github: str = ""


class BlogConfig(BaseModel):
    profile: ProfileConfig = ProfileConfig()
    friends: list[FriendLink] = []
    about: str = ""


@router.put("/config", dependencies=[Depends(require_token)])
def update_config(data: BlogConfig):
    raw = {
        "profile": data.profile.model_dump(),
        "friends": [f.model_dump() for f in data.friends],
        "about": data.about,
    }
    CONFIG_PATH.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"success": True, "message": "配置保存成功喵~"}


# ---------- 文件上传 ----------

from fastapi import UploadFile, File, Form
import uuid

IMAGES_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "assets" / "images"
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_TYPES = {"avatar", "banner"}


@router.post("/upload", dependencies=[Depends(require_token)])
async def upload_image(file: UploadFile = File(...), type: str = Form("avatar")):
    if type not in ALLOWED_TYPES:
        raise HTTPException(status_code=400, detail="type 必须是 avatar 或 banner 喵~")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="只能上传图片喵~")

    ext = Path(file.filename).suffix if file.filename else ".png"
    filename = f"{type}-{uuid.uuid4().hex[:8]}{ext}"
    dest = IMAGES_DIR / filename

    content = await file.read()
    dest.write_bytes(content)

    rel_path = f"assets/images/{filename}"
    return {"path": rel_path, "message": f"头像上传成功喵~"}


# ---------- 评论管理 ----------

import sqlite3

COMMENTS_DB = Path(__file__).parent / "comments.db"


@router.get("/comments", dependencies=[Depends(require_token)])
def list_comments_admin():
    if not COMMENTS_DB.exists():
        return []
    conn = sqlite3.connect(str(COMMENTS_DB))
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT id, name, content, created_at FROM comments ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.delete("/comments/{comment_id}", status_code=204, dependencies=[Depends(require_token)])
def delete_comment_admin(comment_id: int):
    if not COMMENTS_DB.exists():
        raise HTTPException(status_code=404)
    conn = sqlite3.connect(str(COMMENTS_DB))
    cur = conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="评论不见啦喵~")


# ---------- 前端重建 ----------

import subprocess
import sys


@router.post("/rebuild", dependencies=[Depends(require_token)])
def rebuild_frontend():
    """重新构建前端静态页面"""
    try:
        result = subprocess.run(
            ["pnpm", "run", "build"],
            cwd=str(FRONTEND_DIR),
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode != 0:
            return {"success": False, "error": (result.stderr or result.stdout)[:500]}
        return {"success": True, "message": "前端重建成功喵~"}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "构建超时啦喵~"}
    except Exception as e:
        return {"success": False, "error": str(e)}
