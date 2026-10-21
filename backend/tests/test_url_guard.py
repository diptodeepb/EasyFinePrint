"""Tests for SSRF prevention, URL validation, and IP range blocking."""
import pytest
from app.services.url_guard import (
    validate_url,
    is_ip_allowed,
    resolve_and_verify_hostname,
    URLValidationError,
)


def test_allowed_public_urls():
    url = "https://example.com/terms"
    parsed = validate_url(url)
    assert parsed.scheme == "https"
    assert parsed.hostname == "example.com"


def test_reject_credentials_in_url():
    with pytest.raises(URLValidationError, match="credentials"):
        validate_url("https://admin:secret@example.com/privacy")


def test_reject_invalid_schemes():
    for bad_url in [
        "file:///etc/passwd",
        "data:text/html,hello",
        "ftp://example.com/terms",
        "gopher://example.com",
    ]:
        with pytest.raises(URLValidationError, match="Invalid scheme"):
            validate_url(bad_url)


def test_reject_blocked_hostnames():
    for host in ["localhost", "metadata.google.internal", "instance-data", "corp.internal", "node.local"]:
        with pytest.raises(URLValidationError, match="Access to hostname"):
            validate_url(f"http://{host}/terms")


def test_reject_unsupported_ports():
    with pytest.raises(URLValidationError, match="Non-standard port"):
        validate_url("http://example.com:22/terms")
    with pytest.raises(URLValidationError, match="Non-standard port"):
        validate_url("http://example.com:3306/terms")


def test_ip_guard_loopback():
    for ip in ["127.0.0.1", "127.0.1.1", "127.255.255.255", "::1"]:
        allowed, reason = is_ip_allowed(ip)
        assert not allowed
        assert "Loopback" in reason


def test_ip_guard_private_rfc1918():
    for ip in ["10.0.0.1", "172.16.0.5", "172.31.255.254", "192.168.1.1", "fc00::1"]:
        allowed, reason = is_ip_allowed(ip)
        assert not allowed
        assert "Private" in reason


def test_ip_guard_cloud_metadata():
    for ip in ["169.254.169.254", "fd00:ec2::254"]:
        allowed, reason = is_ip_allowed(ip)
        assert not allowed
        assert "metadata" in reason.lower() or "link-local" in reason.lower()


def test_ip_guard_public_ips():
    for ip in ["8.8.8.8", "1.1.1.1", "93.184.216.34", "2606:4700:4700::1111"]:
        allowed, _ = is_ip_allowed(ip)
        assert allowed
