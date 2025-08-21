from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Post, PostStatus
from .ig_client import InstagramClient


@contextmanager
def session_scope() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_post(session: Session, *, image_url: str, caption: Optional[str], topic: Optional[str], scheduled_at: Optional[datetime]) -> Post:
    post = Post(image_url=str(image_url), caption=caption, topic=topic, scheduled_at=scheduled_at, status=PostStatus.draft)
    session.add(post)
    session.flush()
    return post


def submit_for_approval(session: Session, post_id: int) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    post.status = PostStatus.pending_approval
    session.flush()
    return post


def approve_post(session: Session, post_id: int, *, scheduled_at: Optional[datetime] = None) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    if scheduled_at:
        post.scheduled_at = scheduled_at
    post.status = PostStatus.approved
    session.flush()
    return post


def schedule_post(session: Session, post_id: int, *, scheduled_at: datetime) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    post.scheduled_at = scheduled_at
    post.status = PostStatus.scheduled
    session.flush()
    return post


def publish_post(session: Session, post_id: int, *, ig: Optional[InstagramClient] = None) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    if not post.image_url:
        raise ValueError("Post missing image_url")

    ig = ig or InstagramClient()

    try:
        container_id = ig.create_image_container(post.image_url, post.caption)
        post.ig_container_id = container_id
        publish_data = ig.publish_container(container_id)
        media_id = publish_data.get("id") or publish_data.get("media_id")
        post.ig_media_id = media_id
        if media_id:
            media = ig.get_media(media_id)
            post.ig_permalink = media.get("permalink")
        post.status = PostStatus.published
        post.published_at = datetime.now(timezone.utc)
        session.flush()
        return post
    except Exception as exc:  # noqa: BLE001
        post.status = PostStatus.failed
        post.failure_reason = str(exc)
        session.flush()
        return post


def refresh_metrics(session: Session, post_id: int, *, ig: Optional[InstagramClient] = None) -> Post:
    post = session.get(Post, post_id)
    if not post:
        raise ValueError("Post not found")
    if not post.ig_media_id:
        raise ValueError("Post has no media_id yet")
    ig = ig or InstagramClient()
    metrics = ig.get_media_insights(post.ig_media_id)
    post.metrics = metrics
    session.flush()
    return post


def refresh_metrics_all(session: Session, *, ig: Optional[InstagramClient] = None) -> int:
    stmt = select(Post).where(Post.ig_media_id.is_not(None))
    posts = session.execute(stmt).scalars().all()
    count = 0
    for p in posts:
        try:
            refresh_metrics(session, p.id, ig=ig)
            count += 1
        except Exception:
            continue
    return count


def find_due_posts(session: Session, *, now: datetime) -> list[Post]:
    stmt = select(Post).where(
        Post.status.in_([PostStatus.approved, PostStatus.scheduled]),
        Post.scheduled_at.is_not(None),
        Post.scheduled_at <= now,
    )
    return session.execute(stmt).scalars().all()


def clone_post(session: Session, post_id: int, *, scheduled_at: Optional[datetime], tweak_caption: Optional[str]) -> Post:
    original = session.get(Post, post_id)
    if not original:
        raise ValueError("Post not found")
    caption = tweak_caption if tweak_caption is not None else original.caption
    clone = Post(
        image_url=original.image_url,
        caption=caption,
        topic=original.topic,
        scheduled_at=scheduled_at,
        status=PostStatus.draft,
    )
    session.add(clone)
    session.flush()
    return clone

