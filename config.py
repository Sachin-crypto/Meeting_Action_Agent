import os
from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            f"Check your .env file against .env.example."
        )
    return value


# Scalekit credentials
SCALEKIT_CLIENT_ID = _require("SCALEKIT_CLIENT_ID")
SCALEKIT_CLIENT_SECRET = _require("SCALEKIT_CLIENT_SECRET")
SCALEKIT_ENV_URL = _require("SCALEKIT_ENV_URL")

# Connection names (must match names created in Scalekit dashboard)
ZOOM_CONNECTION_NAME = os.getenv("ZOOM_CONNECTION_NAME", "zoom")
NOTION_CONNECTION_NAME = os.getenv("NOTION_CONNECTION_NAME", "notion")
JIRA_CONNECTION_NAME = os.getenv("JIRA_CONNECTION_NAME", "jira")

# Anthropic
ANTHROPIC_API_KEY = _require("ANTHROPIC_API_KEY")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-5")

# Notion / Jira targets
NOTION_DATABASE_ID = _require("NOTION_DATABASE_ID")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY", "MMN")

# Zoom meeting to fetch recordings/transcript for (spaces are stripped)
ZOOM_MEETING_ID = os.getenv("ZOOM_MEETING_ID", "").replace(" ", "")