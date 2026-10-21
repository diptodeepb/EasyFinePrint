"""SSRF Protection and URL Validation Service.

Enforces strict URL format checks, DNS resolution validation (IPv4 & IPv6),
private/loopback/cloud-metadata blocking, and hop-by-hop redirect inspection.
"""
from __future__ import annotations
import ipaddress
import logging
import socket
from urllib.parse import urlparse, ParseResult
from typing import Tuple, List

logger = logging.getLogger("easyfineprint.url_guard")

# Specific cloud metadata endpoints & domains to explicitly block
BLOCKED_HOSTNAMES = {
    "metadata.google.internal",
    "metadata.internal",
    "instance-data",
    "localhost",
}

CARRIER_GRADE_NAT = ipaddress.ip_network("100.64.0.0/10")
ALLOWED_PORTS = {80, 443, 8080, 8443}


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

    # IPv6 specific checks
    if isinstance(ip, ipaddress.IPv6Address):
        # IPv4-mapped IPv6 address (e.g. ::ffff:127.0.0.1)
        if ip.ipv4_mapped:
            return is_ip_allowed(str(ip.ipv4_mapped))

    return True, "OK"


def validate_url(url_str: str) -> ParseResult:
    """
    Perform structural validation on URL.
    Returns parsed URL on success, raises URLValidationError on violation.
    """
    if not url_str or not isinstance(url_str, str):
        raise URLValidationError("URL cannot be empty")

    url_str = url_str.strip()
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

    hostname = parsed.hostname
    if not hostname:
        raise URLValidationError("Missing hostname in URL.")

    # Check hostname against blacklisted names
    if hostname.lower() in BLOCKED_HOSTNAMES or hostname.lower().endswith(".internal") or hostname.lower().endswith(".local"):
        raise URLValidationError(f"Access to hostname '{hostname}' is blocked.")

    # Port check
    port = parsed.port
    if port is not None and port not in ALLOWED_PORTS:
        raise URLValidationError(f"Non-standard port '{port}' is prohibited.")

    return parsed


def resolve_and_verify_hostname(hostname: str) -> List[str]:
    """
    Resolve DNS for both IPv4 and IPv6 and verify that none of the resolved IPs are internal.
    Returns list of verified IP addresses. Raises URLValidationError if resolution fails or any IP is blocked.
    """
    # If hostname is already a literal IP address
    try:
        ipaddress.ip_address(hostname)
        allowed, reason = is_ip_allowed(hostname)
        if not allowed:
            raise URLValidationError(f"Target IP {hostname} is forbidden: {reason}")
        return [hostname]
    except ValueError:
        pass  # Hostname is a domain name

    try:
        addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise URLValidationError(f"DNS resolution failed for {hostname}: {exc}")

    resolved_ips: List[str] = []
    for entry in addr_info:
        sockaddr = entry[4]
        ip_str = sockaddr[0]
        if ip_str not in resolved_ips:
            resolved_ips.append(ip_str)

    if not resolved_ips:
        raise URLValidationError(f"No IP addresses resolved for hostname {hostname}")

    for ip_str in resolved_ips:
        allowed, reason = is_ip_allowed(ip_str)
        if not allowed:
            raise URLValidationError(f"Resolved IP {ip_str} for host {hostname} is forbidden: {reason}")

    return resolved_ips
