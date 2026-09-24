from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import httpx
from pulse.config import settings


@dataclass(frozen=True)
class Item:
    provider: str
    kind: str
    external_id: str
    creator_id: str | None
    title: str | None
    body: str | None
    url: str
    language: str | None
    published_at: datetime


class ProviderError(Exception):
    def __init__(self, code: str, retry_after: int | None = None):
        self.code = code
        self.retry_after = retry_after


def utc(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def checked(response: httpx.Response) -> dict:
    if response.status_code == 429:
        retry = response.headers.get("Retry-After")
        raise ProviderError("rate_limited", int(retry) if retry and retry.isdigit() else None)
    if response.status_code in (401, 403):
        raise ProviderError("provider_auth_or_permission")
    if response.status_code >= 400:
        raise ProviderError("provider_http_error")
    try:
        return response.json()
    except ValueError as exc:
        raise ProviderError("invalid_provider_response") from exc


def fetch(provider: str, query: str, start: datetime, end: datetime, limit: int) -> tuple[list[Item], str, list[str]]:
    cfg = settings()
    with httpx.Client(timeout=10, follow_redirects=False) as client:
        if provider == "x":
            if not cfg.x_bearer_token:
                raise ProviderError("credential_missing")
            if start < datetime.now(timezone.utc) - timedelta(days=7, minutes=1):
                raise ProviderError("history_unsupported")
            effective_start = max(start, datetime.now(timezone.utc) - timedelta(days=7) + timedelta(minutes=2))
            effective_end = min(end, datetime.now(timezone.utc) - timedelta(seconds=30))
            if effective_start >= effective_end:
                raise ProviderError("history_unsupported")
            params = {"query": query, "start_time": effective_start.isoformat().replace("+00:00", "Z"), "end_time": effective_end.isoformat().replace("+00:00", "Z"), "max_results": max(10, min(limit, 100)), "tweet.fields": "created_at,author_id,lang"}
            data = checked(client.get("https://api.x.com/2/tweets/search/recent", params=params, headers={"Authorization": f"Bearer {cfg.x_bearer_token}"}))
            items = [Item("x", "post", str(p["id"]), p.get("author_id"), None, p.get("text"), f"https://x.com/i/web/status/{p['id']}", p.get("lang"), utc(p["created_at"])) for p in data.get("data", [])]
            return items, query, ["X recent-search sample; provider ordering and pagination limit apply", "Oldest two minutes and latest 30 seconds of a seven-day request may be unavailable", "English requested for analysis; source discovery is not language filtered"]
        if provider == "youtube":
            if not cfg.youtube_api_key:
                raise ProviderError("credential_missing")
            params = {"part": "snippet", "q": query, "type": "video", "maxResults": min(limit, 50), "publishedAfter": start.isoformat().replace("+00:00", "Z"), "publishedBefore": end.isoformat().replace("+00:00", "Z")}
            data = checked(client.get("https://www.googleapis.com/youtube/v3/search", params=params, headers={"x-goog-api-key": cfg.youtube_api_key}))
            items = [Item("youtube", "video", p["id"]["videoId"], p["snippet"].get("channelId"), p["snippet"].get("title"), p["snippet"].get("description"), f"https://www.youtube.com/watch?v={p['id']['videoId']}", None, utc(p["snippet"]["publishedAt"])) for p in data.get("items", []) if p.get("id", {}).get("videoId")]
            return items, query, ["YouTube native search relevance is an approximation of Pulse AND grammar", "Native display only unless derived-use approval is recorded", "English requested for analysis; source discovery is not language filtered"]
        if provider == "reddit":
            if not cfg.reddit_client_id or not cfg.reddit_client_secret:
                raise ProviderError("credential_missing")
            token_data = checked(client.post("https://www.reddit.com/api/v1/access_token", data={"grant_type": "client_credentials"}, auth=(cfg.reddit_client_id, cfg.reddit_client_secret), headers={"User-Agent": cfg.reddit_user_agent}))
            token = token_data.get("access_token")
            if not token:
                raise ProviderError("provider_auth_or_permission")
            data = checked(client.get("https://oauth.reddit.com/search", params={"q": query, "sort": "new", "t": "all", "type": "link", "limit": min(limit, 100), "raw_json": 1}, headers={"Authorization": f"Bearer {token}", "User-Agent": cfg.reddit_user_agent}))
            posts = [p["data"] for p in data.get("data", {}).get("children", []) if p.get("kind") == "t3"]
            items = [Item("reddit", "submission", p["id"], p.get("author_fullname"), p.get("title"), p.get("selftext"), "https://www.reddit.com" + p["permalink"], None, datetime.fromtimestamp(p["created_utc"], timezone.utc)) for p in posts]
            return [p for p in items if start <= p.published_at < end], query, ["Reddit query matching may approximate Pulse AND grammar", "Reddit search has no exact arbitrary date filter; returned items were filtered to the requested interval", "Search results are sampled, not complete network coverage", "English requested for analysis; source discovery is not language filtered"]
    raise ProviderError("unknown_provider")
