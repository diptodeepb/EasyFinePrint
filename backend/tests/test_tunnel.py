"""Unit tests for Sentry envelope tunneling endpoint (/api/tunnel)."""
import json
import pytest
from unittest.mock import AsyncMock, patch
from httpx import ASGITransport, AsyncClient
from fastapi import Response
from app.main import app


@pytest.mark.asyncio
async def test_tunnel_empty_body():
    """Empty body should return 200 OK without errors."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/tunnel", content=b"")
        assert resp.status_code == 200
        assert resp.text == "OK"


@pytest.mark.asyncio
async def test_tunnel_no_dsn():
    """Envelope with missing DSN should return 200 OK gracefully."""
    header = json.dumps({"event_id": "1234567890abcdef"}).encode("utf-8")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/tunnel", content=header + b"\n{}")
        assert resp.status_code == 200
        assert resp.text == "OK"


@pytest.mark.asyncio
async def test_tunnel_reject_invalid_host():
    """Envelope with untrusted host should be rejected with 403 Forbidden."""
    header = json.dumps({"dsn": "https://pubkey@evil.com/12345"}).encode("utf-8")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/tunnel", content=header + b"\n{}")
        assert resp.status_code == 403
        assert "Invalid target host" in resp.text


@pytest.mark.asyncio
async def test_tunnel_reject_spoofed_subdomain():
    """Envelope targeting a domain ending with sentry.io but not a valid subdomain must be rejected."""
    header = json.dumps({"dsn": "https://pubkey@evilsentry.io/12345"}).encode("utf-8")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        resp = await ac.post("/api/tunnel", content=header + b"\n{}")
        assert resp.status_code == 403
        assert "Invalid target host" in resp.text


@pytest.mark.asyncio
async def test_tunnel_valid_sentry_forwarding():
    """Valid Sentry envelope should proxy to authentic ingest endpoint."""
    header = json.dumps({"dsn": "https://pubkey@o123456.ingest.sentry.io/789012"}).encode("utf-8")
    payload = header + b"\n" + b'{"type":"event"}\n{"message":"Test error"}'

    mock_resp = Response(status_code=200, content=b'{"id":"12345"}')

    with patch("app.main.forward_envelope_to_sentry", new_callable=AsyncMock) as mock_forward:
        mock_forward.return_value = mock_resp
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/tunnel", content=payload)
            assert resp.status_code == 200
            assert resp.content == b'{"id":"12345"}'

            mock_forward.assert_called_once()
            call_url = mock_forward.call_args[0][0]
            assert call_url == "https://o123456.ingest.sentry.io/api/789012/envelope/"


@pytest.mark.asyncio
async def test_tunnel_resilience_on_upstream_exception():
    """When upstream Sentry connection fails, the tunnel handles it gracefully with 200 OK."""
    header = json.dumps({"dsn": "https://pubkey@o123456.ingest.sentry.io/789012"}).encode("utf-8")
    payload = header + b"\n" + b'{"type":"event"}\n{}'

    with patch("app.main.forward_envelope_to_sentry", side_effect=Exception("Connection refused")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            resp = await ac.post("/api/tunnel", content=payload)
            assert resp.status_code == 200
            assert resp.text == "OK"
