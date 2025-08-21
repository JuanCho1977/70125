from __future__ import annotations

from typing import Optional

import requests

from .config import settings


class InstagramClient:
    def __init__(self, access_token: Optional[str] = None) -> None:
        self.base = settings.ig_graph_api_base.rstrip("/")
        self.user_id = settings.ig_user_id
        self.access_token = access_token or settings.access_token

    def _require(self) -> None:
        if not (self.user_id and self.access_token):
            raise RuntimeError("Missing IG_USER_ID or ACCESS_TOKEN. Configure .env")

    def create_image_container(self, image_url: str, caption: Optional[str]) -> str:
        self._require()
        url = f"{self.base}/{self.user_id}/media"
        params = {
            "image_url": image_url,
            "caption": caption or "",
            "access_token": self.access_token,
        }
        resp = requests.post(url, data=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return data.get("id")

    def publish_container(self, creation_id: str) -> dict:
        self._require()
        url = f"{self.base}/{self.user_id}/media_publish"
        params = {
            "creation_id": creation_id,
            "access_token": self.access_token,
        }
        resp = requests.post(url, data=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_media(self, media_id: str) -> dict:
        self._require()
        url = f"{self.base}/{media_id}"
        params = {
            "fields": "id,permalink,media_type,caption,timestamp",
            "access_token": self.access_token,
        }
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_media_insights(self, media_id: str) -> dict:
        self._require()
        url = f"{self.base}/{media_id}/insights"
        params = {
            "metric": "impressions,reach,engagement,saved,likes,comments",
            "access_token": self.access_token,
        }
        resp = requests.get(url, params=params, timeout=30)
        # Not all metrics are always available; soft-fail to empty
        if resp.status_code != 200:
            return {"metrics_raw": {"status": resp.status_code, "body": resp.text}}
        return resp.json()

