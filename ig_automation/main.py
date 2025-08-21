from __future__ import annotations

from fastapi import FastAPI, HTTPException
from sqlalchemy.orm import Session

from .database import engine, Base, SessionLocal
from .schemas import PostCreate, PostUpdate, PostOut, ApproveRequest, CloneRequest, MetricsRefreshResponse
from .services import (
    create_post as svc_create_post,
    submit_for_approval as svc_submit_for_approval,
    approve_post as svc_approve_post,
    schedule_post as svc_schedule_post,
    publish_post as svc_publish_post,
    refresh_metrics as svc_refresh_metrics,
    refresh_metrics_all as svc_refresh_metrics_all,
    clone_post as svc_clone_post,
)
from .models import Post
from .scheduler import create_scheduler


app = FastAPI(title="IG Automation Service")


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)
    scheduler = create_scheduler()
    scheduler.start()


@app.post("/posts", response_model=PostOut)
def create_post(payload: PostCreate) -> Post:
    with SessionLocal() as session:
        post = svc_create_post(
            session,
            image_url=str(payload.image_url),
            caption=payload.caption,
            topic=payload.topic,
            scheduled_at=payload.scheduled_at,
        )
        session.commit()
        session.refresh(post)
        return post


@app.get("/posts/{post_id}", response_model=PostOut)
def get_post(post_id: int) -> Post:
    with SessionLocal() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        return post


@app.patch("/posts/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate) -> Post:
    with SessionLocal() as session:
        post = session.get(Post, post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        if payload.image_url is not None:
            post.image_url = str(payload.image_url)
        if payload.caption is not None:
            post.caption = payload.caption
        if payload.topic is not None:
            post.topic = payload.topic
        if payload.scheduled_at is not None:
            post.scheduled_at = payload.scheduled_at
        session.commit()
        session.refresh(post)
        return post


@app.post("/posts/{post_id}/submit-for-approval", response_model=PostOut)
def submit_for_approval(post_id: int) -> Post:
    with SessionLocal() as session:
        try:
            post = svc_submit_for_approval(session, post_id)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/posts/{post_id}/approve", response_model=PostOut)
def approve(post_id: int, payload: ApproveRequest) -> Post:
    with SessionLocal() as session:
        try:
            post = svc_approve_post(session, post_id, scheduled_at=payload.scheduled_at)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/posts/{post_id}/schedule", response_model=PostOut)
def schedule(post_id: int, payload: ApproveRequest) -> Post:
    if payload.scheduled_at is None:
        raise HTTPException(status_code=400, detail="scheduled_at is required")
    with SessionLocal() as session:
        try:
            post = svc_schedule_post(session, post_id, scheduled_at=payload.scheduled_at)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/posts/{post_id}/publish", response_model=PostOut)
def publish(post_id: int) -> Post:
    with SessionLocal() as session:
        try:
            post = svc_publish_post(session, post_id)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/posts/{post_id}/metrics/refresh", response_model=PostOut)
def refresh_metrics(post_id: int) -> Post:
    with SessionLocal() as session:
        try:
            post = svc_refresh_metrics(session, post_id)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e


@app.post("/metrics/refresh-all", response_model=MetricsRefreshResponse)
def refresh_metrics_all() -> MetricsRefreshResponse:
    with SessionLocal() as session:
        updated = svc_refresh_metrics_all(session)
        session.commit()
        return MetricsRefreshResponse(success=True, updated=updated)


@app.post("/posts/{post_id}/clone", response_model=PostOut)
def clone(post_id: int, payload: CloneRequest) -> Post:
    with SessionLocal() as session:
        try:
            post = svc_clone_post(session, post_id, scheduled_at=payload.scheduled_at, tweak_caption=payload.tweak_caption)
            session.commit()
            session.refresh(post)
            return post
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e)) from e

