from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), default="匿名")
    content = Column(Text, nullable=False)
    page = Column(String(100), default="/")  # which page this comment belongs to
    created_at = Column(DateTime(timezone=True), server_default=func.now())
