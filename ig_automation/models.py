from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    DateTime,
    Enum as SAEnum,
    Integer,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

from .database import Base


class PostStatus(str, Enum):
    draft = "draft"
    pending_approval = "pending_approval"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    topic: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[PostStatus] = mapped_column(SAEnum(PostStatus), default=PostStatus.draft, nullable=False)

    ig_container_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ig_media_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    ig_permalink: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    failure_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

