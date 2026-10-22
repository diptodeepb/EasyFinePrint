"""Company Legal Policy Discovery Service.

Discovers official Terms of Service, Privacy Policy, and User Agreement URLs for
companies and web services using a combination of an authoritative directory
and live heuristic HTML discovery. Zero external search dependencies.
"""
from __future__ import annotations
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import httpx
from app.services.url_guard import validate_url, resolve_and_verify_hostname, URLValidationError

logger = logging.getLogger("easyfineprint.discovery")

# In-memory query cache: normalized_query -> (candidates, timestamp)
_query_cache: Dict[str, tuple[List[Dict[str, Any]], datetime]] = {}

# Authoritative directory of known top web platforms and enterprise services
KNOWN_DIRECTORY: Dict[str, List[Dict[str, str]]] = {
    "discord": [
        {"title": "Discord Terms of Service", "url": "https://discord.com/terms", "snippet": "Official Terms of Service governing user accounts, conduct, and safety on Discord."},
        {"title": "Discord Privacy Policy", "url": "https://discord.com/privacy", "snippet": "Explains data collection, communication privacy, and third-party integrations."},
    ],
    "spotify": [
        {"title": "Spotify Terms and Conditions of Use", "url": "https://www.spotify.com/legal/end-user-agreement/", "snippet": "General terms covering Spotify subscriptions, billing, and content licensing."},
        {"title": "Spotify Privacy Policy", "url": "https://www.spotify.com/legal/privacy-policy/", "snippet": "Covers user listening history, behavioral telemetry, and ad targeting."},
    ],
    "github": [
        {"title": "GitHub Terms of Service", "url": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service", "snippet": "Terms governing repository hosting, account quotas, and code copyright."},
        {"title": "GitHub Privacy Statement", "url": "https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement", "snippet": "Details developer telemetry, commit attribution, and data security."},
    ],
    "roblox": [
        {"title": "Roblox Terms of Use", "url": "https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use", "snippet": "Covers Roblox virtual currency, avatar economies, and arbitration clauses."},
        {"title": "Roblox Privacy and Cookie Policy", "url": "https://en.help.roblox.com/hc/en-us/articles/115004630823-Roblox-Privacy-and-Cookie-Policy", "snippet": "Data protection policies specifically concerning minor safety and user accounts."},
    ],
    "reddit": [
        {"title": "Reddit User Agreement", "url": "https://redditinc.com/policies/user-agreement", "snippet": "Terms covering community moderation, content licensing, and account suspension."},
        {"title": "Reddit Privacy Policy", "url": "https://redditinc.com/policies/privacy-policy", "snippet": "Covers personal information, browsing history, and promotional data sharing."},
    ],
    "netflix": [
        {"title": "Netflix Terms of Use", "url": "https://help.netflix.com/legal/termsofuse", "snippet": "Governs streaming access, household sharing, and billing renewal terms."},
        {"title": "Netflix Privacy Statement", "url": "https://help.netflix.com/legal/privacy", "snippet": "Details viewing history collection and streaming recommendations."},
    ],
    "openai": [
        {"title": "OpenAI Terms of Use", "url": "https://openai.com/policies/terms-of-use/", "snippet": "Terms governing ChatGPT access, API utilization, and model training permissions."},
        {"title": "OpenAI Privacy Policy", "url": "https://openai.com/policies/privacy-policy/", "snippet": "Covers conversation retention, fine-tuning opt-outs, and account information."},
    ],
    "google": [
        {"title": "Google Terms of Service", "url": "https://policies.google.com/terms", "snippet": "Universal terms for Google Search, Android, Gmail, Drive, and cloud services."},
        {"title": "Google Privacy Policy", "url": "https://policies.google.com/privacy", "snippet": "Details search indexing, ad profiling, location tracking, and user controls."},
    ],
    "apple": [
        {"title": "Apple Media Services Terms and Conditions", "url": "https://www.apple.com/legal/internet-services/itunes/", "snippet": "Governs the App Store, Apple Music, iCloud, and device subscriptions."},
        {"title": "Apple Privacy Policy", "url": "https://www.apple.com/legal/privacy/", "snippet": "Outlines Apple on-device privacy protections and iCloud storage."},
    ],
    "microsoft": [
        {"title": "Microsoft Services Agreement", "url": "https://www.microsoft.com/en-us/servicesagreement", "snippet": "Terms for Windows, Xbox, Office 365, OneDrive, and Microsoft accounts."},
        {"title": "Microsoft Privacy Statement", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Details enterprise telemetry, consumer data, and telemetry opt-outs."},
    ],
    "amazon": [
        {"title": "Amazon.com Conditions of Use", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GLSBYFE9MGKKQWW4", "snippet": "Terms covering purchases, digital streaming, Prime, and dispute resolution."},
        {"title": "Amazon.com Privacy Notice", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ", "snippet": "Explains purchase history tracking, Alexa voice data, and fulfillment telemetry."},
    ],
    "meta": [
        {"title": "Meta Terms of Service", "url": "https://www.facebook.com/terms.php", "snippet": "Governs Facebook, Messenger, and VR platform services."},
        {"title": "Meta Privacy Policy", "url": "https://www.facebook.com/privacy/policy/", "snippet": "Covers cross-app social graph tracking, Instagram data, and behavioral advertising."},
    ],
    "facebook": [
        {"title": "Facebook Terms of Service", "url": "https://www.facebook.com/terms.php", "snippet": "Governs Facebook account rights, community standards, and data usage."},
        {"title": "Facebook Privacy Policy", "url": "https://www.facebook.com/privacy/policy/", "snippet": "Explains user tracking and promotional partner data sharing."},
    ],
    "instagram": [
        {"title": "Instagram Terms of Use", "url": "https://help.instagram.com/581066165581870", "snippet": "Covers user photos, reels licensing, and intellectual property."},
        {"title": "Instagram Privacy Policy", "url": "https://help.instagram.com/155833707900388", "snippet": "Covers image analysis, follower engagement, and targeted ads."},
    ],
    "twitter": [
        {"title": "X (Twitter) Terms of Service", "url": "https://twitter.com/en/tos", "snippet": "Covers user tweets, API access, subscriptions, and dispute resolution."},
        {"title": "X (Twitter) Privacy Policy", "url": "https://twitter.com/en/privacy", "snippet": "Details public tweet syndication and AI training usage."},
    ],
    "x": [
        {"title": "X (formerly Twitter) Terms of Service", "url": "https://twitter.com/en/tos", "snippet": "Covers user tweets, API access, subscriptions, and dispute resolution."},
        {"title": "X Privacy Policy", "url": "https://twitter.com/en/privacy", "snippet": "Details public tweet syndication and AI training usage."},
    ],
    "uber": [
        {"title": "Uber Terms of Use", "url": "https://www.uber.com/legal/en/document/?name=general-terms-of-use", "snippet": "Covers passenger transportation, Uber Eats, and mandatory arbitration."},
        {"title": "Uber Privacy Notice", "url": "https://www.uber.com/legal/en/document/?name=privacy-notice", "snippet": "Covers continuous GPS tracking, driver ratings, and route telemetry."},
    ],
    "airbnb": [
        {"title": "Airbnb Terms of Service", "url": "https://www.airbnb.com/help/article/2908", "snippet": "Covers host and guest booking rules, cancellations, and damages."},
        {"title": "Airbnb Privacy Policy", "url": "https://www.airbnb.com/help/article/2855", "snippet": "Explains identity verification, passport collection, and host messaging logs."},
    ],
    "stripe": [
        {"title": "Stripe Services Agreement", "url": "https://stripe.com/legal/consumer", "snippet": "Terms governing payment processing, checkout, and merchant settlements."},
        {"title": "Stripe Privacy Policy", "url": "https://stripe.com/privacy", "snippet": "Covers financial transaction monitoring and fraud detection."},
    ],
    "paypal": [
        {"title": "PayPal User Agreement", "url": "https://www.paypal.com/us/legalhub/useragreement-full", "snippet": "Covers buyer protection, currency exchange fees, and account holds."},
        {"title": "PayPal Privacy Statement", "url": "https://www.paypal.com/us/legalhub/privacy-full", "snippet": "Details credit reporting and financial regulatory compliance sharing."},
    ],
    "twitch": [
        {"title": "Twitch Terms of Service", "url": "https://www.twitch.tv/p/en/legal/terms-of-service/", "snippet": "Governs live broadcasting, subscriptions, bits, and chat moderation."},
        {"title": "Twitch Privacy Notice", "url": "https://www.twitch.tv/p/en/legal/privacy-notice/", "snippet": "Details stream viewership metrics and chat analytics."},
    ],
    "tiktok": [
        {"title": "TikTok Terms of Service", "url": "https://www.tiktok.com/legal/page/row/terms-of-service/en", "snippet": "Covers video sharing, viral sound licenses, and content moderation."},
        {"title": "TikTok Privacy Policy", "url": "https://www.tiktok.com/legal/page/row/privacy-policy/en", "snippet": "Covers device fingerprinting, biometric telemetry, and ad tracking."},
    ],
    "linkedin": [
        {"title": "LinkedIn User Agreement", "url": "https://www.linkedin.com/legal/user-agreement", "snippet": "Governs professional networking, recruiter tools, and profile data."},
        {"title": "LinkedIn Privacy Policy", "url": "https://www.linkedin.com/legal/privacy-policy", "snippet": "Details career telemetry, recruiter searches, and workplace insights."},
    ],
    "steam": [
        {"title": "Steam Subscriber Agreement", "url": "https://store.steampowered.com/subscriber_agreement/", "snippet": "Governs game purchases, digital wallet balances, and software licenses."},
        {"title": "Valve Privacy Policy Agreement", "url": "https://store.steampowered.com/privacy_agreement/", "snippet": "Details gameplay statistics, multiplayer telemetry, and purchase logs."},
    ],
    "valve": [
        {"title": "Valve / Steam Subscriber Agreement", "url": "https://store.steampowered.com/subscriber_agreement/", "snippet": "Governs game purchases, digital wallet balances, and software licenses."},
        {"title": "Valve Privacy Policy", "url": "https://store.steampowered.com/privacy_agreement/", "snippet": "Details gameplay statistics, multiplayer telemetry, and purchase logs."},
    ],
    "slack": [
        {"title": "Slack Terms of Service", "url": "https://slack.com/terms-of-service", "snippet": "Terms governing workspace administration, customer data, and integrations."},
        {"title": "Slack Privacy Policy", "url": "https://slack.com/privacy-policy", "snippet": "Explains team chat retention, message exports, and workspace analytics."},
    ],
    "zoom": [
        {"title": "Zoom Terms of Service", "url": "https://explore.zoom.us/en/terms/", "snippet": "Governs video conferencing, cloud recording, and meeting encryption."},
        {"title": "Zoom Privacy Statement", "url": "https://explore.zoom.us/en/privacy/", "snippet": "Covers meeting audio/video metadata and AI meeting summaries."},
    ],
    "dropbox": [
        {"title": "Dropbox Terms of Service", "url": "https://www.dropbox.com/terms", "snippet": "Covers cloud file syncing, storage quotas, and shared folder access."},
        {"title": "Dropbox Privacy Policy", "url": "https://www.dropbox.com/privacy", "snippet": "Explains file metadata, file versioning retention, and third-party links."},
    ],
    "notion": [
        {"title": "Notion Terms and Conditions", "url": "https://www.notion.so/Terms-and-Privacy-28fc8652d37f487381ade7a256950346", "snippet": "Governs collaborative documentation, Notion AI, and enterprise workspaces."},
        {"title": "Notion Privacy Policy", "url": "https://www.notion.so/Privacy-Policy-3468d120cf614d4c9014c09f6adc9091", "snippet": "Covers workspace content confidentiality and analytics."},
    ],
    "figma": [
        {"title": "Figma Terms of Service", "url": "https://www.figma.com/summary-of-terms/", "snippet": "Terms covering collaborative design files, team libraries, and plugin hosting."},
        {"title": "Figma Privacy Policy", "url": "https://www.figma.com/privacy/", "snippet": "Details design canvas telemetry and user accounts."},
    ],
    "anthropic": [
        {"title": "Anthropic Consumer Terms of Service", "url": "https://www.anthropic.com/legal/consumer-terms", "snippet": "Governs Claude web service, subscription features, and acceptable use."},
        {"title": "Anthropic Privacy Policy", "url": "https://www.anthropic.com/legal/privacy", "snippet": "Covers prompt data handling and research training opt-outs."},
    ],
    "vercel": [
        {"title": "Vercel Terms of Service", "url": "https://vercel.com/legal/terms", "snippet": "Covers frontend cloud deployments, edge functions, and hosting bandwidth."},
        {"title": "Vercel Privacy Policy", "url": "https://vercel.com/legal/privacy-policy", "snippet": "Details deployment telemetry, analytics, and visitor logs."},
    ],
    "cloudflare": [
        {"title": "Cloudflare Self-Serve Subscription Agreement", "url": "https://www.cloudflare.com/terms/", "snippet": "Terms covering CDN caching, Workers AI, DNS services, and edge computing."},
        {"title": "Cloudflare Privacy Policy", "url": "https://www.cloudflare.com/privacypolicy/", "snippet": "Covers DNS query telemetry, edge proxy logs, and security mitigations."},
    ],
}


async def crawl_homepage_for_policy_links(base_url: str) -> List[Dict[str, str]]:
    """
    Safely probes a company homepage and extracts candidate Terms and Privacy links from the DOM.
    Enforces SSRF validation before attempting connection.
    """
    try:
        parsed = validate_url(base_url)
        resolve_and_verify_hostname(parsed.hostname)
    except URLValidationError as exc:
        logger.debug("Discovery URL validation rejected %s: %s", base_url, exc)
        return []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    candidates: List[Dict[str, str]] = []
    seen_urls: set[str] = set()

    try:
        async with httpx.AsyncClient(timeout=5.0, follow_redirects=True, verify=True) as client:
            resp = await client.get(base_url, headers=headers)
            if resp.status_code != 200 or not resp.text:
                return []

            soup = BeautifulSoup(resp.text[:500000], "html.parser")
            target_keywords = ["terms", "privacy", "legal", "tos", "policy", "agreement", "disclaimer", "condition"]

            # Prefer links in footer or nav containers first
            all_links = []
            for container in soup.find_all(["footer", "nav", "div"]):
                all_links.extend(container.find_all("a", href=True))
            if not all_links:
                all_links = soup.find_all("a", href=True)

            for a in all_links:
                href = a["href"].strip()
                if not href or href.startswith(("#", "javascript:", "mailto:", "tel:")):
                    continue

                text = a.get_text(separator=" ", strip=True)
                combined = f"{text} {href}".lower()

                if any(kw in combined for kw in target_keywords):
                    full_url = urljoin(str(resp.url), href)
                    if full_url.startswith(("http://", "https://")) and full_url not in seen_urls:
                        # Validate full URL against SSRF
                        try:
                            p_target = validate_url(full_url)
                            resolve_and_verify_hostname(p_target.hostname)
                        except URLValidationError:
                            continue

                        seen_urls.add(full_url)
                        clean_title = text if (text and len(text) > 3) else "Legal Document"
                        snippet = f"Discovered directly on official website ({parsed.hostname})"
                        candidates.append({
                            "title": clean_title,
                            "url": full_url,
                            "snippet": snippet,
                            "source": "discovery",
                        })

                        if len(candidates) >= 6:
                            break

    except Exception as exc:
        logger.debug("Crawl discovery exception for %s: %s", base_url, exc)

    return candidates


async def discover_policy_urls(query: str) -> Dict[str, Any]:
    """
    Discover candidate official Terms of Service and Privacy Policy URLs for a company.
    1. Checks in-memory cache.
    2. Checks authoritative known directory.
    3. Crawls live homepage and extracts footer legal links dynamically if not found.
    """
    clean_q = query.strip().lower()
    if not clean_q:
        return {"candidates": [], "cached": False}

    # 1. Check in-memory cache
    if clean_q in _query_cache:
        cached_candidates, _ = _query_cache[clean_q]
        return {"candidates": cached_candidates, "cached": True}

    candidates: List[Dict[str, str]] = []

    # 2. Check authoritative known directory
    # Direct match or substring match (e.g. "spotify web" -> matches "spotify")
    matched_key = None
    if clean_q in KNOWN_DIRECTORY:
        matched_key = clean_q
    else:
        for k in KNOWN_DIRECTORY:
            if k in clean_q or clean_q in k:
                matched_key = k
                break

    if matched_key:
        for item in KNOWN_DIRECTORY[matched_key]:
            candidates.append({
                "title": item["title"],
                "url": item["url"],
                "snippet": item.get("snippet", ""),
                "source": "discovery",
            })

    # 3. Dynamic discovery if not enough candidates found
    if len(candidates) < 2:
        # Determine candidate base URLs to probe
        probe_urls = []
        if "." in clean_q and not clean_q.startswith("http"):
            probe_urls.append(f"https://{clean_q}")
        elif clean_q.startswith(("http://", "https://")):
            probe_urls.append(clean_q)
        else:
            clean_domain = re.sub(r"[^a-z0-9\-]", "", clean_q)
            if clean_domain:
                probe_urls.extend([
                    f"https://www.{clean_domain}.com",
                    f"https://{clean_domain}.com",
                ])

        for target in probe_urls:
            discovered = await crawl_homepage_for_policy_links(target)
            for d in discovered:
                if not any(c["url"] == d["url"] for c in candidates):
                    candidates.append(d)
            if len(candidates) >= 3:
                break

    # Cache result
    _query_cache[clean_q] = (candidates, datetime.now(timezone.utc))

    return {
        "candidates": candidates[:6],
        "cached": False,
    }
