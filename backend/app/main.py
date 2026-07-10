from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import DATABASE_URL, Base
from app.models import Comment

app = FastAPI(title="茶猫小栈 API", version="0.1.0")

# CORS - 允许局域网访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


class CommentCreate(BaseModel):
    name: str = "匿名"
    content: str
    page: str = "/"


class CommentOut(BaseModel):
    id: int
    name: str
    content: str
    page: str
    created_at: str

    model_config = {"from_attributes": True}


@app.get("/api/comments")
def get_comments(page: str = "/"):
    db = SessionLocal()
    comments = (
        db.query(Comment)
        .filter(Comment.page == page)
        .order_by(Comment.created_at.desc())
        .limit(50)
        .all()
    )
    db.close()
    return [
        CommentOut(
            id=c.id,
            name=c.name,
            content=c.content,
            page=c.page,
            created_at=c.created_at.isoformat() if c.created_at else "",
        )
        for c in comments
    ]


@app.post("/api/comments", status_code=201)
def create_comment(comment: CommentCreate):
    db = SessionLocal()
    db_comment = Comment(
        name=comment.name.strip() or "匿名",
        content=comment.content.strip(),
        page=comment.page or "/",
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    db.close()
    return {
        "id": db_comment.id,
        "name": db_comment.name,
        "content": db_comment.content,
        "page": db_comment.page,
        "created_at": db_comment.created_at.isoformat() if db_comment.created_at else "",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "blog": "茶猫小栈"}
