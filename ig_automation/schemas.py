from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, HttpUrl, Field

from .models import PostStatus


class PostCreate(BaseModel):
    image_url: HttpUrl
    caption: Optional[str] = None
    topic: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class PostUpdate(BaseModel):
    image_url: Optional[HttpUrl] = None
    caption: Optional[str] = None
    topic: Optional[str] = None
    scheduled_at: Optional[datetime] = None


class PostOut(BaseModel):
    id: int
    image_url: str
    caption: Optional[str]
    topic: Optional[str]
    scheduled_at: Optional[datetime]
    status: PostStatus
    ig_container_id: Optional[str]
    ig_media_id: Optional[str]
    ig_permalink: Optional[str]
    published_at: Optional[datetime]
    metrics: Optional[dict]
    failure_reason: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ApproveRequest(BaseModel):
    scheduled_at: Optional[datetime] = None


class CloneRequest(BaseModel):
    scheduled_at: Optional[datetime] = None
    tweak_caption: Optional[str] = Field(None, description="Override or tweak caption")


class MetricsRefreshResponse(BaseModel):
    success: bool
    updated: int
    detail: Optional[str] = None

