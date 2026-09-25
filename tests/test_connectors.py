from datetime import datetime, timedelta, timezone
import pytest
import respx
from httpx import Response
from pulse.config import settings
from pulse.connectors.live import ProviderError, checked, fetch


def window():
    end = datetime.now(timezone.utc) - timedelta(minutes=1)
    return end - timedelta(days=2), end


def test_x_payment_required_is_not_retryable():
    with pytest.raises(ProviderError) as error:
        checked(Response(402, json={"detail": "credits depleted"}))
    assert error.value.code == "provider_credits_depleted"


@respx.mock
def test_x_normalization():
    cfg = settings()
    object.__setattr__(cfg, "x_bearer_token", "test")
    start, end = window()
    respx.get("https://api.x.com/2/tweets/search/recent").mock(return_value=Response(200, json={"data": [{"id": "123", "author_id": "456", "text": "AI agents are useful", "lang": "en", "created_at": (end-timedelta(hours=1)).isoformat()}]}))
    items, _, warnings = fetch("x", "AI agents", start, end, 10)
    assert items[0].url == "https://x.com/i/web/status/123"
    assert items[0].language == "en"
    assert warnings
    settings.cache_clear()


@respx.mock
def test_youtube_normalization():
    cfg = settings()
    object.__setattr__(cfg, "youtube_api_key", "test")
    start, end = window()
    route = respx.get("https://www.googleapis.com/youtube/v3/search").mock(return_value=Response(200, json={"items": [{"id": {"videoId": "abc"}, "snippet": {"channelId": "channel", "title": "AI agents", "description": "A video", "publishedAt": (end-timedelta(hours=1)).isoformat()}}]}))
    items, _, _ = fetch("youtube", "AI agents", start, end, 10)
    assert items[0].kind == "video"
    assert items[0].url == "https://www.youtube.com/watch?v=abc"
    assert route.calls.last.request.headers["x-goog-api-key"] == "test"
    assert "key=" not in str(route.calls.last.request.url)
    settings.cache_clear()


@respx.mock
def test_reddit_normalization_and_date_filter():
    cfg = settings()
    object.__setattr__(cfg, "reddit_client_id", "test")
    object.__setattr__(cfg, "reddit_client_secret", "test")
    start, end = window()
    respx.post("https://www.reddit.com/api/v1/access_token").mock(return_value=Response(200, json={"access_token": "token"}))
    respx.get("https://oauth.reddit.com/search").mock(return_value=Response(200, json={"data": {"children": [{"kind": "t3", "data": {"id": "abc", "author_fullname": "t2_x", "title": "AI agents", "selftext": "Discussion", "permalink": "/r/example/comments/abc", "created_utc": (end-timedelta(hours=1)).timestamp()}}, {"kind": "t3", "data": {"id": "old", "title": "Old", "permalink": "/r/example/comments/old", "created_utc": (start-timedelta(days=1)).timestamp()}}]}}))
    items, _, _ = fetch("reddit", "AI agents", start, end, 10)
    assert [item.external_id for item in items] == ["abc"]
    settings.cache_clear()
