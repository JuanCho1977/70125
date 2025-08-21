from __future__ import annotations

from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler

from .services import session_scope, find_due_posts, publish_post


def publish_due_posts_job() -> None:
    now = datetime.now(timezone.utc)
    with session_scope() as session:
        due = find_due_posts(session, now=now)
        for post in due:
            publish_post(session, post.id)


def create_scheduler() -> BackgroundScheduler:
    scheduler = BackgroundScheduler(timezone="UTC")
    scheduler.add_job(publish_due_posts_job, "interval", seconds=30, id="publish_due_posts")
    return scheduler

