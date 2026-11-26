"""SSRF Protection and URL Validation Service.

Enforces strict URL format checks, DNS resolution validation (IPv4 & IPv6),
private/loopback/cloud-metadata/tunneling blocking, and hop-by-hop redirect inspection.
"""
from __future__ import annotations
import ipaddress
import logging
import re
import socket
from urllib.parse import urlparse, ParseResult
from typing import Tuple, List

logger = logging.getLogger("easyfineprint.url_guard")

# Specific cloud metadata endpoints & domains to explicitly block
BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.internal",
    "metadata.azure.internal",
    "instance-data",
    "localhost",
    "localhost.localdomain",
    "0.0.0.0",
    "::",
}

BLOCKED_SUFFIXES = (
    ".internal",
    ".local",
    ".localhost",
    ".home.arpa",
)

CARRIER_GRADE_NAT = ipaddress.ip_network("100.64.0.0/10")
ALLOWED_PORTS = {80, 443}
_RE_CTRL_OR_NULL = re.compile(r"[\x00-\x1f\x7f]")


class URLValidationError(Exception):
    """Raised when a URL fails security or format validation."""
    pass


def is_ip_allowed(ip_str: str) -> Tuple[bool, str]:
    """
    Check if an IP address string is safe to connect to (public, non-internal, non-cloud-metadata).
    Returns (is_allowed, reason_if_blocked).
    """
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return False, f"Invalid IP address format: {ip_str}"

    # Cloud metadata checks (IPv4 & IPv6)
    if str(ip) == "169.254.169.254":
        return False, f"Cloud metadata IP blocked ({ip_str})"
    if isinstance(ip, ipaddress.IPv6Address) and str(ip).startswith("fd00:ec2::"):
        return False, f"Cloud metadata IPv6 blocked ({ip_str})"

    if ip.is_loopback:
        return False, f"Loopback address blocked ({ip_str})"
    if ip.is_link_local:
        return False, f"Link-local address blocked ({ip_str})"
    if ip.is_private:
        return False, f"Private network address blocked ({ip_str})"
    if ip.is_multicast:
        return False, f"Multicast address blocked ({ip_str})"
    if ip.is_reserved:
        return False, f"Reserved address blocked ({ip_str})"
    if ip.is_unspecified:
        return False, f"Unspecified address blocked ({ip_str})"

    # IPv4 specific checks
    if isinstance(ip, ipaddress.IPv4Address):
        if ip in CARRIER_GRADE_NAT:
            return False, f"Carrier-grade NAT address blocked ({ip_str})"

    # IPv6 specific checks (mapped, site-local, 6to4, Teredo tunneling bypasses)
    if isinstance(ip, ipaddress.IPv6Address):
        if ip.is_site_local:
            return False, f"IPv6 site-local address blocked ({ip_str})"
        if ip.ipv4_mapped:
            return is_ip_allowed(str(ip.ipv4_mapped))
        if ip.sixtofour:
            return is_ip_allowed(str(ip.sixtofour))
        if ip.teredo:
            server_ip, client_ip = ip.teredo
            ok_srv, reason_srv = is_ip_allowed(str(server_ip))
            if not ok_srv:
                return False, reason_srv
            return is_ip_allowed(str(client_ip))

    return True, "OK"


def validate_url(url_str: str) -> ParseResult:
    """
    Perform structural and literal-IP validation on URL.
    Returns parsed URL on success, raises URLValidationError on violation.
    """
    if not url_str or not isinstance(url_str, str):
        raise URLValidationError("URL cannot be empty")

    if _RE_CTRL_OR_NULL.search(url_str):
        raise URLValidationError("URL contains prohibited control characters.")

    url_str = url_str.strip()
    if len(url_str) > 2048:
        raise URLValidationError("URL exceeds maximum permitted length of 2048 characters.")

    if any(ch.isspace() for ch in url_str):
        raise URLValidationError("URL must not contain whitespace.")

    try:
        parsed = urlparse(url_str)
    except Exception as exc:
        raise URLValidationError(f"Malformed URL: {exc}")

    # Scheme check: ONLY http or https
    if parsed.scheme.lower() not in ("http", "https"):
        raise URLValidationError(f"Invalid scheme '{parsed.scheme}'. Only http and https are permitted.")

    # Reject credentials (user:pass@host)
    if parsed.username or parsed.password:
        raise URLValidationError("Embedded credentials in URL are prohibited.")

    raw_hostname = parsed.hostname
    if not raw_hostname:
        raise URLValidationError("Missing hostname in URL.")

    hostname = raw_hostname.lower().rstrip(".")
    if not hostname:
        raise URLValidationError("Missing hostname in URL.")

    # Check hostname against blacklisted names and suffixes
    if hostname in BLOCKED_HOSTNAMES or hostname.endswith(BLOCKED_SUFFIXES):
        raise URLValidationError(f"Access to hostname '{hostname}' is blocked.")

    # Port check
    port = parsed.port
    if port is not None and port not in ALLOWED_PORTS:
        raise URLValidationError(f"Non-standard port '{port}' is prohibited.")

    # Literal IP check (defends even when caller only performs structural validation)
    try:
        ipaddress.ip_address(hostname)
        allowed, reason = is_ip_allowed(hostname)
        if not allowed:
            raise URLValidationError(f"Target IP {hostname} is forbidden: {reason}")
    except ValueError:
        pass

    return parsed


def resolve_and_verify_hostname(hostname: str) -> List[str]:
    """
    Resolve DNS for both IPv4 and IPv6 and verify that none of the resolved IPs are internal.
    Returns list of verified IP addresses. Raises URLValidationError if resolution fails or any IP is blocked.
    """
    if not hostname:
        raise URLValidationError("Missing hostname.")

    clean_host = hostname.strip().lower().rstrip(".")
    if not clean_host:
        raise URLValidationError("Missing hostname.")

    if clean_host in BLOCKED_HOSTNAMES or clean_host.endswith(BLOCKED_SUFFIXES):
        raise URLValidationError(f"Access to hostname '{clean_host}' is blocked.")

    # If hostname is already a literal IP address
    try:
        ipaddress.ip_address(clean_host)
        allowed, reason = is_ip_allowed(clean_host)
        if not allowed:
            raise URLValidationError(f"Target IP {clean_host} is forbidden: {reason}")
        return [clean_host]
    except ValueError:
        pass  # Hostname is a domain name

    try:
        addr_info = socket.getaddrinfo(clean_host, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except (OSError, UnicodeError) as exc:
        if not isinstance(exc, socket.gaierror):
            logger.warning("DNS resolution failed for '%s': %s", clean_host, exc)
        raise URLValidationError(
            f"Unable to resolve domain '{clean_host}'. Please check that the URL is spelled correctly and the website is publicly reachable."
        ) from exc

    resolved_ips: List[str] = []
    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        if ip_str not in resolved_ips:
            resolved_ips.append(ip_str)

    if not resolved_ips:
        raise URLValidationError(f"No IP addresses resolved for hostname {clean_host}")

    for ip_str in resolved_ips:
        allowed, reason = is_ip_allowed(ip_str)
        if not allowed:
            raise URLValidationError(f"Resolved IP {ip_str} for host {clean_host} is forbidden: {reason}")

    return resolved_ips
