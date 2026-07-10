"""
茶猫小栈 - 评论后端服务
FastAPI + SQLite，轻量好养喵~
"""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from admin import router as admin_router

app = FastAPI(title="茶猫小栈评论 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin_router)

DB_PATH = Path(__file__).parent / "comments.db"


class CommentCreate(BaseModel):
    name: str = Field(default="匿名", max_length=32)
    content: str = Field(min_length=1, max_length=1000)


class Comment(CommentCreate):
    id: int
    created_at: str


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL DEFAULT '匿名',
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


@app.get("/api/comments")
def list_comments():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, name, content, created_at FROM comments ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.post("/api/comments", status_code=201)
def create_comment(body: CommentCreate):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    conn = get_db()
    cur = conn.execute(
        "INSERT INTO comments (name, content, created_at) VALUES (?, ?, ?)",
        (body.name, body.content, now),
    )
    conn.commit()
    comment_id = cur.lastrowid
    conn.close()
    return {"id": comment_id, "name": body.name, "content": body.content, "created_at": now}


@app.delete("/api/comments/{comment_id}", status_code=204)
def delete_comment(comment_id: int):
    conn = get_db()
    cur = conn.execute("DELETE FROM comments WHERE id = ?", (comment_id,))
    conn.commit()
    conn.close()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="评论不见啦喵~")


# ---------- 静态文件托管 ----------

FRONTEND_DIST = Path(__file__).resolve().parent.parent / "frontend" / "dist"

# 可上传的图片目录
ASSETS_DIR = Path(__file__).resolve().parent.parent / "frontend" / "src" / "assets"
if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=str(ASSETS_DIR)), name="assets")

if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIST), html=True), name="frontend")
