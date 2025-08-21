import os
from dataclasses import dataclass
from dotenv import load_dotenv


load_dotenv()


@dataclass
class Settings:
    ig_graph_api_base: str = os.getenv("IG_GRAPH_API_BASE", "https://graph.facebook.com/v21.0")
    ig_user_id: str | None = os.getenv("IG_USER_ID")
    facebook_page_id: str | None = os.getenv("FACEBOOK_PAGE_ID")
    access_token: str | None = os.getenv("ACCESS_TOKEN")
    app_secret: str | None = os.getenv("APP_SECRET")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:////workspace/ig_automation/app.db")
    timezone: str = os.getenv("TIMEZONE", "UTC")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")


settings = Settings()
