import httpx
import pytest

from app import service_client


class _FakeResponse:
    def __init__(self, status_code: int = 200):
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("POST", service_client.SERVICE_URL),
                response=httpx.Response(self.status_code),
            )


class _FakeAsyncClient:
    """Stand-in for httpx.AsyncClient that records the POST call."""

    calls: list[dict] = []
    status_code = 200

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    async def post(self, url, json=None):
        type(self).calls.append({"url": url, "json": json})
        return _FakeResponse(type(self).status_code)


@pytest.fixture(autouse=True)
def fake_httpx(monkeypatch):
    _FakeAsyncClient.calls = []
    _FakeAsyncClient.status_code = 200
    monkeypatch.setattr(httpx, "AsyncClient", _FakeAsyncClient)
    return _FakeAsyncClient


async def test_posts_payload_to_service_url(fake_httpx):
    payload = {"username": "alice", "cheating_detected": True}

    await service_client.send_cheating_event(payload)

    assert fake_httpx.calls == [
        {"url": service_client.SERVICE_URL, "json": payload}
    ]


async def test_raises_on_http_error(fake_httpx):
    fake_httpx.status_code = 503

    with pytest.raises(httpx.HTTPStatusError):
        await service_client.send_cheating_event({"username": "alice"})
