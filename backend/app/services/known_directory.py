"""Authoritative Known Legal Policy Directory.

Curated and verified repository of official Terms of Service, Privacy Policies,
and User Agreements for the world's most widely used web platforms, SaaS products,
cloud infrastructure services, fintechs, developer tools, and consumer applications.
"""
from __future__ import annotations
import re
from typing import Dict, List, Optional

# Authoritative directory mapping canonical slug -> list of verified legal documents
KNOWN_DIRECTORY: Dict[str, List[Dict[str, str]]] = {
    # ---------------------------------------------------------
    # 1. Tech Giants & Universal Platforms
    # ---------------------------------------------------------
    "google": [
        {"title": "Google Terms of Service", "url": "https://policies.google.com/terms", "snippet": "Universal terms for Google Search, Android, Gmail, Drive, Docs, and ecosystem services."},
        {"title": "Google Privacy Policy", "url": "https://policies.google.com/privacy", "snippet": "Details data collection, search profiling, ad personalization, and user telemetry controls."},
        {"title": "Google Workspace Terms of Service", "url": "https://workspace.google.com/terms/premier_terms/", "snippet": "Enterprise agreement covering Google Workspace, Gmail for business, and admin controls."},
    ],
    "youtube": [
        {"title": "YouTube Terms of Service", "url": "https://www.youtube.com/t/terms", "snippet": "Governs video uploads, channel monetization, copyright strikes, and content licensing."},
        {"title": "YouTube Privacy Guidelines", "url": "https://www.youtube.com/howyoutubeworks/user-settings/privacy/", "snippet": "Details viewing history telemetry, recommendation algorithms, and child safety."},
    ],
    "apple": [
        {"title": "Apple Media Services Terms and Conditions", "url": "https://www.apple.com/legal/internet-services/itunes/", "snippet": "Governs App Store, Apple Music, Apple TV+, iCloud, and hardware services."},
        {"title": "Apple Privacy Policy", "url": "https://www.apple.com/legal/privacy/", "snippet": "Outlines Apple on-device differential privacy protections, iCloud encryption, and device analytics."},
    ],
    "microsoft": [
        {"title": "Microsoft Services Agreement", "url": "https://www.microsoft.com/en-us/servicesagreement", "snippet": "Terms for Windows, Xbox Live, Office 365, OneDrive, Bing, and consumer accounts."},
        {"title": "Microsoft Privacy Statement", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Covers diagnostic telemetry, enterprise customer data, and telemetry opt-outs."},
    ],
    "amazon": [
        {"title": "Amazon.com Conditions of Use", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GLSBYFE9MGKKQWW4", "snippet": "Terms covering purchases, digital streaming, Prime memberships, and dispute resolution."},
        {"title": "Amazon.com Privacy Notice", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=GX7NJQ4ZB8MHFRNJ", "snippet": "Explains purchase history tracking, Alexa voice data retention, and fulfillment telemetry."},
        {"title": "AWS Customer Agreement", "url": "https://aws.amazon.com/agreement/", "snippet": "Governs Amazon Web Services cloud infrastructure, compute instances, and SLAs."},
    ],
    "meta": [
        {"title": "Meta Terms of Service", "url": "https://www.facebook.com/terms.php", "snippet": "Governs Facebook, Messenger, and VR platform accounts and acceptable use."},
        {"title": "Meta Privacy Policy", "url": "https://www.facebook.com/privacy/policy/", "snippet": "Covers cross-app social graph tracking, behavioral advertising, and Meta AI processing."},
    ],
    "facebook": [
        {"title": "Facebook Terms of Service", "url": "https://www.facebook.com/terms.php", "snippet": "Governs Facebook account rights, community standards, and data usage."},
        {"title": "Facebook Privacy Policy", "url": "https://www.facebook.com/privacy/policy/", "snippet": "Explains social tracking, ad targeting algorithms, and promotional partner data sharing."},
    ],
    "instagram": [
        {"title": "Instagram Terms of Use", "url": "https://help.instagram.com/581066165581870", "snippet": "Covers user photos, reels licensing, commercial promotion, and intellectual property."},
        {"title": "Instagram Privacy Policy", "url": "https://help.instagram.com/155833707900388", "snippet": "Covers image analysis, follower engagement metrics, and targeted ads."},
    ],
    "threads": [
        {"title": "Threads Supplemental Terms of Use", "url": "https://help.instagram.com/769980938343082", "snippet": "Supplemental terms for Meta Threads decentralized fediverse and microblogging platform."},
        {"title": "Threads Supplemental Privacy Policy", "url": "https://help.instagram.com/515230437301944", "snippet": "Details fediverse public post syndication and Meta cross-service tracking."},
    ],
    "whatsapp": [
        {"title": "WhatsApp Terms of Service", "url": "https://www.whatsapp.com/legal/terms-of-service", "snippet": "Governs end-to-end encrypted messaging, business accounts, and VoIP calling."},
        {"title": "WhatsApp Privacy Policy", "url": "https://www.whatsapp.com/legal/privacy-policy", "snippet": "Explains metadata handling, device information, and Meta infrastructure sharing."},
    ],
    "twitter": [
        {"title": "X (Twitter) Terms of Service", "url": "https://twitter.com/en/tos", "snippet": "Covers user tweets, API access, subscriptions, and mandatory dispute arbitration."},
        {"title": "X (Twitter) Privacy Policy", "url": "https://twitter.com/en/privacy", "snippet": "Details public post syndication, biometric data, and AI training permissions."},
    ],
    "x": [
        {"title": "X (formerly Twitter) Terms of Service", "url": "https://twitter.com/en/tos", "snippet": "Covers user posts, Premium subscriptions, creator payouts, and Grok AI usage."},
        {"title": "X Privacy Policy", "url": "https://twitter.com/en/privacy", "snippet": "Details public tweet syndication, behavioral telemetry, and third-party data sharing."},
    ],
    "linkedin": [
        {"title": "LinkedIn User Agreement", "url": "https://www.linkedin.com/legal/user-agreement", "snippet": "Governs professional networking, recruiter tools, InMail, and profile data."},
        {"title": "LinkedIn Privacy Policy", "url": "https://www.linkedin.com/legal/privacy-policy", "snippet": "Details career telemetry, recruiter searches, workplace insights, and AI training."},
    ],
    "tiktok": [
        {"title": "TikTok Terms of Service", "url": "https://www.tiktok.com/legal/page/row/terms-of-service/en", "snippet": "Covers short-form video sharing, viral sound licenses, and content moderation rules."},
        {"title": "TikTok Privacy Policy", "url": "https://www.tiktok.com/legal/page/row/privacy-policy/en", "snippet": "Covers device fingerprinting, biometric face telemetry, clipboard access, and ad tracking."},
    ],
    "reddit": [
        {"title": "Reddit User Agreement", "url": "https://redditinc.com/policies/user-agreement", "snippet": "Terms covering community moderation, content licensing, and account suspension."},
        {"title": "Reddit Privacy Policy", "url": "https://redditinc.com/policies/privacy-policy", "snippet": "Covers personal information, browsing history, and promotional data sharing."},
    ],
    "discord": [
        {"title": "Discord Terms of Service", "url": "https://discord.com/terms", "snippet": "Official Terms of Service governing user accounts, conduct, and safety on Discord."},
        {"title": "Discord Privacy Policy", "url": "https://discord.com/privacy", "snippet": "Explains data collection, communication privacy, and third-party integrations."},
    ],
    "snapchat": [
        {"title": "Snap Inc. Terms of Service", "url": "https://values.snap.com/legal/terms-of-service", "snippet": "Governs Snapchat ephemeral messaging, Spotlight, Spectacles, and Bitmoji."},
        {"title": "Snap Inc. Privacy Policy", "url": "https://values.snap.com/privacy/privacy-policy", "snippet": "Covers Snap Map location tracking, facial lens recognition, and ephemeral retention."},
    ],
    "pinterest": [
        {"title": "Pinterest Terms of Service", "url": "https://policy.pinterest.com/en/terms-of-service", "snippet": "Governs board curation, visual bookmarking, and merchant product pins."},
        {"title": "Pinterest Privacy Policy", "url": "https://policy.pinterest.com/en/privacy-policy", "snippet": "Details visual search tracking, shopping history, and targeted recommendations."},
    ],
    "tumblr": [
        {"title": "Tumblr Terms of Service", "url": "https://www.tumblr.com/policy/en/terms-of-service", "snippet": "Governs blogging, reblogs, community guidelines, and Automattic account rights."},
        {"title": "Tumblr Privacy Policy", "url": "https://automattic.com/privacy/", "snippet": "Covers blog analytics, visitor telemetry, and Automattic network tracking."},
    ],
    "telegram": [
        {"title": "Telegram Terms of Service", "url": "https://telegram.org/tos", "snippet": "Governs channel broadcasting, bot development, and account termination policies."},
        {"title": "Telegram Privacy Policy", "url": "https://telegram.org/privacy", "snippet": "Details cloud chat retention, secret chat encryption, and phone number processing."},
    ],
    "signal": [
        {"title": "Signal Terms of Service & Privacy Policy", "url": "https://signal.org/legal/", "snippet": "Non-profit zero-knowledge privacy policy and minimal metadata retention terms."},
    ],
    "bluesky": [
        {"title": "Bluesky Terms of Service", "url": "https://bsky.social/about/support/tos", "snippet": "Governs AT Protocol federated social networking and user-owned identity."},
        {"title": "Bluesky Privacy Policy", "url": "https://bsky.social/about/support/privacy-policy", "snippet": "Covers public data syndication across decentralized relays and account records."},
    ],

    # ---------------------------------------------------------
    # 2. AI Platforms & Machine Learning Services
    # ---------------------------------------------------------
    "openai": [
        {"title": "OpenAI Terms of Use", "url": "https://openai.com/policies/terms-of-use/", "snippet": "Terms governing ChatGPT access, API utilization, and model output ownership."},
        {"title": "OpenAI Privacy Policy", "url": "https://openai.com/policies/privacy-policy/", "snippet": "Covers conversation retention, training opt-outs, and account information."},
        {"title": "OpenAI Business Terms", "url": "https://openai.com/policies/business-terms/", "snippet": "Enterprise terms regarding API data confidentiality and zero-retention policies."},
    ],
    "anthropic": [
        {"title": "Anthropic Consumer Terms of Service", "url": "https://www.anthropic.com/legal/consumer-terms", "snippet": "Governs Claude web service, subscription tiers, and acceptable use."},
        {"title": "Anthropic Privacy Policy", "url": "https://www.anthropic.com/legal/privacy", "snippet": "Covers prompt data handling and research training opt-outs."},
        {"title": "Anthropic Commercial Terms of Service", "url": "https://www.anthropic.com/legal/commercial-terms", "snippet": "Enterprise API terms guaranteeing no customer prompt training on Claude models."},
    ],
    "perplexity": [
        {"title": "Perplexity AI Terms of Service", "url": "https://www.perplexity.ai/hub/legal/terms-of-service", "snippet": "Governs conversational search, citations, and Pro subscription services."},
        {"title": "Perplexity AI Privacy Policy", "url": "https://www.perplexity.ai/hub/legal/privacy-policy", "snippet": "Details search query telemetry, source indexing, and personal data storage."},
    ],
    "mistral": [
        {"title": "Mistral AI Terms of Service", "url": "https://mistral.ai/terms/", "snippet": "Terms governing Le Chat, Mistral API, and open weight model usage."},
        {"title": "Mistral AI Privacy Policy", "url": "https://mistral.ai/privacy-policy/", "snippet": "Covers European data protection, GDPR compliance, and telemetry retention."},
    ],
    "cohere": [
        {"title": "Cohere Terms of Use", "url": "https://cohere.com/terms-of-use", "snippet": "Enterprise terms governing Cohere Command, Embed, and Rerank foundation models."},
        {"title": "Cohere Privacy Policy", "url": "https://cohere.com/privacy", "snippet": "Details enterprise customer data isolation and compliance certifications."},
    ],
    "huggingface": [
        {"title": "Hugging Face Terms of Service", "url": "https://huggingface.co/terms-of-service", "snippet": "Governs model hub hosting, dataset repositories, Spaces, and inference endpoints."},
        {"title": "Hugging Face Privacy Policy", "url": "https://huggingface.co/privacy", "snippet": "Covers public model repository metrics, API telemetry, and developer accounts."},
    ],
    "midjourney": [
        {"title": "Midjourney Terms of Service", "url": "https://docs.midjourney.com/docs/terms-of-service", "snippet": "Governs generative image synthesis, copyright ownership, and commercial licenses."},
        {"title": "Midjourney Privacy Policy", "url": "https://docs.midjourney.com/docs/privacy-policy", "snippet": "Explains image prompt logging, public gallery indexing, and Discord integration."},
    ],
    "stabilityai": [
        {"title": "Stability AI Terms of Use", "url": "https://stability.ai/terms-of-use", "snippet": "Terms governing Stable Diffusion, API endpoints, and community model licenses."},
        {"title": "Stability AI Privacy Policy", "url": "https://stability.ai/privacy-policy", "snippet": "Details generation logs, website telemetry, and user registration data."},
    ],
    "elevenlabs": [
        {"title": "ElevenLabs Terms of Service", "url": "https://elevenlabs.io/terms", "snippet": "Governs AI voice cloning, speech synthesis, and voice actor royalties."},
        {"title": "ElevenLabs Privacy Policy", "url": "https://elevenlabs.io/privacy", "snippet": "Details audio sample retention, voice biometrics, and API telemetry."},
    ],
    "runway": [
        {"title": "Runway Terms of Use", "url": "https://runwayml.com/terms-of-use/", "snippet": "Governs Gen-2/Gen-3 video generation, media asset storage, and subscriptions."},
        {"title": "Runway Privacy Policy", "url": "https://runwayml.com/privacy-policy/", "snippet": "Covers video asset telemetry, cloud rendering retention, and usage analytics."},
    ],
    "replicate": [
        {"title": "Replicate Terms of Service", "url": "https://replicate.com/terms", "snippet": "Governs serverless machine learning inference, open-source model execution, and billing."},
        {"title": "Replicate Privacy Policy", "url": "https://replicate.com/privacy", "snippet": "Details API request logging, model weights hosting, and user metadata."},
    ],
    "jasper": [
        {"title": "Jasper Terms of Service", "url": "https://www.jasper.ai/terms-of-service", "snippet": "Governs enterprise AI marketing, brand voice fine-tuning, and content creation."},
        {"title": "Jasper Privacy Policy", "url": "https://www.jasper.ai/privacy-policy", "snippet": "Covers organizational content safety, data segregation, and marketing telemetry."},
    ],
    "characterai": [
        {"title": "Character.ai Terms of Service", "url": "https://character.ai/tos", "snippet": "Governs personalized AI chatbot interactions, avatar creations, and acceptable use."},
        {"title": "Character.ai Privacy Policy", "url": "https://character.ai/privacy", "snippet": "Covers chat log retention, user personas, and behavioral personalization."},
    ],
    "cursor": [
        {"title": "Cursor Terms of Service", "url": "https://www.cursor.com/terms-of-service", "snippet": "Governs Anysphere Cursor AI code editor, agentic completions, and subscriptions."},
        {"title": "Cursor Privacy Policy", "url": "https://www.cursor.com/privacy", "snippet": "Details privacy mode, code snippet transmission, and AI indexing opt-outs."},
    ],
    "deepl": [
        {"title": "DeepL Terms and Conditions", "url": "https://www.deepl.com/en/pro-license", "snippet": "Governs DeepL Pro translation, neural machine translation APIs, and confidentiality."},
        {"title": "DeepL Privacy Policy", "url": "https://www.deepl.com/en/privacy", "snippet": "Explains immediate deletion of translated texts for Pro subscribers."},
    ],
    "grammarly": [
        {"title": "Grammarly Terms of Service", "url": "https://www.grammarly.com/terms", "snippet": "Governs automated writing assistance, enterprise extensions, and cloud syncing."},
        {"title": "Grammarly Privacy Policy", "url": "https://www.grammarly.com/privacy-policy", "snippet": "Covers text keystroke processing, enterprise zero-training commitments, and telemetry."},
    ],

    # ---------------------------------------------------------
    # 3. Developer Tools, Cloud & Hosting Infrastructure
    # ---------------------------------------------------------
    "github": [
        {"title": "GitHub Terms of Service", "url": "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service", "snippet": "Terms governing repository hosting, account quotas, and code copyright."},
        {"title": "GitHub Privacy Statement", "url": "https://docs.github.com/en/site-policy/privacy-policies/github-privacy-statement", "snippet": "Details developer telemetry, commit attribution, and data security."},
    ],
    "gitlab": [
        {"title": "GitLab Terms of Use", "url": "https://about.gitlab.com/handbook/legal/terms-of-use/", "snippet": "Governs self-hosted and cloud CI/CD pipelines, DevOps lifecycle, and repository storage."},
        {"title": "GitLab Privacy Statement", "url": "https://about.gitlab.com/handbook/legal/privacy/", "snippet": "Details developer activity telemetry, user account authentication, and security."},
    ],
    "atlassian": [
        {"title": "Atlassian Customer Agreement", "url": "https://www.atlassian.com/legal/customer-agreement", "snippet": "Governs Jira, Confluence, Bitbucket, Trello, and Opsgenie enterprise cloud products."},
        {"title": "Atlassian Privacy Policy", "url": "https://www.atlassian.com/legal/privacy-policy", "snippet": "Covers enterprise collaboration logs, user profiles, and cloud telemetry."},
    ],
    "cloudflare": [
        {"title": "Cloudflare Self-Serve Subscription Agreement", "url": "https://www.cloudflare.com/terms/", "snippet": "Terms covering CDN caching, Workers AI, DNS services, and edge computing."},
        {"title": "Cloudflare Privacy Policy", "url": "https://www.cloudflare.com/privacypolicy/", "snippet": "Covers DNS query telemetry, edge proxy logs, and security mitigations."},
    ],
    "vercel": [
        {"title": "Vercel Terms of Service", "url": "https://vercel.com/legal/terms", "snippet": "Covers frontend cloud deployments, edge functions, and hosting bandwidth."},
        {"title": "Vercel Privacy Policy", "url": "https://vercel.com/legal/privacy-policy", "snippet": "Details deployment telemetry, analytics, and visitor logs."},
    ],
    "netlify": [
        {"title": "Netlify Terms of Use", "url": "https://www.netlify.com/legal/terms-of-use/", "snippet": "Governs composable web builds, serverless functions, form submissions, and edge routing."},
        {"title": "Netlify Privacy Policy", "url": "https://www.netlify.com/privacy/", "snippet": "Details visitor edge logs, developer dashboard metrics, and telemetry."},
    ],
    "supabase": [
        {"title": "Supabase Terms of Service", "url": "https://supabase.com/terms", "snippet": "Governs Postgres database hosting, authentication, storage, and edge functions."},
        {"title": "Supabase Privacy Policy", "url": "https://supabase.com/privacy", "snippet": "Covers developer accounts, database connection logs, and billing telemetry."},
    ],
    "railway": [
        {"title": "Railway Terms of Service", "url": "https://railway.com/legal/terms", "snippet": "Governs containerized infrastructure, ephemeral environments, and persistent volumes."},
        {"title": "Railway Privacy Policy", "url": "https://railway.com/legal/privacy", "snippet": "Details deploy telemetry, build logs, and developer account management."},
    ],
    "render": [
        {"title": "Render Terms of Service", "url": "https://render.com/terms", "snippet": "Governs unified cloud hosting for web apps, databases, cron jobs, and background workers."},
        {"title": "Render Privacy Policy", "url": "https://render.com/privacy", "snippet": "Covers server logs, user telemetry, and infrastructure monitoring metrics."},
    ],
    "flyio": [
        {"title": "Fly.io Terms of Service", "url": "https://fly.io/legal/terms-of-service/", "snippet": "Governs global physical hardware VM deployment, Anycast routing, and LiteFS storage."},
        {"title": "Fly.io Privacy Policy", "url": "https://fly.io/legal/privacy-policy/", "snippet": "Details network packet routing logs, user authentication, and infrastructure metrics."},
    ],
    "digitalocean": [
        {"title": "DigitalOcean Terms of Service", "url": "https://www.digitalocean.com/legal/terms-of-service-agreement", "snippet": "Governs Droplets, Kubernetes, managed databases, and cloud bandwidth quotas."},
        {"title": "DigitalOcean Privacy Policy", "url": "https://www.digitalocean.com/legal/privacy", "snippet": "Details cloud account verification, abuse prevention, and network telemetry."},
    ],
    "heroku": [
        {"title": "Heroku Terms of Service", "url": "https://www.heroku.com/policy/tos", "snippet": "Governs Heroku Dynos, Postgres add-ons, and Salesforce Platform cloud services."},
        {"title": "Salesforce Privacy Statement", "url": "https://www.salesforce.com/company/privacy/", "snippet": "Details enterprise customer telemetry, cloud access audits, and authentication."},
    ],
    "docker": [
        {"title": "Docker Terms of Service", "url": "https://www.docker.com/legal/docker-terms-service/", "snippet": "Governs Docker Desktop, Docker Hub registry, organization seats, and pull rate limits."},
        {"title": "Docker Privacy Policy", "url": "https://www.docker.com/legal/docker-privacy-policy/", "snippet": "Covers container image download analytics, desktop telemetry, and billing."},
    ],
    "postman": [
        {"title": "Postman Terms of Service", "url": "https://www.postman.com/legal/terms/", "snippet": "Governs API client workspaces, mock servers, automated testing monitors, and team collaboration."},
        {"title": "Postman Privacy Policy", "url": "https://www.postman.com/legal/privacy-policy/", "snippet": "Covers API request history synchronization, team member invites, and analytics."},
    ],
    "sentry": [
        {"title": "Sentry Terms of Service", "url": "https://sentry.io/terms/", "snippet": "Governs application performance monitoring, crash telemetry ingestion, and error tracking."},
        {"title": "Sentry Privacy Policy", "url": "https://sentry.io/privacy/", "snippet": "Details scrubbing of PII in stack traces, error telemetry retention, and customer data rights."},
    ],
    "datadog": [
        {"title": "Datadog Terms of Service", "url": "https://www.datadoghq.com/legal/terms/", "snippet": "Governs cloud monitoring, log management, APM tracing, and infrastructure agents."},
        {"title": "Datadog Privacy Policy", "url": "https://www.datadoghq.com/legal/privacy/", "snippet": "Details observability telemetry, server metrics retention, and enterprise compliance."},
    ],
    "newrelic": [
        {"title": "New Relic Terms of Service", "url": "https://newrelic.com/termsandconditions/terms", "snippet": "Governs full-stack observability, synthetic monitoring, and telemetry data platform."},
        {"title": "New Relic Services Privacy Notice", "url": "https://newrelic.com/termsandconditions/services-privacy-notice", "snippet": "Covers application performance traces, server health metrics, and account data."},
    ],
    "mongodb": [
        {"title": "MongoDB Terms of Service", "url": "https://www.mongodb.com/legal/terms-of-use", "snippet": "Governs MongoDB Atlas managed cloud database, serverless clusters, and Realm sync."},
        {"title": "MongoDB Privacy Policy", "url": "https://www.mongodb.com/legal/privacy-policy", "snippet": "Covers cluster connection metrics, administrative logs, and billing details."},
    ],
    "redis": [
        {"title": "Redis Terms of Service", "url": "https://redis.io/legal/terms-of-service/", "snippet": "Governs in-memory data store licenses, Redis Cloud instances, and enterprise software."},
        {"title": "Redis Privacy Policy", "url": "https://redis.io/legal/privacy-policy/", "snippet": "Details cloud account authentication, usage monitoring, and marketing telemetry."},
    ],
    "snowflake": [
        {"title": "Snowflake Terms of Service", "url": "https://www.snowflake.com/en/legal-hub/terms-of-service/", "snippet": "Governs data cloud warehouses, compute credits, and cross-cloud data sharing."},
        {"title": "Snowflake Privacy Notice", "url": "https://www.snowflake.com/en/legal-hub/privacy-policy/", "snippet": "Covers customer data isolation, query execution logs, and compliance standards."},
    ],
    "databricks": [
        {"title": "Databricks Terms of Use", "url": "https://www.databricks.com/legal/terms-of-use", "snippet": "Governs lakehouse data platforms, Apache Spark clusters, and MLflow compute services."},
        {"title": "Databricks Privacy Notice", "url": "https://www.databricks.com/legal/privacy-notice", "snippet": "Details user telemetry, enterprise access governance, and cloud platform auditing."},
    ],
    "twilio": [
        {"title": "Twilio Terms of Service", "url": "https://www.twilio.com/en-us/legal/tos", "snippet": "Governs SMS APIs, voice calling, Verify authentication, and telecommunications compliance."},
        {"title": "Twilio Privacy Notice", "url": "https://www.twilio.com/en-us/legal/privacy", "snippet": "Covers call detail records (CDRs), phone number routing telemetry, and regulatory retention."},
    ],
    "sendgrid": [
        {"title": "SendGrid Terms of Service", "url": "https://www.twilio.com/en-us/legal/tos", "snippet": "Governs transactional email delivery, marketing campaigns, and anti-spam compliance."},
        {"title": "SendGrid Privacy Policy", "url": "https://www.twilio.com/en-us/legal/privacy", "snippet": "Details email delivery logs, bounce tracking, and recipient telemetry."},
    ],
    "resend": [
        {"title": "Resend Terms of Service", "url": "https://resend.com/legal/terms-of-service", "snippet": "Governs modern developer email APIs, custom domain DKIM/SPF verification, and delivery."},
        {"title": "Resend Privacy Policy", "url": "https://resend.com/legal/privacy-policy", "snippet": "Details email dispatch logs, webhook delivery records, and account security."},
    ],
    "stackoverflow": [
        {"title": "Stack Overflow Public Network Terms", "url": "https://stackoverflow.com/legal/terms-of-service/public", "snippet": "Governs community Q&A, reputation points, CC BY-SA content licensing, and moderation."},
        {"title": "Stack Overflow Privacy Policy", "url": "https://stackoverflow.com/legal/privacy-policy", "snippet": "Covers developer profile tracking, job searches, and community telemetry."},
    ],

    # ---------------------------------------------------------
    # 4. Productivity, Workspace & Creative Collaboration
    # ---------------------------------------------------------
    "notion": [
        {"title": "Notion Terms and Conditions", "url": "https://www.notion.so/Terms-and-Privacy-28fc8652d37f487381ade7a256950346", "snippet": "Governs collaborative documentation, Notion AI, and enterprise workspaces."},
        {"title": "Notion Privacy Policy", "url": "https://www.notion.so/Privacy-Policy-3468d120cf614d4c9014c09f6adc9091", "snippet": "Covers workspace content confidentiality, telemetry, and subprocessor disclosures."},
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
    "box": [
        {"title": "Box Terms of Service", "url": "https://www.box.com/legal/termsofservice", "snippet": "Governs enterprise cloud content management, regulatory compliance, and governance."},
        {"title": "Box Privacy Policy", "url": "https://www.box.com/legal/privacypolicy", "snippet": "Details enterprise audit logs, file access controls, and customer data encryption."},
    ],
    "figma": [
        {"title": "Figma Terms of Service", "url": "https://www.figma.com/summary-of-terms/", "snippet": "Terms covering collaborative design files, team libraries, and plugin hosting."},
        {"title": "Figma Privacy Policy", "url": "https://www.figma.com/privacy/", "snippet": "Details design canvas telemetry, collaboration events, and user accounts."},
    ],
    "canva": [
        {"title": "Canva Terms of Use", "url": "https://www.canva.com/policies/terms-of-use/", "snippet": "Governs graphic design templates, stock media licensing, and Magic Studio AI tools."},
        {"title": "Canva Privacy Policy", "url": "https://www.canva.com/policies/privacy-policy/", "snippet": "Covers user project telemetry, uploaded media assets, and personalized recommendations."},
    ],
    "adobe": [
        {"title": "Adobe General Terms of Use", "url": "https://www.adobe.com/legal/terms.html", "snippet": "Governs Creative Cloud, Photoshop, Acrobat, Firefly AI, and subscription auto-renewals."},
        {"title": "Adobe Privacy Policy", "url": "https://www.adobe.com/privacy/policy.html", "snippet": "Details cloud document syncing, desktop app diagnostic telemetry, and machine learning."},
    ],
    "linear": [
        {"title": "Linear Terms of Service", "url": "https://linear.app/terms", "snippet": "Governs issue tracking, software roadmap planning, Git integrations, and team workspaces."},
        {"title": "Linear Privacy Policy", "url": "https://linear.app/privacy", "snippet": "Explains workspace issue confidentiality, account authentication, and telemetry."},
    ],
    "asana": [
        {"title": "Asana Terms of Service", "url": "https://asana.com/terms", "snippet": "Governs project management boards, workflow automation rules, and organizational goals."},
        {"title": "Asana Privacy Statement", "url": "https://asana.com/privacy", "snippet": "Details workspace telemetry, task assignment logs, and third-party app permissions."},
    ],
    "monday": [
        {"title": "monday.com Terms of Service", "url": "https://monday.com/terms/tos/", "snippet": "Governs work operating system boards, custom automations, and CRM integrations."},
        {"title": "monday.com Privacy Policy", "url": "https://monday.com/terms/privacy/", "snippet": "Covers enterprise board data protection, usage statistics, and subprocessor compliance."},
    ],
    "trello": [
        {"title": "Trello Terms of Service", "url": "https://www.atlassian.com/legal/cloud-terms-of-service", "snippet": "Governs Kanban boards, Power-Ups, Butler automation, and Atlassian account linking."},
        {"title": "Trello Privacy Policy", "url": "https://www.atlassian.com/legal/privacy-policy", "snippet": "Covers board activity feeds, team member permissions, and diagnostic metrics."},
    ],
    "clickup": [
        {"title": "ClickUp Terms of Service", "url": "https://clickup.com/terms", "snippet": "Governs all-in-one productivity suites, task tracking, Docs, and ClickUp Brain AI."},
        {"title": "ClickUp Privacy Policy", "url": "https://clickup.com/privacy", "snippet": "Details workspace information security, user telemetry, and billing details."},
    ],
    "airtable": [
        {"title": "Airtable Terms of Service", "url": "https://www.airtable.com/tos", "snippet": "Governs relational database spreadsheets, automated workflows, and app interfaces."},
        {"title": "Airtable Privacy Policy", "url": "https://www.airtable.com/privacy", "snippet": "Covers base data confidentiality, user access permissions, and enterprise encryption."},
    ],
    "miro": [
        {"title": "Miro Terms of Service", "url": "https://miro.com/legal/terms-of-service/", "snippet": "Governs digital whiteboard collaboration, infinite canvas diagrams, and enterprise security."},
        {"title": "Miro Privacy Policy", "url": "https://miro.com/legal/privacy-policy/", "snippet": "Details canvas interaction telemetry, meeting notes security, and account management."},
    ],
    "loom": [
        {"title": "Loom Terms of Service", "url": "https://www.loom.com/terms-of-service", "snippet": "Governs async video recording, AI video transcripts, and Atlassian enterprise integration."},
        {"title": "Loom Privacy Policy", "url": "https://www.loom.com/privacy-policy", "snippet": "Details video file hosting, viewer engagement telemetry, and transcript storage."},
    ],
    "evernote": [
        {"title": "Evernote Terms of Service", "url": "https://evernote.com/legal/terms-of-service", "snippet": "Governs note-taking synchronization, web clipping, and Bending Spoons subscriptions."},
        {"title": "Evernote Privacy Policy", "url": "https://evernote.com/legal/privacy", "snippet": "Explains customer note encryption, data access audits, and search indexing."},
    ],
    "todoist": [
        {"title": "Todoist Terms of Service", "url": "https://todoist.com/terms", "snippet": "Governs task list synchronization, recurring reminders, and Doist cloud accounts."},
        {"title": "Todoist Privacy Policy", "url": "https://todoist.com/privacy", "snippet": "Details task metadata handling, data portability, and privacy commitments."},
    ],
    "zapier": [
        {"title": "Zapier Terms of Service", "url": "https://zapier.com/legal/terms", "snippet": "Governs cross-application automated Zaps, webhook relays, and authentication connections."},
        {"title": "Zapier Privacy Policy", "url": "https://zapier.com/legal/privacy", "snippet": "Explains third-party API token encryption, execution logs, and data retention."},
    ],
    "docusign": [
        {"title": "DocuSign Terms of Use", "url": "https://www.docusign.com/company/terms-and-conditions/web", "snippet": "Governs legally binding electronic signatures, audit trails, and contract envelope routing."},
        {"title": "DocuSign Privacy Notice", "url": "https://www.docusign.com/privacy", "snippet": "Details identity verification records, digital signature audit logs, and compliance."},
    ],
    "mailchimp": [
        {"title": "Mailchimp Standard Terms of Use", "url": "https://mailchimp.com/legal/terms/", "snippet": "Governs email newsletter distribution, audience segmentation, and anti-spam requirements."},
        {"title": "Intuit Global Privacy Statement", "url": "https://www.intuit.com/privacy/statement/", "snippet": "Details subscriber contact data handling, open-rate telemetry, and cross-Intuit profiling."},
    ],
    "webflow": [
        {"title": "Webflow Terms of Service", "url": "https://webflow.com/legal/terms", "snippet": "Governs visual web development, CMS hosting, custom code embeds, and ecommerce."},
        {"title": "Webflow Privacy Policy", "url": "https://webflow.com/legal/privacy", "snippet": "Details designer telemetry, published website visitor metrics, and account data."},
    ],
    "wordpress": [
        {"title": "WordPress.com Terms of Service", "url": "https://wordpress.com/tos/", "snippet": "Governs Automattic managed blogging, plugin hosting, and custom domain subscriptions."},
        {"title": "Automattic Privacy Policy", "url": "https://automattic.com/privacy/", "snippet": "Covers visitor comment tracking, Jetpack stats telemetry, and account security."},
    ],
    "squarespace": [
        {"title": "Squarespace Terms of Service", "url": "https://www.squarespace.com/terms-of-service", "snippet": "Governs website builders, domain registrations, Acuity Scheduling, and commerce fees."},
        {"title": "Squarespace Privacy Policy", "url": "https://www.squarespace.com/privacy", "snippet": "Details site analytics, subscriber lists, checkout data, and payment telemetry."},
    ],
    "wix": [
        {"title": "Wix Terms of Use", "url": "https://www.wix.com/about/terms-of-use", "snippet": "Governs website creation, Studio workspaces, app market widgets, and domain registrations."},
        {"title": "Wix Privacy Policy", "url": "https://www.wix.com/about/privacy", "snippet": "Explains website visitor data handling, customer account security, and telemetry."},
    ],

    # ---------------------------------------------------------
    # 5. Fintech, Payments & Banking Services
    # ---------------------------------------------------------
    "stripe": [
        {"title": "Stripe Services Agreement", "url": "https://stripe.com/legal/consumer", "snippet": "Terms governing payment processing, checkout, and merchant settlements."},
        {"title": "Stripe Privacy Policy", "url": "https://stripe.com/privacy", "snippet": "Covers financial transaction monitoring and fraud detection algorithms."},
    ],
    "paypal": [
        {"title": "PayPal User Agreement", "url": "https://www.paypal.com/us/legalhub/useragreement-full", "snippet": "Covers buyer protection, currency exchange fees, and account holds."},
        {"title": "PayPal Privacy Statement", "url": "https://www.paypal.com/us/legalhub/privacy-full", "snippet": "Details credit reporting and financial regulatory compliance sharing."},
    ],
    "venmo": [
        {"title": "Venmo User Agreement", "url": "https://venmo.com/legal/us-user-agreement/", "snippet": "Governs peer-to-peer money transfers, social feed transactions, and debit cards."},
        {"title": "Venmo Privacy Statement", "url": "https://venmo.com/legal/us-privacy-policy/", "snippet": "Details social feed privacy controls, transaction metadata, and banking partner reports."},
    ],
    "square": [
        {"title": "Square General Terms of Service", "url": "https://squareup.com/us/en/legal/general/ua", "snippet": "Governs Point of Sale hardware, merchant payment processing, and seller capital."},
        {"title": "Block Privacy Notice", "url": "https://squareup.com/us/en/legal/general/privacy", "snippet": "Covers payment card tokenization, transaction histories, and merchant analytics."},
    ],
    "cashapp": [
        {"title": "Cash App Terms of Service", "url": "https://cash.app/legal/us/en-us/tos", "snippet": "Governs Cash App balance, Cash Card, Bitcoin trades, and fractional stock investing."},
        {"title": "Cash App Privacy Notice", "url": "https://cash.app/legal/us/en-us/privacy", "snippet": "Explains regulatory KYC identity verification, debit card spending logs, and telemetry."},
    ],
    "wise": [
        {"title": "Wise Customer Agreement", "url": "https://wise.com/terms-and-conditions", "snippet": "Governs multi-currency accounts, international wire transfers, and mid-market exchange rates."},
        {"title": "Wise Privacy Policy", "url": "https://wise.com/privacy-policy", "snippet": "Details international cross-border anti-money laundering (AML) compliance disclosures."},
    ],
    "revolut": [
        {"title": "Revolut Personal Terms", "url": "https://www.revolut.com/legal/terms/", "snippet": "Governs digital banking, multi-currency debit cards, and cryptocurrency exchange."},
        {"title": "Revolut Customer Privacy Notice", "url": "https://www.revolut.com/legal/privacy/", "snippet": "Details biometric KYC verification, location-based fraud detection, and credit scoring."},
    ],
    "robinhood": [
        {"title": "Robinhood Terms and Conditions", "url": "https://robinhood.com/us/en/support/articles/user-agreement/", "snippet": "Governs commission-free stock trading, margin accounts, options, and cash management."},
        {"title": "Robinhood Privacy Policy", "url": "https://robinhood.com/us/en/support/articles/privacy-policy/", "snippet": "Details SEC/FINRA regulatory reporting, trade execution disclosures, and security."},
    ],
    "coinbase": [
        {"title": "Coinbase User Agreement", "url": "https://www.coinbase.com/legal/user_agreement", "snippet": "Governs cryptocurrency exchange trades, digital asset custody, and staking rewards."},
        {"title": "Coinbase Privacy Policy", "url": "https://www.coinbase.com/legal/privacy", "snippet": "Explains blockchain address tracking, tax reporting disclosures, and biometric identity."},
    ],
    "kraken": [
        {"title": "Kraken Terms of Service", "url": "https://www.kraken.com/legal", "snippet": "Governs spot and futures digital asset trading, margin leverage, and security protocols."},
        {"title": "Kraken Privacy Notice", "url": "https://www.kraken.com/legal/privacy", "snippet": "Details cryptographic wallet telemetry, regulatory reporting, and identity authentication."},
    ],
    "binance": [
        {"title": "Binance Terms of Use", "url": "https://www.binance.com/en/terms", "snippet": "Governs global crypto exchange services, futures trading, and API execution."},
        {"title": "Binance Privacy Policy", "url": "https://www.binance.com/en/privacy", "snippet": "Covers international identity verification, trade audits, and anti-fraud monitoring."},
    ],
    "plaid": [
        {"title": "Plaid End User Services Agreement", "url": "https://plaid.com/legal/", "snippet": "Governs consumer bank account credential verification and financial data aggregation."},
        {"title": "Plaid Privacy Policy", "url": "https://plaid.com/legal/#consumers", "snippet": "Details bank transaction history aggregation, balance retrieval, and data encryption."},
    ],
    "klarna": [
        {"title": "Klarna Terms and Conditions", "url": "https://www.klarna.com/us/legal/", "snippet": "Governs Buy Now Pay Later (BNPL) 4-installment financing, credit lines, and merchant checkouts."},
        {"title": "Klarna Privacy Notice", "url": "https://www.klarna.com/us/privacy/", "snippet": "Details credit bureau inquiries, purchase history profiling, and payment reminders."},
    ],
    "affirm": [
        {"title": "Affirm Terms of Use", "url": "https://www.affirm.com/terms", "snippet": "Governs consumer installment loans, point-of-sale financing, and savings accounts."},
        {"title": "Affirm Privacy Policy", "url": "https://www.affirm.com/privacy", "snippet": "Details creditworthiness evaluations, debt collection disclosures, and personal data usage."},
    ],
    "intuit": [
        {"title": "Intuit Terms of Service", "url": "https://www.intuit.com/legal/terms/en-us/", "snippet": "Governs TurboTax, QuickBooks, and Credit Karma accounting and tax filing software."},
        {"title": "Intuit Global Privacy Statement", "url": "https://www.intuit.com/privacy/statement/", "snippet": "Covers sensitive IRS tax filing records, payroll data, and credit score monitoring."},
    ],
    "patreon": [
        {"title": "Patreon Terms of Use", "url": "https://www.patreon.com/policy/legal", "snippet": "Governs creator memberships, subscriber patron billing, and community content standards."},
        {"title": "Patreon Privacy Policy", "url": "https://www.patreon.com/policy/privacy", "snippet": "Covers pledge tracking, patron contact details, and payment processor interactions."},
    ],
    "kickstarter": [
        {"title": "Kickstarter Terms of Use", "url": "https://www.kickstarter.com/terms-of-use", "snippet": "Governs crowdfunding pledges, creator reward fulfillment, and dispute resolution."},
        {"title": "Kickstarter Privacy Policy", "url": "https://www.kickstarter.com/privacy", "snippet": "Details backer pledge histories, payment authorization records, and marketing."},
    ],
    "gofundme": [
        {"title": "GoFundMe Terms of Service", "url": "https://www.gofundme.com/c/terms", "snippet": "Governs charitable fundraisers, medical/personal donations, and GoFundMe Giving Guarantee."},
        {"title": "GoFundMe Privacy Policy", "url": "https://www.gofundme.com/c/privacy", "snippet": "Covers donor payment information, public donor lists, and tax reporting requirements."},
    ],

    # ---------------------------------------------------------
    # 6. E-Commerce, Retail & On-Demand Delivery
    # ---------------------------------------------------------
    "ebay": [
        {"title": "eBay User Agreement", "url": "https://www.ebay.com/help/policies/member-behaviour-policies/user-agreement?id=4259", "snippet": "Governs online auctions, fixed-price purchases, seller performance, and dispute resolution."},
        {"title": "eBay User Privacy Notice", "url": "https://www.ebay.com/help/policies/member-behaviour-policies/user-privacy-notice-privacy-policy?id=4260", "snippet": "Explains bidding telemetry, purchasing behavior, and third-party advertising profiling."},
    ],
    "shopify": [
        {"title": "Shopify Terms of Service", "url": "https://www.shopify.com/legal/terms", "snippet": "Governs merchant ecommerce storefronts, Shopify POS, checkout routing, and payment fees."},
        {"title": "Shopify Privacy Policy", "url": "https://www.shopify.com/legal/privacy", "snippet": "Details merchant data handling, buyer checkout telemetry, and fraud risk scoring."},
    ],
    "etsy": [
        {"title": "Etsy Terms of Use", "url": "https://www.etsy.com/legal/terms-of-use", "snippet": "Governs handmade craft marketplaces, vintage goods selling, and seller fees."},
        {"title": "Etsy Privacy Policy", "url": "https://www.etsy.com/legal/privacy", "snippet": "Details buyer shopping recommendations, merchant analytics, and targeted promotions."},
    ],
    "walmart": [
        {"title": "Walmart.com Terms of Use", "url": "https://www.walmart.com/help/article/walmart-com-terms-of-use/3b75080af40340d6bbd596f11618e1b0", "snippet": "Governs retail purchases, Walmart+ memberships, delivery subscriptions, and arbitration."},
        {"title": "Walmart Privacy Policy", "url": "https://corporate.walmart.com/privacy-security/walmart-privacy-policy", "snippet": "Details in-store purchase matching, app geolocation tracking, and consumer marketing."},
    ],
    "target": [
        {"title": "Target Terms and Conditions", "url": "https://www.target.com/c/terms-conditions/-/N-4sr7l", "snippet": "Governs Target Circle loyalty perks, online orders, RedCard discounts, and return policies."},
        {"title": "Target Privacy Policy", "url": "https://www.target.com/c/target-privacy-policy/-/N-4sr7p", "snippet": "Details customer loyalty telemetry, mobile app location services, and ad personalization."},
    ],
    "bestbuy": [
        {"title": "Best Buy Terms and Conditions", "url": "https://www.bestbuy.com/site/help-topics/terms-and-conditions/pcmcat204400050067.c", "snippet": "Governs consumer electronics sales, Geek Squad protection plans, and Totaltech memberships."},
        {"title": "Best Buy Privacy Policy", "url": "https://www.bestbuy.com/site/help-topics/privacy-policy/pcmcat204400050062.c", "snippet": "Covers repair device handling, purchase warranties, and customer behavioral profiling."},
    ],
    "homedepot": [
        {"title": "The Home Depot Terms of Use", "url": "https://www.homedepot.com/c/Terms_of_Use", "snippet": "Governs home improvement orders, tool rentals, pro contractor accounts, and delivery."},
        {"title": "The Home Depot Privacy and Security Statement", "url": "https://www.homedepot.com/c/Privacy_Security", "snippet": "Covers store pickup tracking, online contractor profiles, and commercial telemetry."},
    ],
    "wayfair": [
        {"title": "Wayfair Terms of Use", "url": "https://www.wayfair.com/help/article/terms_and_conditions", "snippet": "Governs furniture and home decor orders, white-glove delivery, and returns."},
        {"title": "Wayfair Privacy Policy", "url": "https://www.wayfair.com/help/article/privacy_policy", "snippet": "Details visual browsing history, augmented reality room view telemetry, and ads."},
    ],
    "alibaba": [
        {"title": "Alibaba.com Terms of Use", "url": "https://rule.alibaba.com/rule/detail/2041.htm", "snippet": "Governs international B2B wholesale trade, Trade Assurance guarantees, and supplier accounts."},
        {"title": "Alibaba.com Privacy Policy", "url": "https://rule.alibaba.com/rule/detail/2034.htm", "snippet": "Details cross-border commerce verification, merchant audits, and transaction logs."},
    ],
    "aliexpress": [
        {"title": "AliExpress Terms of Use", "url": "https://help.aliexpress.com/buyer_terms_conditions.html", "snippet": "Governs consumer retail orders, global shipping, dispute resolution, and refunds."},
        {"title": "AliExpress Privacy Policy", "url": "https://help.aliexpress.com/privacy_policy.html", "snippet": "Covers buyer location telemetry, purchase histories, and international shipping data."},
    ],
    "temu": [
        {"title": "Temu Terms of Use", "url": "https://www.temu.com/terms-of-use.html", "snippet": "Governs discount consumer marketplace orders, shipping coupons, and gamified promotions."},
        {"title": "Temu Privacy Policy", "url": "https://www.temu.com/privacy-policy.html", "snippet": "Details device fingerprinting, clipboard telemetry, social referrals, and ad profiling."},
    ],
    "shein": [
        {"title": "SHEIN Terms and Conditions", "url": "https://us.shein.com/Terms-and-Conditions-a-399.html", "snippet": "Governs fast fashion online purchases, rewards points, shipping policies, and intellectual property."},
        {"title": "SHEIN Privacy Policy", "url": "https://us.shein.com/Privacy-Security-Policy-a-282.html", "snippet": "Covers browsing behavior, mobile app device analytics, and targeted fashion advertising."},
    ],
    "myntra": [
        {"title": "Myntra Terms of Use", "url": "https://www.myntra.com/termsofuse", "snippet": "Official Terms of Use governing online shopping, accounts, and consumer returns on Myntra."},
        {"title": "Myntra Privacy Policy", "url": "https://www.myntra.com/privacypolicy", "snippet": "Explains user account telemetry, purchase histories, and device information handling."},
    ],
    "instacart": [
        {"title": "Instacart Terms of Service", "url": "https://www.instacart.com/terms", "snippet": "Governs grocery delivery orders, personal shopper fulfillment, and Instacart+ subscriptions."},
        {"title": "Instacart Privacy Policy", "url": "https://www.instacart.com/privacy", "snippet": "Covers supermarket loyalty card linking, delivery address telemetry, and ad targeting."},
    ],
    "doordash": [
        {"title": "DoorDash Terms of Service", "url": "https://help.doordash.com/consumers/s/terms-and-conditions-us", "snippet": "Governs restaurant food delivery, DashPass subscriptions, tip policies, and arbitration."},
        {"title": "DoorDash Privacy Policy", "url": "https://help.doordash.com/consumers/s/privacy-policy-us", "snippet": "Details real-time delivery GPS tracking, restaurant preferences, and payment telemetry."},
    ],
    "ubereats": [
        {"title": "Uber Eats Terms of Use", "url": "https://www.uber.com/legal/en/document/?name=general-terms-of-use", "snippet": "Governs restaurant ordering, courier dispatch fees, and Uber One memberships."},
        {"title": "Uber Eats Privacy Notice", "url": "https://www.uber.com/legal/en/document/?name=privacy-notice", "snippet": "Covers order telemetry, dietary preferences, and courier GPS tracking."},
    ],
    "grubhub": [
        {"title": "Grubhub Terms of Use", "url": "https://www.grubhub.com/legal/terms-of-use", "snippet": "Governs online takeout food orders, Grubhub+ memberships, and restaurant listings."},
        {"title": "Grubhub Privacy Policy", "url": "https://www.grubhub.com/legal/privacy-policy", "snippet": "Covers order history tracking, location data for delivery, and marketing telemetry."},
    ],

    # ---------------------------------------------------------
    # 7. Rideshare, Travel & Hospitality
    # ---------------------------------------------------------
    "uber": [
        {"title": "Uber Terms of Use", "url": "https://www.uber.com/legal/en/document/?name=general-terms-of-use", "snippet": "Covers passenger transportation, Uber Eats, and mandatory arbitration."},
        {"title": "Uber Privacy Notice", "url": "https://www.uber.com/legal/en/document/?name=privacy-notice", "snippet": "Covers continuous GPS tracking, driver ratings, and route telemetry."},
    ],
    "lyft": [
        {"title": "Lyft Terms of Service", "url": "https://www.lyft.com/terms", "snippet": "Governs rideshare matchmaking, driver fees, bike/scooter rentals, and disputes."},
        {"title": "Lyft Privacy Policy", "url": "https://www.lyft.com/privacy", "snippet": "Covers rider location tracking, ride duration metrics, and contact synchronization."},
    ],
    "airbnb": [
        {"title": "Airbnb Terms of Service", "url": "https://www.airbnb.com/help/article/2908", "snippet": "Covers host and guest booking rules, cancellations, and damages."},
        {"title": "Airbnb Privacy Policy", "url": "https://www.airbnb.com/help/article/2855", "snippet": "Explains identity verification, passport collection, and host messaging logs."},
    ],
    "booking": [
        {"title": "Booking.com Terms and Conditions", "url": "https://www.booking.com/content/terms.html", "snippet": "Governs hotel reservations, flight bookings, car rentals, and cancellation guarantees."},
        {"title": "Booking.com Privacy Statement", "url": "https://www.booking.com/content/privacy.html", "snippet": "Details travel itinerary telemetry, passport verification, and hotel partner data sharing."},
    ],
    "expedia": [
        {"title": "Expedia Terms of Use", "url": "https://www.expedia.com/lp/b/terms-of-service", "snippet": "Governs vacation packages, airfare reservations, One Key loyalty points, and lodging."},
        {"title": "Expedia Privacy Policy", "url": "https://www.expedia.com/lp/b/privacy-policy", "snippet": "Details flight preference tracking, booking details, and travel partner disclosures."},
    ],
    "tripadvisor": [
        {"title": "TripAdvisor Terms of Use", "url": "https://tripadvisor.mediaroom.com/US-terms-of-use", "snippet": "Governs traveler reviews, photo uploads, hotel rankings, and tour bookings."},
        {"title": "TripAdvisor Privacy and Cookies Statement", "url": "https://tripadvisor.mediaroom.com/US-privacy-policy", "snippet": "Covers user travel reviews, location-based tourist recommendations, and ad tracking."},
    ],
    "vrbo": [
        {"title": "Vrbo Terms and Conditions", "url": "https://www.vrbo.com/en-us/legal/terms-and-conditions", "snippet": "Governs whole-home vacation rentals, host damage deposits, and Expedia Group policies."},
        {"title": "Vrbo Privacy Statement", "url": "https://www.vrbo.com/en-us/legal/privacy-policy", "snippet": "Details property inquiry logs, guest identity verification, and booking telemetry."},
    ],
    "kayak": [
        {"title": "Kayak Terms and Conditions", "url": "https://www.kayak.com/terms-of-use", "snippet": "Governs travel search aggregation, price forecasting, and third-party airline redirects."},
        {"title": "Kayak Privacy Policy", "url": "https://www.kayak.com/privacy", "snippet": "Details search query telemetry, flight alert subscriptions, and Booking Holdings sharing."},
    ],
    "skyscanner": [
        {"title": "Skyscanner Terms of Service", "url": "https://www.skyscanner.com/terms-of-service", "snippet": "Governs flight comparison engines, car hire quotes, and redirect booking terms."},
        {"title": "Skyscanner Privacy Policy", "url": "https://www.skyscanner.com/privacy-policy", "snippet": "Covers travel search telemetry, flight price alert emails, and device identifiers."},
    ],
    "marriott": [
        {"title": "Marriott Terms of Use", "url": "https://www.marriott.com/about/terms-of-use.mi", "snippet": "Governs Marriott Bonvoy loyalty rewards, hotel room reservations, and mobile keys."},
        {"title": "Marriott Global Privacy Statement", "url": "https://www.marriott.com/about/privacy.mi", "snippet": "Details guest stay histories, payment records, and on-premises Wi-Fi telemetry."},
    ],
    "hilton": [
        {"title": "Hilton Terms and Conditions", "url": "https://www.hilton.com/en/p/terms-and-conditions/", "snippet": "Governs Hilton Honors points, hotel check-ins, Digital Key access, and reservations."},
        {"title": "Hilton Global Privacy Statement", "url": "https://www.hilton.com/en/p/global-privacy-statement/", "snippet": "Covers guest preferences, room service records, and hotel partner disclosures."},
    ],
    "delta": [
        {"title": "Delta Air Lines Terms of Use", "url": "https://www.delta.com/us/en/legal/terms-of-use", "snippet": "Governs flight ticket purchases, SkyMiles loyalty program, and in-flight Wi-Fi terms."},
        {"title": "Delta Air Lines Privacy Policy", "url": "https://www.delta.com/us/en/legal/privacy-policy", "snippet": "Covers TSA Secure Flight data requirements, passport details, and travel telemetry."},
    ],
    "united": [
        {"title": "United Airlines Legal Information", "url": "https://www.united.com/en/us/fly/legal.html", "snippet": "Governs airline contract of carriage, MileagePlus rewards, baggage rules, and ticket refunds."},
        {"title": "United Airlines Privacy Policy", "url": "https://www.united.com/en/us/fly/privacy-policy.html", "snippet": "Details flight booking manifests, government border agency data sharing, and security."},
    ],

    # ---------------------------------------------------------
    # 8. Streaming, Media & Digital Entertainment
    # ---------------------------------------------------------
    "netflix": [
        {"title": "Netflix Terms of Use", "url": "https://help.netflix.com/legal/termsofuse", "snippet": "Governs streaming access, household account sharing, and monthly billing renewal."},
        {"title": "Netflix Privacy Statement", "url": "https://help.netflix.com/legal/privacy", "snippet": "Details viewing history collection, device telemetry, and streaming recommendations."},
    ],
    "spotify": [
        {"title": "Spotify Terms and Conditions of Use", "url": "https://www.spotify.com/legal/end-user-agreement/", "snippet": "General terms covering Spotify subscriptions, billing, and content licensing."},
        {"title": "Spotify Privacy Policy", "url": "https://www.spotify.com/legal/privacy-policy/", "snippet": "Covers user listening history, behavioral telemetry, and ad targeting."},
    ],
    "disneyplus": [
        {"title": "Disney+ Subscriber Agreement", "url": "https://www.disneyplus.com/legal/subscriber-agreement", "snippet": "Governs Disney+, Pixar, Marvel, Star Wars streaming, downloads, and household access."},
        {"title": "Disney Privacy Policy", "url": "https://privacy.thewaltdisneycompany.com/en/", "snippet": "Details viewing telemetry, parental control profiles, and cross-Disney marketing."},
    ],
    "hulu": [
        {"title": "Hulu Subscriber Agreement", "url": "https://www.hulu.com/terms", "snippet": "Governs on-demand and Live TV streaming, ad-supported tiers, and Disney bundle terms."},
        {"title": "Hulu Privacy Policy", "url": "https://www.hulu.com/privacy", "snippet": "Covers viewing habits, targeted advertising telemetry, and household device identifiers."},
    ],
    "max": [
        {"title": "Max Terms of Use", "url": "https://auth.max.com/terms-of-use", "snippet": "Governs Warner Bros. Discovery Max streaming, HBO content licenses, and subscription fees."},
        {"title": "Max Privacy Policy", "url": "https://www.wbdprivacy.com/policycenter/b2c/", "snippet": "Details video streaming telemetry, profile preferences, and targeted advertising."},
    ],
    "peacock": [
        {"title": "Peacock Terms of Use", "url": "https://www.peacocktv.com/terms", "snippet": "Governs NBCUniversal streaming video, sports broadcasts, and subscription renewals."},
        {"title": "NBCUniversal Privacy Policy", "url": "https://www.nbcuniversal.com/privacy", "snippet": "Covers viewing habits, video ad impressions, and Comcast corporate disclosures."},
    ],
    "paramountplus": [
        {"title": "Paramount+ Subscription Terms", "url": "https://www.paramountplus.com/terms/", "snippet": "Governs CBS, MTV, Nickelodeon, Paramount streaming, and Showtime add-ons."},
        {"title": "Paramount Privacy Policy", "url": "https://www.paramount.com/privacy-policy", "snippet": "Details user viewership logs, device identifiers, and promotional marketing."},
    ],
    "soundcloud": [
        {"title": "SoundCloud Terms of Use", "url": "https://soundcloud.com/terms-of-use", "snippet": "Governs independent music uploads, copyright fingerprinting, and Go+ subscriptions."},
        {"title": "SoundCloud Privacy Policy", "url": "https://soundcloud.com/pages/privacy", "snippet": "Covers streaming telemetry, playlist creation, and targeted audio advertising."},
    ],
    "deezer": [
        {"title": "Deezer Terms of Use", "url": "https://www.deezer.com/legal/cgu", "snippet": "Governs digital music streaming, Flow algorithmic recommendations, and offline downloads."},
        {"title": "Deezer Privacy Policy", "url": "https://www.deezer.com/legal/personal-data", "snippet": "Covers audio listening telemetry, subscriber credentials, and ad measurement."},
    ],
    "tidal": [
        {"title": "TIDAL Terms and Conditions", "url": "https://tidal.com/terms", "snippet": "Governs lossless HiFi audio streaming, artist royalty calculations, and Block ecosystem terms."},
        {"title": "TIDAL Privacy Policy", "url": "https://tidal.com/privacy", "snippet": "Details high-resolution audio streaming telemetry, playlists, and user account records."},
    ],
    "pandora": [
        {"title": "Pandora Terms of Use", "url": "https://www.pandora.com/legal", "snippet": "Governs Music Genome Project automated radio stations, SiriusXM subscriptions, and ads."},
        {"title": "Pandora Privacy Policy", "url": "https://www.pandora.com/legal/privacy", "snippet": "Details music preference feedback (thumbs up/down), audio advertising, and telemetry."},
    ],
    "audible": [
        {"title": "Audible Conditions of Use", "url": "https://www.audible.com/legal/conditions-of-use", "snippet": "Governs audiobook purchases, monthly member credits, and Amazon account linking."},
        {"title": "Audible Privacy Notice", "url": "https://www.audible.com/legal/privacy-policy", "snippet": "Details audiobook listening progress, Whispersync bookmark telemetry, and Amazon sharing."},
    ],
    "vimeo": [
        {"title": "Vimeo Terms of Service", "url": "https://vimeo.com/terms", "snippet": "Governs professional video hosting, enterprise live streaming, and OTT monetization."},
        {"title": "Vimeo Privacy Policy", "url": "https://vimeo.com/privacy", "snippet": "Covers video viewer telemetry, embed analytics, and creator account security."},
    ],
    "twitch": [
        {"title": "Twitch Terms of Service", "url": "https://www.twitch.tv/p/en/legal/terms-of-service/", "snippet": "Governs live broadcasting, subscriptions, bits, and chat moderation."},
        {"title": "Twitch Privacy Notice", "url": "https://www.twitch.tv/p/en/legal/privacy-notice/", "snippet": "Details stream viewership metrics and chat analytics."},
    ],
    "medium": [
        {"title": "Medium Terms of Service", "url": "https://policy.medium.com/medium-terms-of-service-9db0094a1e0f", "snippet": "Governs online article publishing, Partner Program compensation, and member paywalls."},
        {"title": "Medium Privacy Policy", "url": "https://policy.medium.com/medium-privacy-policy-f03e51f38dfe", "snippet": "Details reader reading time telemetry, article claps, and recommendation cookies."},
    ],
    "substack": [
        {"title": "Substack Terms of Use", "url": "https://substack.com/tos", "snippet": "Governs newsletter publication, subscriber billing, creator revenue splits, and freedom of speech."},
        {"title": "Substack Privacy Policy", "url": "https://substack.com/privacy", "snippet": "Covers subscriber email lists, open-rate telemetry, and payment processor interactions."},
    ],
    "wikipedia": [
        {"title": "Wikimedia Terms of Use", "url": "https://foundation.wikimedia.org/wiki/Policy:Terms_of_Use", "snippet": "Governs Wikipedia editing, CC BY-SA free content licensing, and non-profit volunteer rules."},
        {"title": "Wikimedia Privacy Policy", "url": "https://foundation.wikimedia.org/wiki/Policy:Privacy_policy", "snippet": "Covers public edit revision logs, IP address tracking for anonymous edits, and minimal data retention."},
    ],

    # ---------------------------------------------------------
    # 9. Gaming & Interactive Entertainment
    # ---------------------------------------------------------
    "steam": [
        {"title": "Steam Subscriber Agreement", "url": "https://store.steampowered.com/subscriber_agreement/", "snippet": "Governs game purchases, digital wallet balances, and software licenses."},
        {"title": "Valve Privacy Policy Agreement", "url": "https://store.steampowered.com/privacy_agreement/", "snippet": "Details gameplay statistics, multiplayer telemetry, and purchase logs."},
    ],
    "valve": [
        {"title": "Valve / Steam Subscriber Agreement", "url": "https://store.steampowered.com/subscriber_agreement/", "snippet": "Governs game purchases, digital wallet balances, and software licenses."},
        {"title": "Valve Privacy Policy", "url": "https://store.steampowered.com/privacy_agreement/", "snippet": "Details gameplay statistics, multiplayer telemetry, and purchase logs."},
    ],
    "epicgames": [
        {"title": "Epic Games Terms of Service", "url": "https://www.epicgames.com/site/en-US/tos", "snippet": "Governs Epic Games Store purchases, Fortnite, Unreal Engine marketplace, and V-Bucks."},
        {"title": "Epic Games Privacy Policy", "url": "https://www.epicgames.com/site/en-US/privacypolicy", "snippet": "Covers in-game telemetry, friend lists, anti-cheat monitoring, and digital store purchases."},
    ],
    "roblox": [
        {"title": "Roblox Terms of Use", "url": "https://en.help.roblox.com/hc/en-us/articles/115004647846-Roblox-Terms-of-Use", "snippet": "Covers Roblox virtual currency, avatar economies, and arbitration clauses."},
        {"title": "Roblox Privacy and Cookie Policy", "url": "https://en.help.roblox.com/hc/en-us/articles/115004630823-Roblox-Privacy-and-Cookie-Policy", "snippet": "Data protection policies specifically concerning minor safety and user accounts."},
    ],
    "playstation": [
        {"title": "PlayStation Network Terms of Service", "url": "https://www.playstation.com/en-us/legal/psn-terms-of-service/", "snippet": "Governs PSN accounts, digital game purchases, PS Plus subscriptions, and console conduct."},
        {"title": "PlayStation Privacy Policy", "url": "https://www.playstation.com/en-us/legal/privacy-policy/", "snippet": "Covers console telemetry, trophy achievements, multiplayer voice logs, and safety."},
    ],
    "nintendo": [
        {"title": "Nintendo User Agreement", "url": "https://www.nintendo.com/terms-of-use/", "snippet": "Governs Nintendo Switch Online, Nintendo eShop purchases, and My Nintendo points."},
        {"title": "Nintendo Privacy Policy", "url": "https://www.nintendo.com/privacy-policy/", "snippet": "Details console gameplay logs, parental controls, and eShop transaction histories."},
    ],
    "ea": [
        {"title": "Electronic Arts User Agreement", "url": "https://www.ea.com/legal/user-agreement", "snippet": "Governs EA app, EA Play subscriptions, in-game virtual currency, and fair play standards."},
        {"title": "Electronic Arts Privacy and Cookie Policy", "url": "https://www.ea.com/legal/privacy-and-cookie-policy", "snippet": "Details matchmaking telemetry, anti-cheat detection, and targeted promotional offers."},
    ],
    "ubisoft": [
        {"title": "Ubisoft Terms of Use", "url": "https://legal.ubi.com/termsofuse/en-US", "snippet": "Governs Ubisoft Connect accounts, Ubisoft+ subscriptions, and multiplayer conduct."},
        {"title": "Ubisoft Privacy Policy", "url": "https://legal.ubi.com/privacypolicy/en-US", "snippet": "Covers game session telemetry, cross-platform saves, and promotional communication."},
    ],
    "blizzard": [
        {"title": "Battle.net End User License Agreement", "url": "https://www.blizzard.com/en-us/legal/08b946df-660a-40e4-a072-1fbde6b17737/battle-net-end-user-license-agreement", "snippet": "Governs World of Warcraft, Overwatch, Diablo, Battle.net accounts, and balance."},
        {"title": "Blizzard Privacy Policy", "url": "https://www.blizzard.com/en-us/legal/a4380ee5-5c8d-4e3e-83e6-940ab5e90170/blizzard-entertainment-online-privacy-policy", "snippet": "Details anti-cheat telemetry (Warden), chat moderation logs, and in-game transaction audits."},
    ],
    "riotgames": [
        {"title": "Riot Games Terms of Service", "url": "https://www.riotgames.com/en/terms-of-service", "snippet": "Governs League of Legends, Valorant, Riot ID, virtual currency (RP/VP), and conduct."},
        {"title": "Riot Games Privacy Notice", "url": "https://www.riotgames.com/en/privacy-notice", "snippet": "Details kernel-level Vanguard anti-cheat telemetry, voice comms moderation, and game logs."},
    ],
    "unity": [
        {"title": "Unity Terms of Service", "url": "https://unity.com/legal/terms-of-service", "snippet": "Governs Unity Editor licenses, runtime fee policies, Asset Store, and Unity Gaming Services."},
        {"title": "Unity Privacy Policy", "url": "https://unity.com/legal/privacy-policy", "snippet": "Covers in-game runtime telemetry, developer dashboard metrics, and Unity Ads SDK data."},
    ],

    # ---------------------------------------------------------
    # 10. Security, Privacy & VPN Services
    # ---------------------------------------------------------
    "1password": [
        {"title": "1Password Terms of Service", "url": "https://1password.com/legal/terms-of-service/", "snippet": "Governs zero-knowledge password vault storage, Secret Key encryption, and team accounts."},
        {"title": "1Password Privacy Policy", "url": "https://1password.com/legal/privacy/", "snippet": "Affirms zero-knowledge architecture: 1Password cannot access user master passwords or vault data."},
    ],
    "bitwarden": [
        {"title": "Bitwarden Terms of Service", "url": "https://bitwarden.com/terms/", "snippet": "Governs open-source password management, vault synchronization, and organization sharing."},
        {"title": "Bitwarden Privacy Policy", "url": "https://bitwarden.com/privacy/", "snippet": "Details end-to-end encryption commitments and zero access to customer vault secrets."},
    ],
    "lastpass": [
        {"title": "LastPass Terms of Service", "url": "https://www.lastpass.com/legal-center/terms-of-service", "snippet": "Governs password vault hosting, browser extension autofill, and multi-factor authentication."},
        {"title": "LastPass Privacy Policy", "url": "https://www.lastpass.com/legal-center/privacy-policy", "snippet": "Covers account billing information, customer telemetry, and security incident notifications."},
    ],
    "nordvpn": [
        {"title": "NordVPN Terms of Service", "url": "https://my.nordaccount.com/legal/terms-of-service/", "snippet": "Governs encrypted VPN tunnels, Threat Protection, dedicated IPs, and subscription renewals."},
        {"title": "NordVPN Privacy Policy", "url": "https://my.nordaccount.com/legal/privacy-policy/", "snippet": "Verified strict no-logs policy: zero retention of user traffic, connection timestamps, or IPs."},
    ],
    "expressvpn": [
        {"title": "ExpressVPN Terms of Service", "url": "https://www.expressvpn.com/tos", "snippet": "Governs Lightway VPN protocol tunnels, router apps, and subscription terms."},
        {"title": "ExpressVPN Privacy Policy", "url": "https://www.expressvpn.com/privacy-policy", "snippet": "Strict independently audited no-activity and no-connection logs commitment."},
    ],
    "proton": [
        {"title": "Proton Terms and Conditions", "url": "https://proton.me/legal/terms", "snippet": "Governs Proton Mail, Proton VPN, Proton Drive, and Proton Pass under Swiss jurisdiction."},
        {"title": "Proton Privacy Policy", "url": "https://proton.me/legal/privacy", "snippet": "Details zero-access email encryption, strict Swiss privacy laws, and minimal metadata logs."},
    ],
    "surfshark": [
        {"title": "Surfshark Terms of Service", "url": "https://surfshark.com/terms-of-service", "snippet": "Governs unlimited device VPN connections, CleanWeb ad-blocking, and Nexus routing."},
        {"title": "Surfshark Privacy Policy", "url": "https://surfshark.com/privacy-policy", "snippet": "Audited RAM-only server infrastructure with a strict zero-logs operational policy."},
    ],
    "malwarebytes": [
        {"title": "Malwarebytes Terms of Service", "url": "https://www.malwarebytes.com/tos", "snippet": "Governs real-time antimalware scanning, ransomware shields, and browser extensions."},
        {"title": "Malwarebytes Privacy Policy", "url": "https://www.malwarebytes.com/privacy", "snippet": "Details threat signature telemetry, quarantine telemetry, and diagnostic logs."},
    ],
    "duckduckgo": [
        {"title": "DuckDuckGo Terms of Service", "url": "https://duckduckgo.com/terms", "snippet": "Governs private search engine use, Privacy Browser, and Email Protection forwarding."},
        {"title": "DuckDuckGo Privacy Policy", "url": "https://duckduckgo.com/privacy", "snippet": "Zero tracking commitment: no search history storage, no IP logging, and tracker blocking."},
    ],
    "brave": [
        {"title": "Brave Terms of Use", "url": "https://brave.com/terms-of-use/", "snippet": "Governs Brave Browser, Brave Shields, Brave Search, and Basic Attention Token (BAT) rewards."},
        {"title": "Brave Privacy Policy", "url": "https://brave.com/privacy/browser/", "snippet": "Details local client-side ad matching, no user profiling, and anonymous search queries."},
    ],
    "mozilla": [
        {"title": "Mozilla Websites & Communications Terms of Use", "url": "https://www.mozilla.org/en-US/about/legal/terms/mozilla/", "snippet": "Governs Firefox browser services, Mozilla accounts, and add-ons repository."},
        {"title": "Mozilla Privacy Policy", "url": "https://www.mozilla.org/en-US/privacy/websites/", "snippet": "Open-source data principles: telemetry minimization, opt-outs, and transparent bug tracking."},
    ],

    # ---------------------------------------------------------
    # 11. Dating & Lifestyle Platforms
    # ---------------------------------------------------------
    "tinder": [
        {"title": "Tinder Terms of Use", "url": "https://policies.tinder.com/terms/intl/en", "snippet": "Governs swiping mechanics, Tinder Gold/Platinum subscriptions, and community conduct rules."},
        {"title": "Tinder Privacy Policy", "url": "https://policies.tinder.com/privacy/intl/en", "snippet": "Details location tracking for matches, photo facial geometry processing, and behavioral data."},
    ],
    "bumble": [
        {"title": "Bumble Terms and Conditions", "url": "https://bumble.com/en-us/terms", "snippet": "Governs women-first messaging rules, Bumble Boost/Premium subscriptions, and safety standards."},
        {"title": "Bumble Privacy Policy", "url": "https://bumble.com/en-us/privacy", "snippet": "Covers precise geolocation matching, profile verification selfies, and member preferences."},
    ],
    "hinge": [
        {"title": "Hinge Terms of Use", "url": "https://hinge.co/terms", "snippet": "Governs relationship-oriented matching, profile prompts, and Match Group subscription terms."},
        {"title": "Hinge Privacy Policy", "url": "https://hinge.co/privacy", "snippet": "Details profile preferences, relationship telemetry, and Match Group cross-app sharing."},
    ],
    "strava": [
        {"title": "Strava Terms of Service", "url": "https://www.strava.com/legal/terms", "snippet": "Governs athletic GPS tracking, segment leaderboards, and Strava subscription perks."},
        {"title": "Strava Privacy Policy", "url": "https://www.strava.com/legal/privacy", "snippet": "Details GPS heatmaps, public/private route visibility controls, and health telemetry."},
    ],
    "duolingo": [
        {"title": "Duolingo Terms of Service", "url": "https://www.duolingo.com/terms", "snippet": "Governs gamified language learning, Super Duolingo subscriptions, and the Duolingo English Test."},
        {"title": "Duolingo Privacy Policy", "url": "https://www.duolingo.com/privacy", "snippet": "Covers language proficiency telemetry, microphone pronunciation recordings, and ads."},
    ],
    "coursera": [
        {"title": "Coursera Terms of Use", "url": "https://www.coursera.org/about/terms", "snippet": "Governs online courses, university certificates, Coursera Plus, and academic integrity policies."},
        {"title": "Coursera Privacy Notice", "url": "https://www.coursera.org/about/privacy", "snippet": "Details assignment grades, proctored exam verification data, and university sharing."},
    ],
    "udemy": [
        {"title": "Udemy Terms of Use", "url": "https://www.udemy.com/terms/", "snippet": "Governs course marketplace purchases, instructor revenue sharing, and lifetime course access."},
        {"title": "Udemy Privacy Policy", "url": "https://www.udemy.com/terms/privacy/", "snippet": "Covers student course progress metrics, video player telemetry, and payment details."},
    ],

    # ---------------------------------------------------------
    # 12. Hardware, Consumer Electronics & Automotive
    # ---------------------------------------------------------
    "tesla": [
        {"title": "Tesla Customer Terms", "url": "https://www.tesla.com/legal/terms", "snippet": "Governs electric vehicle orders, Full Self-Driving (FSD) software licenses, and Powerwall services."},
        {"title": "Tesla Customer Privacy Notice", "url": "https://www.tesla.com/legal/privacy", "snippet": "Details external camera video recording telemetry, Autopilot driving logs, and GPS routes."},
    ],
    "samsung": [
        {"title": "Samsung Terms and Conditions", "url": "https://www.samsung.com/us/common/legal/", "snippet": "Governs Galaxy mobile devices, SmartThings IoT, Samsung Knox security, and appliances."},
        {"title": "Samsung Privacy Policy", "url": "https://www.samsung.com/us/account/privacy-policy/", "snippet": "Details Smart TV viewing data (ACR), SmartThings sensor telemetry, and Galaxy analytics."},
    ],
    "sony": [
        {"title": "Sony Terms of Use", "url": "https://www.sony.com/en_us/SCA/terms-of-use.html", "snippet": "Governs Sony electronics, cameras, audio gear, and Sony group digital services."},
        {"title": "Sony Privacy Policy", "url": "https://www.sony.com/en_us/SCA/privacy-policy.html", "snippet": "Covers consumer product registration, warranty records, and device diagnostics."},
    ],
    "dell": [
        {"title": "Dell Terms of Sale", "url": "https://www.dell.com/learn/us/en/uscorp1/terms-of-sale", "snippet": "Governs PC and server hardware purchases, enterprise support contracts, and warranties."},
        {"title": "Dell Privacy Statement", "url": "https://www.dell.com/learn/us/en/uscorp1/policies-privacy", "snippet": "Details hardware diagnostic telemetry, service tags, and customer support records."},
    ],
    "hp": [
        {"title": "HP Terms of Use", "url": "https://www.hp.com/us-en/terms-of-use.html", "snippet": "Governs laptop, printer, and HP Instant Ink subscription contracts."},
        {"title": "HP Privacy Statement", "url": "https://www.hp.com/us-en/privacy/privacy.html", "snippet": "Covers printer page count telemetry, ink cartridge monitoring, and diagnostic logs."},
    ],
    "lenovo": [
        {"title": "Lenovo Terms of Use", "url": "https://www.lenovo.com/us/en/legal/", "snippet": "Governs ThinkPad, Legion, and Motorola hardware purchases, warranties, and software."},
        {"title": "Lenovo Privacy Statement", "url": "https://www.lenovo.com/us/en/privacy/", "snippet": "Details device hardware health metrics, user registration, and support diagnostic data."},
    ],
    "nvidia": [
        {"title": "NVIDIA Terms of Use", "url": "https://www.nvidia.com/en-us/about-nvidia/legal-info/", "snippet": "Governs GeForce drivers, GeForce NOW cloud gaming, CUDA licenses, and developer portals."},
        {"title": "NVIDIA Privacy Policy", "url": "https://www.nvidia.com/en-us/about-nvidia/privacy-policy/", "snippet": "Details GPU driver telemetry, GeForce Experience crash logs, and cloud gaming metrics."},
    ],
    "intel": [
        {"title": "Intel Terms of Use", "url": "https://www.intel.com/content/www/us/en/legal/terms-of-use.html", "snippet": "Governs processor software drivers, developer documentation, and Intel software suites."},
        {"title": "Intel Privacy Notice", "url": "https://www.intel.com/content/www/us/en/privacy/intel-privacy-notice.html", "snippet": "Details diagnostic system telemetry, hardware identifiers, and enterprise support."},
    ],
    "bose": [
        {"title": "Bose Terms of Use", "url": "https://www.bose.com/legal/terms-of-use", "snippet": "Governs Bose headphone apps, smart soundbars, and firmware updates."},
        {"title": "Bose Privacy Policy", "url": "https://www.bose.com/legal/privacy-policy", "snippet": "Covers headphone volume telemetry, connected app metadata, and warranty claims."},
    ],
    "sonos": [
        {"title": "Sonos Terms of Use", "url": "https://www.sonos.com/en-us/legal/terms", "snippet": "Governs smart speaker hardware, Sonos app ecosystem, and Sonos Radio streaming."},
        {"title": "Sonos Privacy Statement", "url": "https://www.sonos.com/en-us/legal/privacy", "snippet": "Details speaker audio diagnostic telemetry, music service links, and network info."},
    ],

    # ---------------------------------------------------------
    # 13. Enterprise SaaS, Business & CRM Solutions
    # ---------------------------------------------------------
    "salesforce": [
        {"title": "Salesforce Main Services Agreement", "url": "https://www.salesforce.com/company/legal/agreements/", "snippet": "Enterprise terms governing Salesforce CRM, Sales Cloud, Service Cloud, and platform security."},
        {"title": "Salesforce Privacy Statement", "url": "https://www.salesforce.com/company/privacy/", "snippet": "Details enterprise customer data processing, cloud access audits, and multi-tenant telemetry."},
    ],
    "hubspot": [
        {"title": "HubSpot Customer Terms of Service", "url": "https://legal.hubspot.com/terms-of-service", "snippet": "Governs inbound marketing, HubSpot CRM, CMS Hub, and sales pipeline automation."},
        {"title": "HubSpot Privacy Policy", "url": "https://legal.hubspot.com/privacy-policy", "snippet": "Covers lead tracking telemetry, website visitor analytics, and email open metrics."},
    ],
    "zendesk": [
        {"title": "Zendesk Main Services Agreement", "url": "https://www.zendesk.com/company/agreements-and-terms/terms-of-use/", "snippet": "Governs customer support ticketing, Sunshine platform, and live chat widgets."},
        {"title": "Zendesk Privacy Notice", "url": "https://www.zendesk.com/company/agreements-and-terms/privacy-notice/", "snippet": "Details end-user support ticket retention, chat transcripts, and customer agent data."},
    ],
    "intercom": [
        {"title": "Intercom Terms of Service", "url": "https://www.intercom.com/legal/terms-of-service", "snippet": "Governs customer messaging platforms, Fin AI bot resolution, and conversational support."},
        {"title": "Intercom Privacy Policy", "url": "https://www.intercom.com/legal/privacy", "snippet": "Covers website visitor tracking, live chat messenger telemetry, and customer communication logs."},
    ],
    "freshworks": [
        {"title": "Freshworks Terms of Service", "url": "https://www.freshworks.com/terms/", "snippet": "Governs Freshdesk customer support, Freshservice IT service management, and Freshsales CRM."},
        {"title": "Freshworks Privacy Notice", "url": "https://www.freshworks.com/privacy/", "snippet": "Details IT ticket telemetry, agent performance tracking, and customer contact data."},
    ],
    "servicenow": [
        {"title": "ServiceNow Terms of Use", "url": "https://www.servicenow.com/terms-of-use.html", "snippet": "Governs enterprise digital workflow automation, IT service management (ITSM), and security operations."},
        {"title": "ServiceNow Privacy Statement", "url": "https://www.servicenow.com/privacy-statement.html", "snippet": "Covers enterprise audit trails, workflow event telemetry, and subprocessor compliance."},
    ],
    "workday": [
        {"title": "Workday Terms of Use", "url": "https://www.workday.com/en-us/terms-of-use.html", "snippet": "Governs cloud human capital management (HCM), enterprise financial management, and payroll."},
        {"title": "Workday Privacy Statement", "url": "https://www.workday.com/en-us/privacy.html", "snippet": "Covers employee payroll records, HR management logs, and sensitive enterprise workforce data."},
    ],
    "oracle": [
        {"title": "Oracle Cloud Services Agreement", "url": "https://www.oracle.com/legal/terms.html", "snippet": "Governs Oracle Cloud Infrastructure (OCI), autonomous databases, and enterprise software licenses."},
        {"title": "Oracle Privacy Policy", "url": "https://www.oracle.com/legal/privacy/", "snippet": "Covers enterprise cloud diagnostic telemetry, customer account data, and database security audits."},
    ],
    "ibm": [
        {"title": "IBM Terms of Use", "url": "https://www.ibm.com/legal", "snippet": "Governs IBM Cloud, Red Hat OpenShift enterprise subscriptions, watsonx AI, and mainframe software."},
        {"title": "IBM Privacy Statement", "url": "https://www.ibm.com/privacy", "snippet": "Details enterprise customer data isolation, system diagnostic telemetry, and compliance."},
    ],
    "cisco": [
        {"title": "Cisco End User License Agreement", "url": "https://www.cisco.com/c/en/us/about/legal/cloud-and-software/end-user-license-agreement.html", "snippet": "Governs network hardware operating software, Webex collaboration, and Meraki cloud management."},
        {"title": "Cisco Online Privacy Statement", "url": "https://www.cisco.com/c/en/us/about/legal/privacy-full.html", "snippet": "Covers network device telemetry, diagnostic packet data, and Webex meeting metrics."},
    ],
    "tailscale": [
        {"title": "Tailscale Terms of Service", "url": "https://tailscale.com/terms", "snippet": "Governs WireGuard zero-config mesh VPN tunnels, MagicDNS, and node access control lists (ACLs)."},
        {"title": "Tailscale Privacy Policy", "url": "https://tailscale.com/privacy-policy", "snippet": "Affirms zero-log mesh coordination: Tailscale cannot decrypt user traffic passing between nodes."},
    ],
    "ngrok": [
        {"title": "ngrok Terms of Service", "url": "https://ngrok.com/tos", "snippet": "Governs secure ingress tunnels to localhost, reverse proxy domains, and webhook delivery."},
        {"title": "ngrok Privacy Policy", "url": "https://ngrok.com/privacy", "snippet": "Details tunnel traffic metadata, connection telemetry, and developer account logs."},
    ],
    "snyk": [
        {"title": "Snyk Terms of Service", "url": "https://snyk.io/policies/terms-of-service/", "snippet": "Governs developer security scanning, open-source vulnerability detection, and container security."},
        {"title": "Snyk Privacy Policy", "url": "https://snyk.io/policies/privacy/", "snippet": "Covers code repository scanning telemetry, dependency graphs, and developer account records."},
    ],
    "jetbrains": [
        {"title": "JetBrains Toolbox Subscription Agreement", "url": "https://www.jetbrains.com/legal/agreements/toolbox-subscription/", "snippet": "Governs IntelliJ IDEA, PyCharm, WebStorm, CLion, and JetBrains AI Assistant."},
        {"title": "JetBrains Privacy Policy", "url": "https://www.jetbrains.com/legal/docs/privacy/privacy/", "snippet": "Details IDE feature usage telemetry, crash logs, and AI completion prompt handling."},
    ],

    # ---------------------------------------------------------
    # 14. News, Journalism & Knowledge
    # ---------------------------------------------------------
    "nytimes": [
        {"title": "The New York Times Terms of Service", "url": "https://help.nytimes.com/hc/en-us/articles/115014893428-Terms-of-Service", "snippet": "Governs digital news subscriptions, NYT Cooking, Games (Wordle), and Audio apps."},
        {"title": "The New York Times Privacy Policy", "url": "https://help.nytimes.com/hc/en-us/articles/115014892108-Privacy-policy", "snippet": "Covers reader article engagement metrics, newsletter tracking, and targeted advertising."},
    ],
    "washingtonpost": [
        {"title": "The Washington Post Terms of Service", "url": "https://www.washingtonpost.com/terms-of-service/2021/11/02/terms-of-service/", "snippet": "Governs news subscription agreements, digital paywalls, and subscriber discussion forums."},
        {"title": "The Washington Post Privacy Policy", "url": "https://www.washingtonpost.com/privacy-policy/2021/11/02/privacy-policy/", "snippet": "Details subscriber reading histories, browser telemetry, and ad targeting."},
    ],
    "wsj": [
        {"title": "The Wall Street Journal Subscriber Agreement", "url": "https://www.dowjones.com/terms-of-use/", "snippet": "Governs Dow Jones financial reporting, market data access, and annual print/digital subscriptions."},
        {"title": "Dow Jones Privacy Notice", "url": "https://www.dowjones.com/privacy-notice/", "snippet": "Covers financial reader demographics, article readership telemetry, and corporate accounts."},
    ],
    "bbc": [
        {"title": "BBC Terms of Use", "url": "https://www.bbc.com/usingthebbc/terms/", "snippet": "Governs global BBC online content, iPlayer streaming outside the UK, and BBC News services."},
        {"title": "BBC Privacy Policy", "url": "https://www.bbc.com/usingthebbc/privacy/", "snippet": "Details public broadcasting telemetry, BBC account preferences, and international cookies."},
    ],
    "cnn": [
        {"title": "CNN Terms of Use", "url": "https://www.cnn.com/terms", "snippet": "Governs digital news broadcasts, live video feeds, mobile apps, and Warner Bros. Discovery terms."},
        {"title": "CNN Privacy Policy", "url": "https://www.cnn.com/privacy", "snippet": "Covers video viewership telemetry, digital ad measurement, and mobile device analytics."},
    ],
    "bloomberg": [
        {"title": "Bloomberg Terms of Service", "url": "https://www.bloomberg.com/notices/tos/", "snippet": "Governs Bloomberg.com news subscriptions, market indices display, and multimedia content."},
        {"title": "Bloomberg Privacy Policy", "url": "https://www.bloomberg.com/notices/privacy/", "snippet": "Details market interest telemetry, reader subscription records, and business disclosures."},
    ],
    "reuters": [
        {"title": "Reuters Terms of Use", "url": "https://www.reuters.com/info/terms-of-use", "snippet": "Governs international wire journalism, financial news feeds, and subscriber accounts."},
        {"title": "Reuters Privacy Notice", "url": "https://www.reuters.com/info/privacy-policy", "snippet": "Details reader engagement telemetry, newsletter subscriptions, and corporate compliance."},
    ],
    "theguardian": [
        {"title": "The Guardian Terms of Service", "url": "https://www.theguardian.com/help/terms-of-service", "snippet": "Governs open-access journalism, voluntary supporter contributions, and reader comments."},
        {"title": "The Guardian Privacy Policy", "url": "https://www.theguardian.com/help/privacy-policy", "snippet": "Covers supporter payment details, reader reading histories, and strict cookie controls."},
    ],

    # ---------------------------------------------------------
    # 15. Telecommunications & Connectivity Providers
    # ---------------------------------------------------------
    "att": [
        {"title": "AT&T Consumer Service Agreement", "url": "https://www.att.com/legal/terms.consumerServiceAgreement.html", "snippet": "Governs wireless mobile plans, fiber broadband, equipment leases, and mandatory arbitration."},
        {"title": "AT&T Privacy Notice", "url": "https://about.att.com/privacy/privacy-policy.html", "snippet": "Details cell tower location telemetry, DNS query records, and broadband bandwidth usage."},
    ],
    "verizon": [
        {"title": "Verizon Customer Agreement", "url": "https://www.verizon.com/support/customer-agreement/", "snippet": "Governs cellular contracts, 5G Ultra Wideband access, Fios home internet, and device financing."},
        {"title": "Verizon Privacy Policy", "url": "https://www.verizon.com/about/privacy/full-privacy-policy", "snippet": "Covers mobile network diagnostics, CPNI telecommunications records, and location tracking."},
    ],
    "tmobile": [
        {"title": "T-Mobile Terms and Conditions", "url": "https://www.t-mobile.com/responsibility/legal/terms-and-conditions", "snippet": "Governs cellular plans, Magenta perks, 5G Home Internet, and arbitration waivers."},
        {"title": "T-Mobile Privacy Notice", "url": "https://www.t-mobile.com/privacy-center/privacy-notices/t-mobile-privacy-notice", "snippet": "Details network diagnostic telemetry, cell site location info (CSLI), and fraud prevention."},
    ],
    "comcast": [
        {"title": "Xfinity Customer Agreement", "url": "https://www.xfinity.com/corporate/customers/policies/subscriberagreement", "snippet": "Governs residential Xfinity cable TV, gigabit home broadband, and gateway equipment rentals."},
        {"title": "Comcast Customer Privacy Notice", "url": "https://www.xfinity.com/corporate/customers/policies/customerprivacy", "snippet": "Covers internet traffic routing telemetry, set-top box viewing history, and broadband metrics."},
    ],
    "starlink": [
        {"title": "Starlink Terms of Service", "url": "https://www.starlink.com/legal/documents/DOC-1020-91087-64", "snippet": "Governs SpaceX low Earth orbit satellite internet terminals, data priority caps, and mobility."},
        {"title": "Starlink Privacy Policy", "url": "https://www.starlink.com/legal/documents/DOC-1021-41916-65", "snippet": "Details dish GPS antenna telemetry, satellite constellation routing logs, and data usage."},
    ],

    # ---------------------------------------------------------
    # 13. E-Commerce, Quick-Commerce & Retail Delivery
    # ---------------------------------------------------------
    "flipkart": [
        {"title": "Flipkart Terms of Use", "url": "https://www.flipkart.com/pages/terms", "snippet": "Covers marketplace transactions, seller dispute resolution, refund timelines, and consumer accounts."},
        {"title": "Flipkart Privacy Policy", "url": "https://www.flipkart.com/pages/privacypolicy", "snippet": "Details consumer order history tracking, payment telemetry, and personalized recommendations."},
    ],
    "meesho": [
        {"title": "Meesho User Terms of Service", "url": "https://www.meesho.com/legal/terms-conditions", "snippet": "Governs reseller marketplace access, social commerce transactions, and dispute handling."},
        {"title": "Meesho Privacy Policy", "url": "https://www.meesho.com/legal/privacy", "snippet": "Details social commerce data gathering, address book telemetry, and order fulfillment tracking."},
    ],
    "swiggy": [
        {"title": "Swiggy Terms of Use", "url": "https://www.swiggy.com/terms-and-conditions", "snippet": "Governs on-demand food delivery ordering, merchant pricing, cancellation fees, and Instamart quick commerce."},
        {"title": "Swiggy Privacy Policy", "url": "https://www.swiggy.com/privacy-policy", "snippet": "Details delivery GPS location tracking, order preference analytics, and payment gateway interactions."},
    ],
    "instamart": [
        {"title": "Swiggy Instamart Terms & Conditions", "url": "https://www.swiggy.com/terms-and-conditions", "snippet": "Covers quick commerce grocery fulfillment, delivery SLA terms, and return/refund guidelines."},
        {"title": "Swiggy Instamart Privacy Policy", "url": "https://www.swiggy.com/privacy-policy", "snippet": "Outlines grocery order history logging, real-time courier telemetry, and user preferences."},
    ],
    "blinkit": [
        {"title": "Blinkit Terms of Service", "url": "https://blinkit.com/terms", "snippet": "Governs ultra-fast grocery delivery, dark store fulfillment, order cancellation, and account policies."},
        {"title": "Blinkit Privacy Policy", "url": "https://blinkit.com/privacy", "snippet": "Details delivery address telemetry, device identifiers, and quick-commerce transaction profiling."},
    ],
    "zepto": [
        {"title": "Zepto Terms and Conditions", "url": "https://www.zeptonow.com/terms-and-conditions", "snippet": "Covers 10-minute grocery delivery, platform wallet credits, product replacements, and acceptable use."},
        {"title": "Zepto Privacy Policy", "url": "https://www.zeptonow.com/privacy-policy", "snippet": "Explains consumer location telemetry, order frequencies, and partner advertising metrics."},
    ],
    "bigbasket": [
        {"title": "BigBasket Terms of Use", "url": "https://www.bigbasket.com/terms-and-conditions/", "snippet": "Governs scheduled grocery delivery, bbdaily subscriptions, wallet balances, and returns."},
        {"title": "BigBasket Privacy Policy", "url": "https://www.bigbasket.com/privacy-policy/", "snippet": "Details household grocery buying patterns, address telemetry, and payment security measures."},
    ],
    "snapdeal": [
        {"title": "Snapdeal Terms of Sale and Use", "url": "https://www.snapdeal.com/page/terms-of-sale", "snippet": "Covers value retail e-commerce purchases, third-party vendor listings, and returns."},
        {"title": "Snapdeal Privacy Policy", "url": "https://www.snapdeal.com/page/privacy-policy", "snippet": "Explains user search telemetry, browsing history, and seller notification preferences."},
    ],
    "toing": [
        {"title": "Toing Terms and Conditions", "url": "https://toing.in/terms-and-conditions", "snippet": "Governs on-demand retail commerce ordering, account verification, and transaction policies."},
        {"title": "Toing Privacy Policy", "url": "https://toing.in/privacy-policy", "snippet": "Details user registration data, device telemetry, and order dispatch location logs."},
    ],
    "ownly": [
        {"title": "Ownly Terms of Service", "url": "https://ownly.in/terms", "snippet": "Governs digital commerce services, consumer account rights, and platform transactions."},
        {"title": "Ownly Privacy Policy", "url": "https://ownly.in/privacy-policy", "snippet": "Covers customer data protection, profile telemetry, and order analytics."},
    ],
    "jiomart": [
        {"title": "JioMart Terms and Conditions", "url": "https://www.jiomart.com/terms-and-conditions", "snippet": "Governs omni-channel retail purchases, Kirana partner deliveries, and Reliance Retail orders."},
        {"title": "JioMart Privacy Policy", "url": "https://www.jiomart.com/privacy-policy", "snippet": "Covers retail ecosystem customer profiles, purchase history, and targeted promotions."},
    ],
    "ajio": [
        {"title": "AJIO Terms and Conditions", "url": "https://www.ajio.com/terms-and-conditions", "snippet": "Governs fashion and apparel e-commerce sales, AJIO Wallet points, exchanges, and doorstep returns."},
        {"title": "AJIO Privacy Policy", "url": "https://www.ajio.com/privacypolicy", "snippet": "Details style preference tracking, sizing telemetry, and payment verification logs."},
    ],
    "nykaa": [
        {"title": "Nykaa Terms and Conditions", "url": "https://www.nykaa.com/terms-conditions", "snippet": "Governs beauty and wellness e-commerce purchases, Nykaa Prive rewards, and authentic product guarantees."},
        {"title": "Nykaa Privacy Policy", "url": "https://www.nykaa.com/privacy-policy", "snippet": "Explains skincare diagnostic profiling, browsing cookies, and order fulfillment analytics."},
    ],
    "tatacliq": [
        {"title": "Tata CLiQ Terms of Use", "url": "https://www.tatacliq.com/terms-of-use", "snippet": "Governs brand certified electronics and luxury fashion purchases, Tata Neu integration, and returns."},
        {"title": "Tata CLiQ Privacy Policy", "url": "https://www.tatacliq.com/privacy-policy", "snippet": "Outlines customer profiling across digital ecosystem services, fraud checks, and telemetry."},
    ],

    # ---------------------------------------------------------
    # 14. Entertainment, Media & Streaming Platforms
    # ---------------------------------------------------------
    "jiohotstar": [
        {"title": "JioHotstar / Hotstar Terms of Use", "url": "https://www.hotstar.com/terms-of-use", "snippet": "Governs live sports streaming, on-demand entertainment licenses, subscription tiers, and DRM."},
        {"title": "Hotstar Privacy Policy", "url": "https://www.hotstar.com/privacy-policy", "snippet": "Details live streaming viewing telemetry, device identifiers, and targeted video advertising."},
    ],
    "jiocinema": [
        {"title": "JioCinema Terms of Use", "url": "https://www.jiocinema.com/terms-and-conditions", "snippet": "Governs digital media streaming, premium ad-free tiers, live sports broadcast access, and DRM."},
        {"title": "JioCinema Privacy Policy", "url": "https://www.jiocinema.com/privacy-policy", "snippet": "Details streaming telemetry, viewer recommendation logs, and device hardware fingerprints."},
    ],
    "crunchyroll": [
        {"title": "Crunchyroll Terms of Service", "url": "https://www.crunchyroll.com/terms/index.html", "snippet": "Governs anime video streaming, simulcasts, fan community forums, and premium subscriptions."},
        {"title": "Crunchyroll Privacy Policy", "url": "https://www.crunchyroll.com/privacy/index.html", "snippet": "Details watch history telemetry, manga reading tracking, and subscription billing analytics."},
    ],
    "sonyliv": [
        {"title": "Sony LIV Terms of Use", "url": "https://www.sonyliv.com/terms-of-use", "snippet": "Governs digital video streaming subscriptions, sports broadcast licenses, and simultaneous screens."},
        {"title": "Sony LIV Privacy Policy", "url": "https://www.sonyliv.com/privacy-policy", "snippet": "Covers viewer telemetry, device profile logging, and personalized content recommendations."},
    ],
    "zee5": [
        {"title": "ZEE5 Terms of Use", "url": "https://www.zee5.com/termsofuse", "snippet": "Governs on-demand multilingual streaming content, premium renewals, and playback device limits."},
        {"title": "ZEE5 Privacy Policy", "url": "https://www.zee5.com/privacypolicy", "snippet": "Details regional language preferences, content consumption telemetry, and ad metrics."},
    ],
    "primevideo": [
        {"title": "Amazon Prime Video Terms of Use", "url": "https://www.primevideo.com/help?nodeId=202064890", "snippet": "Governs digital video streaming, rented content windows, 4K HDR playback, and Amazon Prime benefits."},
        {"title": "Amazon Prime Video Privacy Notice", "url": "https://www.amazon.com/gp/help/customer/display.html?nodeId=468496", "snippet": "Details Prime viewing analytics, device telemetry, and household profile sharing."},
    ],

    # ---------------------------------------------------------
    # 15. Telecommunications & Cellular Networks
    # ---------------------------------------------------------
    "jio": [
        {"title": "Reliance Jio Terms and Conditions", "url": "https://www.jio.com/en-in/terms-and-conditions", "snippet": "Governs 5G and 4G LTE cellular services, JioFiber home broadband, eSIM provisioning, and prepaid validity."},
        {"title": "Reliance Jio Privacy Policy", "url": "https://www.jio.com/en-in/privacy-policy", "snippet": "Explains telecommunication network diagnostics, cell tower connection logs, and digital ecosystem services."},
    ],
    "airtel": [
        {"title": "Bharti Airtel Terms and Conditions", "url": "https://www.airtel.in/terms-conditions/", "snippet": "Governs mobile postpaid and prepaid telecom services, Airtel Xstream fiber, and DTH connections."},
        {"title": "Bharti Airtel Privacy Policy", "url": "https://www.airtel.in/privacy-policy", "snippet": "Covers telecom regulatory compliance data, billing telemetry, and network traffic quality metrics."},
    ],
    "vi": [
        {"title": "Vodafone Idea (Vi) Terms and Conditions", "url": "https://www.myvi.in/terms-and-conditions", "snippet": "Governs cellular voice and data plans, Vi Movies & TV app integration, and SIM card management."},
        {"title": "Vodafone Idea (Vi) Privacy Policy", "url": "https://www.myvi.in/privacy-policy", "snippet": "Details telecom call detail records (CDR), cellular telemetry, and customer care records."},
    ],

    # ---------------------------------------------------------
    # 16. Fintech, Payments, Investment & Ride-Hailing
    # ---------------------------------------------------------
    "phonepe": [
        {"title": "PhonePe Terms and Conditions", "url": "https://www.phonepe.com/terms-conditions/", "snippet": "Governs UPI peer-to-peer payments, merchant QR transactions, PhonePe Wallet, and recharge services."},
        {"title": "PhonePe Privacy Policy", "url": "https://www.phonepe.com/privacy-policy/", "snippet": "Details UPI financial telemetry, device binding security, and transactional record retention."},
    ],
    "paytm": [
        {"title": "Paytm Terms and Conditions", "url": "https://paytm.com/terms-and-conditions", "snippet": "Governs digital wallet transactions, UPI payments, soundbox merchant services, and ticketing."},
        {"title": "Paytm Privacy Policy", "url": "https://paytm.com/privacy-policy", "snippet": "Details financial transaction auditing, KYC identity verification logs, and device security telemetry."},
    ],
    "cred": [
        {"title": "CRED Terms of Service", "url": "https://cred.club/terms", "snippet": "Governs credit card bill payment management, CRED reward coins, peer payments, and lending products."},
        {"title": "CRED Privacy Policy", "url": "https://cred.club/privacy", "snippet": "Details credit bureau score access permissions, email bill parsing consent, and transaction security."},
    ],
    "groww": [
        {"title": "Groww Terms and Conditions", "url": "https://groww.in/terms-and-conditions", "snippet": "Governs stock brokerage, direct mutual fund investing, demat account opening, and F&O trading."},
        {"title": "Groww Privacy Policy", "url": "https://groww.in/privacy-policy", "snippet": "Details financial KYC record storage, depository participant telemetry, and regulatory reporting."},
    ],
    "zerodha": [
        {"title": "Zerodha Terms and Conditions", "url": "https://zerodha.com/terms-and-conditions/", "snippet": "Governs Kite trading platform access, discount brokerage execution, demat services, and Coin funds."},
        {"title": "Zerodha Privacy Policy", "url": "https://zerodha.com/privacy-policy/", "snippet": "Outlines securities regulatory trade auditing, account telemetry, and encrypted session security."},
    ],
    "ola": [
        {"title": "Ola Consumer Terms and Conditions", "url": "https://www.olacabs.com/info/faqs#termsAndConditions", "snippet": "Governs ride-hailing services, driver allocations, peak pricing fares, and Ola Money integration."},
        {"title": "Ola Privacy Policy", "url": "https://www.olacabs.com/info/faqs#privacyPolicy", "snippet": "Details real-time GPS ride telemetry, pickup location tracking, and driver rating feedback logs."},
    ],
    "makemytrip": [
        {"title": "MakeMyTrip User Agreement", "url": "https://www.makemytrip.com/legal/user_agreement.html", "snippet": "Governs flight bookings, hotel reservations, holiday packages, cancellation charges, and refunds."},
        {"title": "MakeMyTrip Privacy Policy", "url": "https://www.makemytrip.com/legal/privacy_policy.html", "snippet": "Details traveler identity passport telemetry, booking preferences, and airline partner data sharing."},
    ],

    # ---------------------------------------------------------
    # 17. Expanded Gaming Studios, Publishers, Platforms & Engines
    # ---------------------------------------------------------
    "rockstargames": [
        {"title": "Rockstar Games / Take-Two Terms of Service", "url": "https://www.take2games.com/legal/", "snippet": "Governs Grand Theft Auto (GTA), GTA Online, Red Dead Redemption, Rockstar Games, and Take-Two services."},
        {"title": "Rockstar Games / Take-Two Privacy Policy", "url": "https://www.take2games.com/privacy/", "snippet": "Details Rockstar Games and Take-Two Interactive account telemetry, anti-cheat logs, and privacy rights."},
    ],
    "taketwo": [
        {"title": "Take-Two Interactive Terms of Service", "url": "https://www.take2games.com/legal/", "snippet": "Parent publisher terms covering Rockstar Games, 2K, Zynga, virtual currencies, and user-generated content."},
        {"title": "Take-Two Interactive Privacy Policy", "url": "https://www.take2games.com/privacy/", "snippet": "Details cross-title player telemetry, anti-cheat enforcement, and marketing disclosures."},
    ],
    "2kgames": [
        {"title": "2K Games Terms of Service", "url": "https://www.take2games.com/legal/", "snippet": "Governs NBA 2K, Civilization, Borderlands, BioShock, and virtual currency (VC) purchases."},
        {"title": "2K Games Privacy Policy", "url": "https://www.take2games.com/privacy/", "snippet": "Covers player matchmaking telemetry, MyPLAYER profiles, and Take-Two account data."},
    ],
    "activision": [
        {"title": "Activision Terms of Use", "url": "https://www.activision.com/legal/terms-of-use", "snippet": "Governs Call of Duty, Warzone, RICOCHET anti-cheat, COD Points, and multiplayer conduct."},
        {"title": "Activision Privacy Policy", "url": "https://www.activision.com/legal/privacy-policy", "snippet": "Details gameplay telemetry, voice chat moderation, anti-cheat kernel drivers, and platform linking."},
    ],
    "bethesda": [
        {"title": "ZeniMax / Bethesda Terms of Service", "url": "https://www.zenimax.com/en/legal/terms-of-service", "snippet": "Governs Elder Scrolls, Fallout, Starfield, DOOM, Creation Club mods, and Bethesda.net accounts."},
        {"title": "ZeniMax / Bethesda Privacy Policy", "url": "https://www.zenimax.com/en/legal/privacy-policy", "snippet": "Details game telemetry, mod marketplace purchases, and Microsoft gaming integration."},
    ],
    "cdprojektred": [
        {"title": "CD PROJEKT RED User Agreement", "url": "https://regulations.cdprojektred.com/en/user_agreement", "snippet": "Governs Cyberpunk 2077, The Witcher series, GWENT, REDmod tools, and fan content guidelines."},
        {"title": "CD PROJEKT RED Privacy Policy", "url": "https://regulations.cdprojektred.com/en/privacy_policy", "snippet": "Covers crash telemetry, cross-progression cloud saves, and account preferences."},
    ],
    "gog": [
        {"title": "GOG User Agreement", "url": "https://support.gog.com/hc/en-us/articles/212632089-GOG-User-Agreement", "snippet": "Governs DRM-free PC game purchases, GOG Galaxy client, and 30-day refund policies."},
        {"title": "GOG Privacy Policy", "url": "https://support.gog.com/hc/en-us/articles/212632109-Privacy-Policy", "snippet": "Details store transaction records, GOG Galaxy cross-platform telemetry, and account security."},
    ],
    "squareenix": [
        {"title": "Square Enix Terms of Use", "url": "https://www.square-enix-games.com/en_US/documents/tnc", "snippet": "Governs Final Fantasy XIV, Dragon Quest, Kingdom Hearts, and Square Enix Members accounts."},
        {"title": "Square Enix Privacy Notice", "url": "https://www.square-enix-games.com/en_US/documents/privacy", "snippet": "Covers MMO subscription records, telemetry, and regional service disclosures."},
    ],
    "capcom": [
        {"title": "Capcom USA Terms of Use", "url": "https://www.capcomusa.com/terms/", "snippet": "Governs Resident Evil, Monster Hunter, Street Fighter, and Capcom online services."},
        {"title": "Capcom Privacy Policy", "url": "https://www.capcomusa.com/privacy/", "snippet": "Details multiplayer matchmaking logs, telemetry, and global player account records."},
    ],
    "bandainamco": [
        {"title": "Bandai Namco Terms of Service", "url": "https://www.bandainamcoent.com/legal/terms", "snippet": "Governs Elden Ring, Tekken, Dragon Ball games, and Bandai Namco ID online services."},
        {"title": "Bandai Namco Privacy Policy", "url": "https://www.bandainamcoent.com/legal/privacy", "snippet": "Covers online multiplayer logs, store orders, and customer telemetry."},
    ],
    "sega": [
        {"title": "SEGA Privacy Policy & Games Hub", "url": "https://privacy.sega.com/en/our-games", "snippet": "Covers Sonic, Yakuza / Like a Dragon, Persona / Atlus, Total War, and SEGA accounts."},
    ],
    "konami": [
        {"title": "KONAMI Privacy Policy", "url": "https://legal.konami.com/knm/privacy/en-intl/", "snippet": "Covers eFootball, Yu-Gi-Oh! Master Duel, Metal Gear, Silent Hill, and KONAMI ID telemetry."},
    ],
    "xbox": [
        {"title": "Microsoft Services Agreement (Xbox)", "url": "https://www.microsoft.com/en-us/servicesagreement", "snippet": "Governs Xbox Network, Xbox Game Pass, Xbox Cloud Gaming, and console digital purchases."},
        {"title": "Xbox & Microsoft Privacy Statement", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Covers Xbox Live voice/chat safety logs, achievement telemetry, and cloud save syncing."},
    ],
    "krafton": [
        {"title": "KRAFTON Privacy Policy", "url": "https://www.krafton.com/en/privacy-policy/", "snippet": "Covers PUBG: BATTLEGROUNDS, PUBG Mobile, inZOI, anti-cheat telemetry, and player account security."},
    ],
    "supercell": [
        {"title": "Supercell Terms of Service", "url": "https://supercell.com/en/terms-of-service/", "snippet": "Governs Clash of Clans, Clash Royale, Brawl Stars, and Supercell ID virtual items."},
        {"title": "Supercell Privacy Policy", "url": "https://supercell.com/en/privacy-policy/", "snippet": "Covers clan chat moderation, device identifiers, and fair-play account enforcement."},
    ],
    "minecraft": [
        {"title": "Minecraft End User License Agreement", "url": "https://www.minecraft.net/en-us/eula", "snippet": "Governs Minecraft Java & Bedrock Editions, Realms subscriptions, Marketplace, and server monetization."},
        {"title": "Microsoft Privacy Statement (Minecraft)", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Covers Xbox/Microsoft account authentication, Realms telemetry, and player safety reporting."},
    ],
    "paradox": [
        {"title": "Paradox Interactive EULA & Terms", "url": "https://legal.paradoxplaza.com/eula", "snippet": "Governs Stellaris, Hearts of Iron, Crusader Kings, Cities: Skylines, and Paradox Mods."},
        {"title": "Paradox Interactive Privacy Policy", "url": "https://legal.paradoxplaza.com/privacy", "snippet": "Covers launcher telemetry, mod downloads, and multiplayer account records."},
    ],
    "larian": [
        {"title": "Larian Studios Privacy Policy", "url": "https://larian.com/privacy", "snippet": "Covers Baldur's Gate 3 and Divinity crash diagnostics, cross-save telemetry, and analytics."},
        {"title": "Larian Studios Fan Content Policy", "url": "https://larian.com/fan-content-policy", "snippet": "Governs fan creations, streaming, mods, and community content guidelines."},
    ],
    "facepunch": [
        {"title": "Facepunch Studios Terms of Service", "url": "https://facepunch.com/legal/tos", "snippet": "Governs Rust, Garry's Mod, s&box, Easy Anti-Cheat enforcement, and community servers."},
        {"title": "Facepunch Studios Privacy Policy", "url": "https://facepunch.com/legal/privacy", "snippet": "Details SteamID linking, server ban logs, and crash reporting."},
    ],
    "wargaming": [
        {"title": "Wargaming End User License Agreement", "url": "https://legal.na.wargaming.net/en/eula", "snippet": "Governs World of Tanks, World of Warships, Wargaming.net ID, and premium vehicles."},
        {"title": "Wargaming Privacy Policy", "url": "https://legal.na.wargaming.net/en/privacy-policy", "snippet": "Details battle replay telemetry, anti-cheat monitoring, and clan records."},
    ],
    "gaijin": [
        {"title": "Gaijin Entertainment Terms of Use", "url": "https://legal.gaijin.net/termsofservice", "snippet": "Governs War Thunder, Enlisted, Crossout, Gaijin Market, and Golden Eagles."},
        {"title": "Gaijin Entertainment Privacy Policy", "url": "https://legal.gaijin.net/privacypolicy", "snippet": "Covers battle telemetry, EAC anti-cheat checks, and marketplace transactions."},
    ],
    "unrealengine": [
        {"title": "Unreal Engine End User License Agreement", "url": "https://www.unrealengine.com/en-US/eula/unreal", "snippet": "Governs Unreal Engine 5 commercial royalties, Fab marketplace assets, and Epic developer terms."},
        {"title": "Epic Games Privacy Policy", "url": "https://www.epicgames.com/site/en-US/privacypolicy", "snippet": "Covers engine crash telemetry, developer account billing, and marketplace metrics."},
    ],
    "godot": [
        {"title": "Godot Engine License & Legal", "url": "https://godotengine.org/license/", "snippet": "MIT open-source licensing for Godot Engine and asset distribution guidelines."},
        {"title": "Godot Foundation Privacy Policy", "url": "https://godotengine.org/privacy-policy/", "snippet": "Covers Godot Asset Library, website analytics, and contributor account privacy."},
    ],
    "itchio": [
        {"title": "itch.io Terms of Service", "url": "https://itch.io/docs/legal/terms", "snippet": "Governs indie game hosting, pay-what-you-want payouts, game jams, and creator pages."},
        {"title": "itch.io Privacy Policy", "url": "https://itch.io/docs/legal/privacy-policy", "snippet": "Covers buyer download receipts, creator payout verification, and minimal cookies."},
    ],
    "nexusmods": [
        {"title": "Nexus Mods Terms of Service", "url": "https://help.nexusmods.com/article/18-terms-of-service", "snippet": "Governs PC game mod hosting, Vortex mod manager, Donation Points, and moderation."},
        {"title": "Nexus Mods Privacy Policy", "url": "https://help.nexusmods.com/article/20-privacy-policy", "snippet": "Details download telemetry, supporter billing, and community forum logs."},
    ],
    "curseforge": [
        {"title": "Overwolf & CurseForge Terms of Service", "url": "https://www.overwolf.com/legal/terms", "snippet": "Governs CurseForge mod repositories (Minecraft, WoW), desktop client, and creator rewards."},
        {"title": "Overwolf & CurseForge Privacy Policy", "url": "https://www.overwolf.com/legal/privacy", "snippet": "Details mod manager telemetry, in-app ads, and developer analytics."},
    ],
    "kick": [
        {"title": "Kick Terms of Service", "url": "https://kick.com/terms-of-service", "snippet": "Governs live video streaming, 95/5 creator subscription splits, and community guidelines."},
        {"title": "Kick Privacy Policy", "url": "https://kick.com/privacy-policy", "snippet": "Covers livestream viewership logs, chat messages, and creator payout verification."},
    ],
    "chesscom": [
        {"title": "Chess.com User Agreement", "url": "https://www.chess.com/legal/user-agreement", "snippet": "Governs online chess games, ELO ratings, fair play anti-cheating, and Diamond memberships."},
        {"title": "Chess.com Privacy Policy", "url": "https://www.chess.com/legal/privacy", "snippet": "Covers game move telemetry, fair-play detection signals, and community messages."},
    ],
    "lichess": [
        {"title": "Lichess Terms of Service", "url": "https://lichess.org/terms-of-service", "snippet": "Non-profit open-source chess server rules, fair play enforcement, and user conduct."},
        {"title": "Lichess Privacy Policy", "url": "https://lichess.org/privacy", "snippet": "Details ad-free, tracker-free operation and game archive retention."},
    ],
    "geforcenow": [
        {"title": "NVIDIA GeForce NOW Terms of Use", "url": "https://www.nvidia.com/en-us/geforce-now/terms-of-use/", "snippet": "Governs cloud game streaming, session time limits, RTX tier billing, and store linking."},
        {"title": "NVIDIA Privacy Policy", "url": "https://www.nvidia.com/en-us/about-nvidia/privacy-policy/", "snippet": "Covers cloud GPU stream telemetry, linked Steam/Epic libraries, and latency diagnostics."},
    ],

    # ---------------------------------------------------------
    # 18. Expanded AI Labs, Coding Agents & ML Infrastructure
    # ---------------------------------------------------------
    "xai": [
        {"title": "xAI Terms of Service", "url": "https://x.ai/legal/terms-of-service", "snippet": "Governs Grok AI assistant, xAI API endpoints, Aurora image generation, and acceptable use."},
        {"title": "xAI Privacy Policy", "url": "https://x.ai/legal/privacy-policy", "snippet": "Details prompt/output retention, X platform integration, and model training opt-outs."},
    ],
    "deepseek": [
        {"title": "DeepSeek Terms of Use", "url": "https://cdn.deepseek.com/policies/en-US/deepseek-terms-of-use.html", "snippet": "Governs DeepSeek Chat, DeepSeek-R1/V3 APIs, and open-weight licensing boundaries."},
        {"title": "DeepSeek Privacy Policy", "url": "https://cdn.deepseek.com/policies/en-US/deepseek-privacy-policy.html", "snippet": "Details conversation storage, keystroke/device telemetry, and cross-border PRC data servers."},
    ],
    "qwen": [
        {"title": "Alibaba Cloud Qwen Terms of Service", "url": "https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-international-website-product-terms-of-service", "snippet": "Governs Qwen AI web chat, Model Studio APIs, and commercial cloud inference."},
        {"title": "Alibaba Cloud Privacy Policy", "url": "https://www.alibabacloud.com/help/en/legal/latest/alibaba-cloud-international-website-privacy-policy", "snippet": "Covers API payload retention, cloud tenant isolation, and international compliance."},
    ],
    "inflection": [
        {"title": "Inflection AI / Pi Terms of Service", "url": "https://inflection.ai/terms-of-service", "snippet": "Governs Pi personal AI companion, voice interactions, and acceptable use."},
        {"title": "Inflection AI Privacy Policy", "url": "https://inflection.ai/privacy-policy", "snippet": "Covers conversational memory, voice audio handling, and safety moderation."},
    ],
    "poe": [
        {"title": "Poe (Quora) Terms of Service", "url": "https://poe.com/tos", "snippet": "Governs multi-model AI chat subscriptions, custom bot creators, and compute points."},
        {"title": "Poe Privacy Policy", "url": "https://poe.com/privacy", "snippet": "Details third-party LLM provider routing, chat histories, and creator monetization."},
    ],
    "windsurf": [
        {"title": "Windsurf (Codeium) Terms of Service", "url": "https://windsurf.com/terms-of-service", "snippet": "Governs Windsurf AI IDE, Cascade agentic coding, and enterprise autocomplete seats."},
        {"title": "Windsurf Privacy Policy", "url": "https://windsurf.com/privacy-policy", "snippet": "Details zero-data-retention modes, codebase indexing telemetry, and snippet encryption."},
    ],
    "replit": [
        {"title": "Replit Terms of Service", "url": "https://replit.com/site/terms", "snippet": "Governs cloud IDEs, Replit Agent app generation, Deployments, and private Repls."},
        {"title": "Replit Privacy Policy", "url": "https://replit.com/site/privacy", "snippet": "Covers workspace source code visibility, AI training opt-outs, and billing records."},
    ],
    "stackblitz": [
        {"title": "StackBlitz & Bolt.new Terms of Service", "url": "https://stackblitz.com/terms-of-service", "snippet": "Governs WebContainers browser IDEs, Bolt.new AI app builder, and token quotas."},
        {"title": "StackBlitz Privacy Policy", "url": "https://stackblitz.com/privacy-policy", "snippet": "Details project code privacy, OAuth tokens, and runtime telemetry."},
    ],
    "lovable": [
        {"title": "Lovable Terms of Service", "url": "https://lovable.dev/terms", "snippet": "Governs AI full-stack app generation, GitHub syncing, and generated code ownership."},
        {"title": "Lovable Privacy Policy", "url": "https://lovable.dev/privacy", "snippet": "Covers prompt retention, Supabase project integrations, and usage telemetry."},
    ],
    "cognition": [
        {"title": "Cognition (Devin) Terms of Service", "url": "https://cognition.ai/terms", "snippet": "Governs Devin autonomous AI software engineer, ACU usage, and enterprise sandboxes."},
        {"title": "Cognition Privacy Policy", "url": "https://cognition.ai/privacy", "snippet": "Details repository access isolation, agent execution logs, and customer data retention."},
    ],
    "sourcegraph": [
        {"title": "Sourcegraph & Cody Terms of Service", "url": "https://sourcegraph.com/terms", "snippet": "Governs enterprise code search, Cody AI coding assistant, and self-hosted licenses."},
        {"title": "Sourcegraph Privacy Policy", "url": "https://sourcegraph.com/terms/privacy", "snippet": "Details codebase context transmission, zero-retention LLM routing, and telemetry."},
    ],
    "togetherai": [
        {"title": "Together AI Terms of Service", "url": "https://www.together.ai/terms-of-service", "snippet": "Governs serverless open-model inference, dedicated GPU clusters, and fine-tuning jobs."},
        {"title": "Together AI Privacy Policy", "url": "https://www.together.ai/privacy", "snippet": "Covers API request retention, fine-tuned weights confidentiality, and SOC 2 controls."},
    ],
    "groq": [
        {"title": "GroqCloud Terms of Service", "url": "https://groq.com/terms-of-use/", "snippet": "Governs LPU ultra-low-latency LLM inference APIs, rate limits, and commercial use."},
        {"title": "Groq Privacy Policy", "url": "https://groq.com/privacy-policy/", "snippet": "Details API prompt ephemerality, zero-retention guarantees, and diagnostic metrics."},
    ],
    "fireworksai": [
        {"title": "Fireworks AI Terms of Service", "url": "https://fireworks.ai/terms-of-service", "snippet": "Governs FireAttention inference APIs, custom LoRA fine-tuning, and batch processing."},
        {"title": "Fireworks AI Privacy Policy", "url": "https://fireworks.ai/privacy-policy", "snippet": "Covers enterprise zero-data-retention policies, model deployment logs, and billing."},
    ],
    "openrouter": [
        {"title": "OpenRouter Terms of Service", "url": "https://openrouter.ai/terms", "snippet": "Governs unified LLM API routing, prepaid credits, and upstream model provider terms."},
        {"title": "OpenRouter Privacy Policy", "url": "https://openrouter.ai/privacy", "snippet": "Details ZDR (Zero Data Retention) routing flags, prompt logging opt-outs, and billing."},
    ],
    "falai": [
        {"title": "fal.ai Terms of Service", "url": "https://fal.ai/terms", "snippet": "Governs serverless generative media APIs (Flux, video/audio models) and GPU billing."},
        {"title": "fal.ai Privacy Policy", "url": "https://fal.ai/privacy", "snippet": "Covers generated media CDN retention, API payload logs, and account metadata."},
    ],
    "modal": [
        {"title": "Modal Terms of Service", "url": "https://modal.com/legal/terms", "snippet": "Governs serverless Python cloud containers, on-demand GPUs, and compute billing."},
        {"title": "Modal Privacy Policy", "url": "https://modal.com/legal/privacy-policy", "snippet": "Covers container image storage, function logs, and customer secret encryption."},
    ],
    "cerebras": [
        {"title": "Cerebras Systems Terms of Service", "url": "https://www.cerebras.ai/terms-of-service", "snippet": "Governs Wafer-Scale Engine cloud inference APIs, enterprise clusters, and SLAs."},
        {"title": "Cerebras Privacy Policy", "url": "https://www.cerebras.ai/privacy-policy", "snippet": "Details inference telemetry, customer dataset security, and compliance standards."},
    ],
    "wandb": [
        {"title": "Weights & Biases Terms of Service", "url": "https://wandb.ai/site/terms", "snippet": "Governs ML experiment tracking, Weave LLM tracing, model registries, and artifacts."},
        {"title": "Weights & Biases Privacy Policy", "url": "https://wandb.ai/site/privacy", "snippet": "Covers training run telemetry, artifact storage, and enterprise isolation."},
    ],
    "scaleai": [
        {"title": "Scale AI Terms of Service", "url": "https://scale.com/legal/terms", "snippet": "Governs RLHF data annotation, enterprise AI evaluation, and model safety pipelines."},
        {"title": "Scale AI Privacy Policy", "url": "https://scale.com/legal/privacy", "snippet": "Details contributor workforce verification, client dataset confidentiality, and audits."},
    ],
    "suno": [
        {"title": "Suno Terms of Service", "url": "https://suno.com/terms", "snippet": "Governs AI music generation, commercial song ownership on Pro/Premier plans, and audio uploads."},
        {"title": "Suno Privacy Policy", "url": "https://suno.com/privacy", "snippet": "Covers prompt lyrics retention, generated audio tracks, and subscription billing."},
    ],
    "lumaai": [
        {"title": "Luma AI Terms of Service", "url": "https://lumalabs.ai/legal/terms-of-service", "snippet": "Governs Dream Machine video generation, 3D NeRF captures, and commercial usage rights."},
        {"title": "Luma AI Privacy Policy", "url": "https://lumalabs.ai/legal/privacy-policy", "snippet": "Covers uploaded reference frames, 3D scene captures, and rendering telemetry."},
    ],
    "heygen": [
        {"title": "HeyGen Terms of Service", "url": "https://www.heygen.com/terms", "snippet": "Governs AI video avatars, voice cloning consent requirements, and enterprise licenses."},
        {"title": "HeyGen Privacy Policy", "url": "https://www.heygen.com/privacy", "snippet": "Details biometric likeness consent verification, video assets, and voice recordings."},
    ],
    "synthesia": [
        {"title": "Synthesia User Terms of Service", "url": "https://www.synthesia.io/legal/user-terms-of-service", "snippet": "Governs enterprise AI presenter videos, custom avatar rights, and moderation rules."},
        {"title": "Synthesia Customer Terms of Service", "url": "https://www.synthesia.io/legal/customer-terms-of-service", "snippet": "Governs commercial organization subscriptions, AI video licensing, and SLAs."},
        {"title": "Synthesia Privacy Policy", "url": "https://www.synthesia.io/legal/privacy-policy", "snippet": "Covers biometric avatar consent, script retention, and GDPR data processing."},
    ],
    "descript": [
        {"title": "Descript Terms of Service", "url": "https://www.descript.com/terms", "snippet": "Governs text-based audio/video editing, Overdub voice cloning, and cloud transcription."},
        {"title": "Descript Privacy Policy", "url": "https://www.descript.com/privacy", "snippet": "Details media project storage, AI transcription processing, and voice model consent."},
    ],
    "ollama": [
        {"title": "Ollama Terms of Use", "url": "https://ollama.com/terms", "snippet": "Governs local LLM runner software, model library distribution, and cloud sync."},
        {"title": "Ollama Privacy Policy", "url": "https://ollama.com/privacy", "snippet": "Details minimal telemetry, local execution privacy, and registry download logs."},
    ],
    "pinecone": [
        {"title": "Pinecone Terms of Service", "url": "https://www.pinecone.io/terms/", "snippet": "Governs serverless vector database indexes, RAG embeddings storage, and usage billing."},
        {"title": "Pinecone Privacy Policy", "url": "https://www.pinecone.io/privacy/", "snippet": "Covers vector metadata isolation, query latency metrics, and enterprise security."},
    ],
    "weaviate": [
        {"title": "Weaviate Cloud Terms of Service", "url": "https://weaviate.io/service", "snippet": "Governs managed vector database clusters, hybrid search, and open-source licensing."},
        {"title": "Weaviate Privacy Policy", "url": "https://weaviate.io/privacy", "snippet": "Details cluster usage telemetry, developer accounts, and GDPR compliance."},
    ],
    "qdrant": [
        {"title": "Qdrant Cloud Terms of Service", "url": "https://qdrant.tech/legal/terms_and_conditions/", "snippet": "Governs Rust-based managed vector search clusters, hybrid cloud, and SLAs."},
        {"title": "Qdrant Privacy Policy", "url": "https://qdrant.tech/legal/privacy-policy/", "snippet": "Covers cloud telemetry, vector cluster security, and European data residency."},
    ],
    "langchain": [
        {"title": "LangChain & LangSmith Terms of Service", "url": "https://www.langchain.com/terms-of-service", "snippet": "Governs LangSmith LLM observability, LangGraph Cloud, and evaluation datasets."},
        {"title": "LangChain Privacy Policy", "url": "https://www.langchain.com/privacy-policy", "snippet": "Details trace span retention, prompt dataset privacy, and enterprise access logs."},
    ],

    # ---------------------------------------------------------
    # 19. Programming Languages, Runtimes, Registries & Foundations
    # ---------------------------------------------------------
    "python": [
        {"title": "Python Software Foundation Terms & PyPI Terms of Use", "url": "https://pypi.org/policy/terms-of-use/", "snippet": "Governs Python Package Index (PyPI) package publishing, PSF trademarks, and acceptable use."},
        {"title": "Python.org & PyPI Privacy Notice", "url": "https://policies.python.org/pypi.org/Privacy-Notice/", "snippet": "Covers PyPI maintainer accounts, 2FA security logs, and package download telemetry."},
    ],
    "nodejs": [
        {"title": "OpenJS Foundation Terms of Service", "url": "https://openjsf.org/terms", "snippet": "Governs Node.js runtime governance, OpenJS projects, and foundation trademark rules."},
        {"title": "OpenJS Foundation Privacy Policy", "url": "https://openjsf.org/privacy", "snippet": "Covers contributor records, mailing lists, and foundation website analytics."},
    ],
    "npm": [
        {"title": "npm Terms of Use", "url": "https://docs.npmjs.com/policies/terms", "snippet": "Governs JavaScript/TypeScript package registry publishing, scoped orgs, and takedown rules."},
        {"title": "npm Privacy Policy", "url": "https://docs.npmjs.com/policies/privacy", "snippet": "Details package maintainer logs, CLI authentication tokens, and GitHub registry integration."},
    ],
    "deno": [
        {"title": "Deno Acceptable Use Policy", "url": "https://docs.deno.com/deploy/acceptable_use_policy/", "snippet": "Governs Deno Deploy serverless isolates, JSR package registry, and acceptable runtime use."},
        {"title": "Deno Privacy Policy", "url": "https://docs.deno.com/deploy/privacy_policy/", "snippet": "Covers Deno CLI update checks, Deploy edge execution logs, and developer accounts."},
    ],
    "typescript": [
        {"title": "Microsoft Open Source & TypeScript Legal", "url": "https://www.microsoft.com/en-us/legal/terms-of-use", "snippet": "Governs TypeScript Playground, DefinitelyTyped ecosystem portals, and Apache-2.0 software."},
        {"title": "Microsoft Privacy Statement (TypeScript)", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Covers TypeScript language service telemetry and documentation portal cookies."},
    ],
    "rustlang": [
        {"title": "Rust Foundation Privacy Policy", "url": "https://rustfoundation.org/policy/privacy-policy/", "snippet": "Official Rust Foundation privacy policy governing rust-lang.org, static.rust-lang.org, and crates.io."},
        {"title": "Rust Internals & Community Terms of Service", "url": "https://internals.rust-lang.org/tos", "snippet": "Governs Rust community forums, user accounts, and acceptable conduct."},
    ],
    "golang": [
        {"title": "Go (golang) Terms of Service", "url": "https://go.dev/tos", "snippet": "Governs go.dev, Go module proxy (proxy.golang.org), checksum database, and pkg.go.dev index."},
        {"title": "Go Module Mirror & Privacy Policy", "url": "https://proxy.golang.org/privacy", "snippet": "Details Go module proxy logging minimization, checksum transparency, and telemetry."},
        {"title": "Google Privacy Policy (Go)", "url": "https://policies.google.com/privacy", "snippet": "Covers go.dev website telemetry and documentation analytics."},
    ],
    "java": [
        {"title": "Oracle Java & JDK License Terms", "url": "https://www.oracle.com/downloads/licenses/no-fee-license.html", "snippet": "Governs Oracle JDK No-Fee Terms and Conditions (NFTC) and commercial Java SE subscriptions."},
        {"title": "Oracle Privacy Policy", "url": "https://www.oracle.com/legal/privacy/", "snippet": "Covers JDK download records, Java updater telemetry, and enterprise support."},
    ],
    "dotnet": [
        {"title": ".NET Foundation & NuGet Terms of Use", "url": "https://www.nuget.org/policies/Terms", "snippet": "Governs .NET / C# NuGet package gallery, Microsoft open-source governance, and symbols."},
        {"title": "Microsoft Privacy Statement (.NET / NuGet)", "url": "https://www.nuget.org/policies/Privacy", "snippet": "Covers .NET CLI opt-out telemetry, NuGet publisher accounts, and crash diagnostics."},
    ],
    "cpp": [
        {"title": "Standard C++ Foundation (isocpp.org) Terms of Use", "url": "https://isocpp.org/home/terms-of-use", "snippet": "Governs C++ standards committee resources, WG21 papers, and C++ FAQ publishing."},
        {"title": "Standard C++ Foundation Privacy Policy", "url": "https://isocpp.org/home/privacy-policy", "snippet": "Covers community portal logs, mailing list records, and website analytics."},
    ],
    "swift": [
        {"title": "Swift.org Terms & Open Source Licensing", "url": "https://www.swift.org/LICENSE.txt", "snippet": "Apache 2.0 open-source license and Swift package/compiler ecosystem governance."},
        {"title": "Apple / Swift.org Privacy Policy", "url": "https://www.apple.com/legal/privacy/", "snippet": "Covers Swift.org forums, bug tracker accounts, and toolchain download logs."},
    ],
    "kotlin": [
        {"title": "Kotlin Foundation & JetBrains Terms", "url": "https://kotlinfoundation.org/guidelines/", "snippet": "Governs Kotlin language trademarks, Apache-2.0 compiler, and Kotlin Multiplatform tools."},
        {"title": "JetBrains Privacy Policy (Kotlin)", "url": "https://www.jetbrains.com/legal/docs/privacy/privacy/", "snippet": "Covers Kotlin Playground execution, compiler telemetry, and community forums."},
    ],
    "ruby": [
        {"title": "RubyGems.org Terms of Service", "url": "https://rubygems.org/policies/terms-of-service", "snippet": "Governs Ruby gem package hosting, gem ownership transfers, and namespace policies."},
        {"title": "RubyGems.org Privacy Policy", "url": "https://rubygems.org/policies/privacy", "snippet": "Details maintainer MFA logs, gem download statistics, and security notifications."},
    ],
    "php": [
        {"title": "PHP.net Privacy Policy", "url": "https://www.php.net/privacy.php", "snippet": "Covers PHP language website logs, documentation mirrors, and contributor privacy."},
    ],
    "flutter": [
        {"title": "Flutter Terms of Service", "url": "https://docs.flutter.dev/tos", "snippet": "Governs Dart pub.dev package repository, Flutter SDK tools, and Google developer policies."},
        {"title": "Flutter & Dart Privacy Policy", "url": "https://policies.google.com/privacy", "snippet": "Covers Flutter CLI diagnostic telemetry (`--suppress-analytics`) and pub.dev accounts."},
    ],
    "elixir": [
        {"title": "Hex.pm (Elixir / Erlang) Code of Conduct", "url": "https://hex.pm/policies/codeofconduct", "snippet": "Governs Elixir and Erlang package registry community conduct and moderation."},
        {"title": "Hex.pm (Elixir / Erlang) Privacy Policy", "url": "https://hex.pm/policies/privacy", "snippet": "Covers package publisher logs, API token access, and minimal billing records."},
    ],
    "julia": [
        {"title": "The Julia Language Privacy Notice", "url": "https://julialang.org/privacy/", "snippet": "Covers Julia Pkg server telemetry, Discourse community forums, and CI build logs."},
        {"title": "JuliaHub Privacy Policy", "url": "https://juliahub.com/legal/privacy-policy", "snippet": "Covers JuliaHub cloud compute workspaces and enterprise package registries."},
    ],
    "linuxfoundation": [
        {"title": "The Linux Foundation Terms of Use", "url": "https://www.linuxfoundation.org/legal/terms", "snippet": "Governs Linux kernel trademarks, CNCF, LF Training certifications, and open-source projects."},
        {"title": "The Linux Foundation Privacy Policy", "url": "https://www.linuxfoundation.org/legal/privacy-policy", "snippet": "Details LFID developer accounts, contributor CLA records, and event registrations."},
    ],
    "canonical": [
        {"title": "Canonical / Ubuntu Legal & Terms", "url": "https://ubuntu.com/legal/terms-and-policies", "snippet": "Governs Ubuntu Linux, Snapcraft Store, Ubuntu Pro subscriptions, and MAAS/Juju."},
        {"title": "Canonical Privacy Notice", "url": "https://ubuntu.com/legal/data-privacy", "snippet": "Details Ubuntu crash reporting (Apport), Snap update checks, and enterprise support."},
    ],
    "redhat": [
        {"title": "Red Hat Enterprise Agreement & Terms", "url": "https://www.redhat.com/en/about/agreements", "snippet": "Governs Red Hat Enterprise Linux (RHEL), OpenShift, Ansible, and developer subscriptions."},
        {"title": "Red Hat Privacy Statement", "url": "https://www.redhat.com/en/about/privacy-policy", "snippet": "Covers Red Hat Insights telemetry, subscription manager logs, and IBM data sharing."},
    ],
    "archlinux": [
        {"title": "Arch Linux Terms of Service", "url": "https://terms.archlinux.org/docs/terms-of-service/", "snippet": "Governs Arch User Repository (AUR), Arch Wiki, bug tracker, and mirror infrastructure."},
        {"title": "Arch Linux Privacy Policy", "url": "https://terms.archlinux.org/docs/privacy-policy/", "snippet": "Details AUR maintainer accounts, forum logs, and minimal package mirror telemetry."},
    ],
    "homebrew": [
        {"title": "Homebrew Anonymous Analytics Policy", "url": "https://docs.brew.sh/Analytics", "snippet": "Details InfluxDB anonymous formula install telemetry and `HOMEBREW_NO_ANALYTICS` opt-out."},
    ],

    # ---------------------------------------------------------
    # 20. Expanded Software Dev Tools, Cloud, DBs, Auth & Observability
    # ---------------------------------------------------------
    "aws": [
        {"title": "AWS Site Terms", "url": "https://aws.amazon.com/terms/", "snippet": "Governs Amazon Web Services EC2, S3, Lambda, Bedrock AI, and cloud portal usage."},
        {"title": "AWS Customer Agreement", "url": "https://aws.amazon.com/agreement/", "snippet": "Governs enterprise AWS cloud infrastructure, compute instances, and SLAs."},
        {"title": "AWS Privacy Notice", "url": "https://aws.amazon.com/privacy/", "snippet": "Covers enterprise cloud data residency, IAM audit logs, and billing telemetry."},
    ],
    "googlecloud": [
        {"title": "Google Cloud Platform Terms of Service", "url": "https://cloud.google.com/terms/", "snippet": "Governs GCP compute, BigQuery, Vertex AI, GKE, and Cloud Run enterprise contracts."},
        {"title": "Google Cloud Privacy Notice", "url": "https://cloud.google.com/terms/cloud-privacy-notice", "snippet": "Details customer data ownership, zero-training commitments on Vertex AI, and telemetry."},
    ],
    "azure": [
        {"title": "Microsoft Azure Online Services Terms", "url": "https://www.microsoft.com/licensing/terms/product/ForOnlineServices/all", "snippet": "Governs Azure cloud VMs, Azure OpenAI Service, AKS, and enterprise compliance."},
        {"title": "Microsoft Privacy Statement (Azure)", "url": "https://privacy.microsoft.com/en-us/privacystatement", "snippet": "Covers enterprise tenant data isolation, Defender logs, and regional data residency."},
    ],
    "hashicorp": [
        {"title": "HashiCorp Terms of Service", "url": "https://www.hashicorp.com/terms-of-service", "snippet": "Governs Terraform Cloud, Vault, Consul, Nomad, and BSL source-available licenses."},
        {"title": "HashiCorp Privacy Policy", "url": "https://www.hashicorp.com/privacy", "snippet": "Details Terraform state storage, CLI checkpoint telemetry, and enterprise billing."},
    ],
    "pulumi": [
        {"title": "Pulumi Legal & Terms Hub", "url": "https://www.pulumi.com/legal/", "snippet": "Governs Infrastructure-as-Code SDKs, Pulumi Cloud state backends, and ESC secrets."},
        {"title": "Pulumi Privacy Policy", "url": "https://www.pulumi.com/privacy/", "snippet": "Covers deployment state metadata, CLI telemetry, and enterprise SSO logs."},
    ],
    "circleci": [
        {"title": "CircleCI Terms of Service", "url": "https://circleci.com/legal/terms-of-service/", "snippet": "Governs cloud CI/CD build runners, Docker layer caching, orbs, and compute credits."},
        {"title": "CircleCI Privacy Policy", "url": "https://circleci.com/legal/privacy/", "snippet": "Details build log retention, environment secret encryption, and VCS webhooks."},
    ],
    "vultr": [
        {"title": "Vultr Terms of Service", "url": "https://www.vultr.com/legal/tos/", "snippet": "Governs bare metal, cloud GPU instances, Kubernetes, and global VPS bandwidth."},
        {"title": "Vultr Privacy Policy", "url": "https://www.vultr.com/legal/privacy/", "snippet": "Covers anti-abuse verification, server provisioning logs, and billing records."},
    ],
    "hetzner": [
        {"title": "Hetzner Online Terms and Conditions", "url": "https://www.hetzner.com/legal/terms-and-conditions/", "snippet": "Governs German/European dedicated servers, Hetzner Cloud VPS, and Storage Boxes."},
        {"title": "Hetzner Online Privacy Policy", "url": "https://www.hetzner.com/legal/privacy-policy/", "snippet": "Details strict German GDPR data protection, KYC verification, and server logs."},
    ],
    "ovhcloud": [
        {"title": "OVHcloud Terms of Service", "url": "https://us.ovhcloud.com/legal/terms-of-service/", "snippet": "Governs European sovereign cloud, bare-metal servers, and Public Cloud instances."},
        {"title": "OVHcloud Privacy Policy", "url": "https://us.ovhcloud.com/legal/privacy-policy/", "snippet": "Covers EU data sovereignty, support ticket audits, and network telemetry."},
    ],
    "firebase": [
        {"title": "Firebase Terms of Service", "url": "https://firebase.google.com/terms", "snippet": "Governs Firestore, Firebase Auth, Realtime Database, Cloud Messaging, and Crashlytics."},
        {"title": "Google Privacy Policy (Firebase)", "url": "https://firebase.google.com/support/privacy", "snippet": "Details mobile SDK analytics, Crashlytics stack traces, and app user telemetry."},
    ],
    "neon": [
        {"title": "Neon Serverless Postgres Terms", "url": "https://neon.com/platform-terms", "snippet": "Governs serverless PostgreSQL branching, autoscaling compute, and storage quotas."},
        {"title": "Neon / Databricks Privacy Notice", "url": "https://www.databricks.com/legal/privacynotice", "snippet": "Covers database connection logs, developer telemetry, and subprocessor security."},
    ],
    "planetscale": [
        {"title": "PlanetScale Terms of Service", "url": "https://planetscale.com/legal/siteterms", "snippet": "Governs Vitess-powered serverless MySQL databases, deploy requests, and Insights."},
        {"title": "PlanetScale Privacy Policy", "url": "https://planetscale.com/legal/privacy", "snippet": "Details query performance metrics, schema metadata, and SOC 2 compliance."},
    ],
    "turso": [
        {"title": "Turso (libSQL) Terms of Service", "url": "https://turso.tech/terms-of-use", "snippet": "Governs edge-replicated libSQL/SQLite databases, multi-tenant DBs, and storage limits."},
        {"title": "Turso Privacy Policy", "url": "https://turso.tech/privacy-policy", "snippet": "Covers edge replication logs, API token telemetry, and billing records."},
    ],
    "upstash": [
        {"title": "Upstash Privacy Policy", "url": "https://upstash.com/trust/privacy", "snippet": "Covers serverless Redis, QStash, and Vector request logs, encryption-at-rest, and developer billing."},
    ],
    "clickhouse": [
        {"title": "ClickHouse Cloud Terms of Service", "url": "https://clickhouse.com/legal/agreements/terms-of-service", "snippet": "Governs managed OLAP analytical databases, real-time SQL ingestion, and BYOC."},
        {"title": "ClickHouse Privacy Policy", "url": "https://clickhouse.com/legal/privacy-policy", "snippet": "Details cloud query telemetry, enterprise support access, and GDPR safeguards."},
    ],
    "grafana": [
        {"title": "Grafana Labs Terms of Service", "url": "https://grafana.com/legal/terms/", "snippet": "Governs Grafana Cloud dashboards, Loki logs, Tempo tracing, and Prometheus metrics."},
        {"title": "Grafana Labs Privacy Policy", "url": "https://grafana.com/legal/privacy-policy/", "snippet": "Covers OSS telemetry opt-outs, cloud observability logs, and user accounts."},
    ],
    "pagerduty": [
        {"title": "PagerDuty Terms of Service", "url": "https://www.pagerduty.com/terms-of-service/", "snippet": "Governs on-call incident response, alert escalations, AIOps, and enterprise SLAs."},
        {"title": "PagerDuty Privacy Policy", "url": "https://www.pagerduty.com/privacy-policy/", "snippet": "Details SMS/voice paging logs, incident payload metadata, and responder schedules."},
    ],
    "posthog": [
        {"title": "PostHog Terms of Service", "url": "https://posthog.com/terms", "snippet": "Governs open-source product analytics, session replays, feature flags, and A/B tests."},
        {"title": "PostHog Privacy Policy", "url": "https://posthog.com/privacy", "snippet": "Covers EU/US data residency, session recording masking, and telemetry ingestion."},
    ],
    "mixpanel": [
        {"title": "Mixpanel Terms of Service", "url": "https://mixpanel.com/legal/terms-of-use/", "snippet": "Governs event-based product analytics, funnel tracking, and warehouse connectors."},
        {"title": "Mixpanel Privacy Policy", "url": "https://mixpanel.com/legal/privacy-policy/", "snippet": "Details end-user behavioral event tracking, session replays, and GDPR deletion APIs."},
    ],
    "launchdarkly": [
        {"title": "LaunchDarkly Terms of Service", "url": "https://launchdarkly.com/terms-of-service/", "snippet": "Governs enterprise feature flags, progressive rollouts, and experimentation SDKs."},
        {"title": "LaunchDarkly Privacy Policy", "url": "https://launchdarkly.com/privacy/", "snippet": "Details user targeting context attributes, SDK evaluation telemetry, and audits."},
    ],
    "auth0": [
        {"title": "Okta / Auth0 Terms of Service", "url": "https://www.okta.com/agreements/", "snippet": "Governs universal identity authentication, SSO, MFA, OAuth2, and CIAM pipelines."},
        {"title": "Okta / Auth0 Privacy Policy", "url": "https://www.okta.com/privacy-policy/", "snippet": "Covers login audit logs, device fingerprinting for anomaly detection, and credentials."},
    ],
    "clerk": [
        {"title": "Clerk Terms of Service", "url": "https://clerk.com/legal/terms", "snippet": "Governs drop-in authentication UI, session JWTs, passkeys, and B2B organizations."},
        {"title": "Clerk Privacy Policy", "url": "https://clerk.com/legal/privacy", "snippet": "Details end-user identity records, OAuth token encryption, and security logs."},
    ],
    "algolia": [
        {"title": "Algolia Terms of Service", "url": "https://www.algolia.com/policies/terms/", "snippet": "Governs instant search APIs, AI neural vector search, and ecommerce merchandising."},
        {"title": "Algolia Privacy Policy", "url": "https://www.algolia.com/policies/privacy/", "snippet": "Covers search query analytics, click-through conversion tracking, and index data."},
    ],
    "cloudinary": [
        {"title": "Cloudinary Terms of Use", "url": "https://cloudinary.com/tos", "snippet": "Governs cloud image/video transformations, DAM asset hosting, and CDN delivery."},
        {"title": "Cloudinary Privacy Policy", "url": "https://cloudinary.com/privacy", "snippet": "Details uploaded media asset processing, AI tagging, and bandwidth telemetry."},
    ],
    "vscode": [
        {"title": "Visual Studio Code License & Terms", "url": "https://code.visualstudio.com/License/", "snippet": "Governs Microsoft VS Code binary distribution, Marketplace extensions, and Remote Tunnels."},
        {"title": "Microsoft Privacy Statement (VS Code)", "url": "https://code.visualstudio.com/docs/supporting/faq#_how-to-disable-telemetry-reporting", "snippet": "Covers editor crash/usage telemetry (`telemetry.telemetryLevel`) and extension metrics."},
    ],
    "zed": [
        {"title": "Zed Industries Terms of Service", "url": "https://zed.dev/terms-of-service", "snippet": "Governs GPU-accelerated Zed code editor, real-time collaboration channels, and Zed AI."},
        {"title": "Zed Industries Privacy Policy", "url": "https://zed.dev/privacy-policy", "snippet": "Details local-first editing privacy, opt-out telemetry, and AI assistant context rules."},
    ],
    "raycast": [
        {"title": "Raycast Terms of Service", "url": "https://www.raycast.com/terms-of-service", "snippet": "Governs macOS/Windows productivity launcher, Raycast Pro AI, Cloud Sync, and extensions."},
        {"title": "Raycast Privacy Policy", "url": "https://www.raycast.com/privacy", "snippet": "Covers encrypted Cloud Sync vaults, extension store logs, and AI query retention."},
    ],
    "warp": [
        {"title": "Warp Terminal Terms of Service", "url": "https://www.warp.dev/legal/terms-of-service", "snippet": "Governs Rust-based modern terminal, Warp Drive team workflows, and AI command search."},
        {"title": "Warp Privacy Policy", "url": "https://www.warp.dev/legal/privacy-policy", "snippet": "Details terminal telemetry controls, secret redaction, and AI prompt retention."},
    ],
    "sonarqube": [
        {"title": "SonarSource & SonarCloud Terms of Use", "url": "https://www.sonarsource.com/legal/website-terms-of-use/", "snippet": "Governs SonarQube static code analysis, SonarCloud SAST scanning, and code quality gates."},
        {"title": "SonarSource Privacy Policy", "url": "https://www.sonarsource.com/company/privacy/", "snippet": "Covers repository scan metadata, vulnerability reports, and developer accounts."},
    ],
    "devto": [
        {"title": "DEV Community Terms of Use", "url": "https://dev.to/terms", "snippet": "Governs Forem-powered developer blogging, open-source community code of conduct, and APIs."},
        {"title": "DEV Community Privacy Policy", "url": "https://dev.to/privacy", "snippet": "Covers developer profile records, reading history, and sponsor disclosure rules."},
    ],
    "leetcode": [
        {"title": "LeetCode Terms of Service", "url": "https://leetcode.com/terms/", "snippet": "Governs coding interview practice, weekly contests, LeetCode Premium, and anti-plagiarism."},
        {"title": "LeetCode Privacy Policy", "url": "https://leetcode.com/privacy/", "snippet": "Details code submission logs, contest rankings, and interview prep analytics."},
    ],
    "hackerrank": [
        {"title": "HackerRank Terms of Service", "url": "https://www.hackerrank.com/terms-of-service/", "snippet": "Governs developer skill assessments, technical interviews, and proctoring integrity."},
        {"title": "HackerRank Privacy Policy", "url": "https://www.hackerrank.com/privacy/", "snippet": "Covers candidate code playback, browser proctoring signals, and recruiter sharing."},
    ],

    # ---------------------------------------------------------
    # 21. Expanded VPNs, Privacy, Cybersecurity & Browsers
    # ---------------------------------------------------------
    "mullvad": [
        {"title": "Mullvad VPN Terms of Service", "url": "https://mullvad.net/en/help/terms-service", "snippet": "Governs anonymous numbered-account VPN tunnels, WireGuard/OpenVPN, and cash/crypto payments."},
        {"title": "Mullvad VPN Privacy Policy", "url": "https://mullvad.net/en/help/privacy-policy", "snippet": "Industry-leading zero-log commitment: no email, no activity logs, and RAM-only servers."},
    ],
    "privateinternetaccess": [
        {"title": "Private Internet Access (PIA) Terms of Service", "url": "https://www.privateinternetaccess.com/pages/terms-of-service", "snippet": "Governs open-source VPN clients, MACE ad-blocking, port forwarding, and dedicated IPs."},
        {"title": "Private Internet Access Privacy Policy", "url": "https://www.privateinternetaccess.com/pages/privacy-policy", "snippet": "Court-proven and audited strict no-logs policy with zero connection or traffic retention."},
    ],
    "ivpn": [
        {"title": "IVPN Terms of Service", "url": "https://www.ivpn.net/en/tos-mobile-app/", "snippet": "Governs multi-hop WireGuard VPN, AntiTracker DNS, and anonymous Monero/cash accounts."},
        {"title": "IVPN Privacy Policy", "url": "https://www.ivpn.net/en/privacy/", "snippet": "Details zero-email account generation, independent security audits, and strict no-logging."},
    ],
    "windscribe": [
        {"title": "Windscribe Terms of Service", "url": "https://windscribe.com/terms", "snippet": "Governs VPN and R.O.B.E.R.T. DNS firewall, free/Pro data allowances, and static IPs."},
        {"title": "Windscribe Privacy Policy", "url": "https://windscribe.com/privacy", "snippet": "Details RAM-disk servers, zero IP/session logging, and minimal bandwidth counters."},
    ],
    "tunnelbear": [
        {"title": "TunnelBear Terms of Service", "url": "https://www.tunnelbear.com/terms-of-service", "snippet": "Governs consumer VPN apps, VigilantBear kill switch, and McAfee-owned service rules."},
        {"title": "TunnelBear Privacy Policy", "url": "https://www.tunnelbear.com/privacy-policy", "snippet": "Details annual independent security audits and zero browsing activity logging."},
    ],
    "adguard": [
        {"title": "AdGuard End User License Agreement", "url": "https://adguard.com/en/eula.html", "snippet": "Governs AdGuard Ad Blocker, AdGuard DNS, and AdGuard VPN encrypted tunneling."},
        {"title": "AdGuard Privacy Policy", "url": "https://adguard.com/en/privacy.html", "snippet": "Covers DNS query filtering options, no-logs VPN claims, and crash report opt-ins."},
    ],
    "nextdns": [
        {"title": "NextDNS Privacy Policy", "url": "https://nextdns.io/privacy", "snippet": "Details user-configurable DNS log retention (including zero-logging mode) and jurisdiction."},
    ],
    "torproject": [
        {"title": "Tor Project Terms & Legal FAQ", "url": "https://www.torproject.org/about/trademark/", "snippet": "Governs Tor Browser open-source anonymity software, onion services, and relay operation."},
        {"title": "Tor Project Privacy Policy", "url": "https://www.torproject.org/about/privacy_policy/", "snippet": "Affirms zero tracking on torproject.org and onion-routed anonymity architecture."},
    ],
    "vivaldi": [
        {"title": "Vivaldi Privacy Policy Overview", "url": "https://vivaldi.com/privacy/", "snippet": "Governs Vivaldi desktop/mobile browser, built-in Mail/Calendar, and sync services."},
        {"title": "Vivaldi Browser Privacy Policy", "url": "https://vivaldi.com/privacy/browser/", "snippet": "Details end-to-end encrypted sync, zero user profiling, and anonymized daily ping counts."},
    ],
    "opera": [
        {"title": "Opera End User License Agreement", "url": "https://legal.opera.com/terms/", "snippet": "Governs Opera Browser, Opera GX gaming browser, built-in free VPN, and Aria AI."},
        {"title": "Opera Privacy Statement", "url": "https://legal.opera.com/privacy/", "snippet": "Details browser telemetry, partner search monetization, and built-in VPN data handling."},
    ],
    "arc": [
        {"title": "The Browser Company (Arc / Dia) Privacy Policy", "url": "https://arc.net/privacy", "snippet": "Covers encrypted tab sync, AI summary query handling, and product analytics."},
    ],
    "dashlane": [
        {"title": "Dashlane Terms of Service", "url": "https://www.dashlane.com/terms", "snippet": "Governs zero-knowledge password vault, passkey sync, and bundled Hotspot Shield VPN."},
        {"title": "Dashlane Privacy Policy", "url": "https://www.dashlane.com/privacy", "snippet": "Details zero-knowledge encryption architecture, dark web monitoring, and billing."},
    ],
    "crowdstrike": [
        {"title": "CrowdStrike Terms and Conditions", "url": "https://www.crowdstrike.com/terms-conditions/", "snippet": "Governs Falcon endpoint detection and response (EDR), threat intelligence, and cloud security."},
        {"title": "CrowdStrike Privacy Notice", "url": "https://www.crowdstrike.com/privacy-notice/", "snippet": "Covers endpoint process telemetry, malware file inspection, and enterprise compliance."},
    ],
    "cloudflarewarp": [
        {"title": "Cloudflare 1.1.1.1 & WARP Terms of Service", "url": "https://developers.cloudflare.com/1.1.1.1/privacy/public-dns-resolver/", "snippet": "Governs 1.1.1.1 public DNS resolver and WARP WireGuard consumer/Zero Trust tunnels."},
        {"title": "Cloudflare 1.1.1.1 Privacy Commitments", "url": "https://www.cloudflare.com/application/privacypolicy/", "snippet": "Audited commitment never to sell browsing data or retain client source IP addresses beyond 25h."},
    ],
    "hackerone": [
        {"title": "HackerOne Terms of Service", "url": "https://www.hackerone.com/terms", "snippet": "Governs bug bounty programs, coordinated vulnerability disclosure, and researcher payouts."},
        {"title": "HackerOne Privacy Policy", "url": "https://www.hackerone.com/privacy", "snippet": "Details researcher identity/KYC checks, vulnerability report confidentiality, and safe harbor."},
    ],
    "virustotal": [
        {"title": "VirusTotal / Google Cloud Terms of Service", "url": "https://cloud.google.com/terms", "snippet": "Governs malware file/URL scanning, Threat Intelligence APIs, and Google Cloud services."},
        {"title": "VirusTotal / Google Cloud Privacy Policy", "url": "https://cloud.google.com/privacy", "snippet": "Covers cloud service privacy, threat sample disclosures, and security telemetry."},
    ],

    # ---------------------------------------------------------
    # 22. Expanded Streaming, Music, Books & Creator Media
    # ---------------------------------------------------------
    "bandcamp": [
        {"title": "Bandcamp Terms of Use", "url": "https://bandcamp.com/terms_of_use", "snippet": "Governs direct-to-artist music sales, vinyl merch, Bandcamp Fridays, and streaming."},
        {"title": "Bandcamp Privacy Policy", "url": "https://bandcamp.com/privacy", "snippet": "Covers fan collection visibility, artist mailing lists, and Epic/Songtradr data transitions."},
    ],
    "plex": [
        {"title": "Plex Terms of Service", "url": "https://www.plex.tv/about/privacy-legal/plex-terms-of-service/", "snippet": "Governs personal media servers, Plex Pass, free ad-supported streaming, and live TV."},
        {"title": "Plex Privacy Policy", "url": "https://www.plex.tv/about/privacy-legal/", "snippet": "Details personal library metadata privacy, Discover Watchlist sharing, and ad telemetry."},
    ],
    "letterboxd": [
        {"title": "Letterboxd Terms of Use", "url": "https://letterboxd.com/legal/terms-of-use/", "snippet": "Governs film logging, community reviews, Pro/Patron tiers, and content moderation."},
        {"title": "Letterboxd Privacy Policy", "url": "https://letterboxd.com/legal/privacy-policy/", "snippet": "Covers public film diary visibility, programmatic advertising, and GDPR rights."},
    ],
    "imdb": [
        {"title": "IMDb Conditions of Use", "url": "https://www.imdb.com/conditions", "snippet": "Governs film/TV database contributions, IMDbPro casting profiles, and Amazon integration."},
        {"title": "IMDb Privacy Notice", "url": "https://www.imdb.com/privacy", "snippet": "Covers watchlist telemetry, user reviews, and Amazon advertising cross-profiling."},
    ],
    "goodreads": [
        {"title": "Goodreads Terms of Use", "url": "https://www.goodreads.com/about/terms", "snippet": "Governs book reviews, reading challenges, Kindle highlights syncing, and giveaways."},
        {"title": "Goodreads Privacy Notice", "url": "https://www.goodreads.com/about/privacy", "snippet": "Covers reading shelves, Amazon account linking, and personalized book recommendations."},
    ],
    "scribd": [
        {"title": "Scribd & Everand Terms of Use", "url": "https://support.scribd.com/hc/en-us/articles/210129366-General-Terms-of-Use", "snippet": "Governs digital document uploads, Everand audiobooks/ebooks, and copyright takedowns."},
        {"title": "Scribd Privacy Policy", "url": "https://support.scribd.com/hc/en-us/articles/210129146-Privacy-Policy", "snippet": "Details reading progress logs, document indexing, and subscription billing."},
    ],
    "gumroad": [
        {"title": "Gumroad Terms of Service", "url": "https://gumroad.com/terms", "snippet": "Governs digital product sales, creator 10% platform fees, chargebacks, and payouts."},
        {"title": "Gumroad Privacy Policy", "url": "https://gumroad.com/privacy", "snippet": "Covers buyer download receipts, creator tax verification, and email marketing lists."},
    ],
    "kofi": [
        {"title": "Ko-fi Terms & Conditions", "url": "https://more.ko-fi.com/terms", "snippet": "Governs creator tips, memberships, commissions, and zero-fee donation tiers."},
        {"title": "Ko-fi Privacy Policy", "url": "https://more.ko-fi.com/privacy", "snippet": "Details supporter payment metadata, creator payout links, and cookie usage."},
    ],
    "ghost": [
        {"title": "Ghost(Pro) Terms of Service", "url": "https://ghost.org/terms/", "snippet": "Governs managed Ghost publishing, newsletter delivery, and zero-commission memberships."},
        {"title": "Ghost Foundation Privacy Policy", "url": "https://ghost.org/privacy/", "snippet": "Covers subscriber lists, email open telemetry, and open-source publishing privacy."},
    ],

    # ---------------------------------------------------------
    # 23. Crypto, Exchanges, Wallets, DeFi & Blockchain
    # ---------------------------------------------------------
    "geminiexchange": [
        {"title": "Gemini Trust User Agreement", "url": "https://www.gemini.com/legal/user-agreement", "snippet": "Governs NYDFS-regulated crypto exchange trading, GUSD stablecoin, and ActiveTrader."},
        {"title": "Gemini Privacy Policy", "url": "https://www.gemini.com/legal/privacy-policy", "snippet": "Covers KYC/AML financial disclosures, wallet addresses, and tax reporting."},
    ],
    "metamask": [
        {"title": "Consensys / MetaMask Terms of Use", "url": "https://consensys.io/terms-of-use", "snippet": "Governs self-custody MetaMask wallet, Swaps aggregator fees, and Infura RPC routing."},
        {"title": "Consensys Privacy Policy", "url": "https://consensys.io/privacy-policy", "snippet": "Details RPC IP address/wallet logging disclosures and privacy toggle settings."},
    ],
    "phantom": [
        {"title": "Phantom Wallet Terms of Service", "url": "https://phantom.app/terms", "snippet": "Governs multi-chain self-custody wallet (Solana, Ethereum, Bitcoin), swaps, and staking."},
        {"title": "Phantom Privacy Policy", "url": "https://phantom.app/privacy", "snippet": "Covers transaction simulation telemetry, phishing domain checks, and non-custodial keys."},
    ],
    "ledger": [
        {"title": "Ledger Terms of Use & Ledger Live", "url": "https://shop.ledger.com/pages/terms-and-conditions", "snippet": "Governs Ledger hardware wallets, Ledger Live companion app, and Ledger Recover."},
        {"title": "Ledger Privacy Policy", "url": "https://www.ledger.com/privacy-policy", "snippet": "Details device attestation checks, e-commerce order records, and opt-in analytics."},
    ],
    "trezor": [
        {"title": "Trezor Terms of Use", "url": "https://trezor.io/terms-of-use", "snippet": "Governs open-source Trezor hardware wallets, Trezor Suite, and firmware updates."},
        {"title": "Trezor Privacy Policy", "url": "https://trezor.io/support/logistics/orders-payments/privacy-policy-at-trezor", "snippet": "Details data erasure schedules after hardware delivery and Tor-enabled Suite privacy."},
    ],
    "uniswap": [
        {"title": "Uniswap Labs Terms of Service", "url": "https://uniswap.org/terms-of-service", "snippet": "Governs Uniswap web interface, Uniswap Wallet, DEX routing fees, and token screening."},
        {"title": "Uniswap Labs Privacy Policy", "url": "https://uniswap.org/privacy-policy", "snippet": "Details on-chain wallet screening, browser local storage, and zero seed-phrase access."},
    ],
    "opensea": [
        {"title": "OpenSea Terms of Service", "url": "https://opensea.io/tos", "snippet": "Governs NFT marketplace listings, creator royalties, Seaport protocol, and takedowns."},
        {"title": "OpenSea Privacy Policy", "url": "https://opensea.io/privacy", "snippet": "Covers public blockchain wallet indexing, IP fraud prevention, and account profiles."},
    ],
    "ethereum": [
        {"title": "Ethereum.org Terms of Use", "url": "https://ethereum.org/en/terms-of-use/", "snippet": "Governs Ethereum Foundation educational portal, open-source docs, and trademark use."},
        {"title": "Ethereum.org Privacy Policy", "url": "https://ethereum.org/en/privacy-policy/", "snippet": "Details minimal, tracker-free web analytics and open-source contributor privacy."},
    ],
    "solana": [
        {"title": "Solana Foundation Terms of Use", "url": "https://solana.com/tos", "snippet": "Governs Solana.com developer portal, validator delegation programs, and trademarks."},
        {"title": "Solana Foundation Privacy Policy", "url": "https://solana.com/privacy-policy", "snippet": "Covers grant applicant records, developer telemetry, and cookie disclosures."},
    ],
    "alchemy": [
        {"title": "Alchemy Terms of Service", "url": "https://www.alchemy.com/policies/terms", "snippet": "Governs Web3 RPC node infrastructure, NFT APIs, Account Kit, and compute unit billing."},
        {"title": "Alchemy Privacy Policy", "url": "https://www.alchemy.com/policies/privacy-policy", "snippet": "Details JSON-RPC request logs, developer API metrics, and security audits."},
    ],
    "coingecko": [
        {"title": "CoinGecko Terms of Service", "url": "https://www.coingecko.com/en/terms", "snippet": "Governs cryptocurrency price tracking, CoinGecko API licensing, and portfolio tools."},
        {"title": "CoinGecko Privacy Policy", "url": "https://www.coingecko.com/en/privacy", "snippet": "Covers portfolio watchlist sync, API key telemetry, and ad personalization."},
    ],

    # ---------------------------------------------------------
    # 24. Expanded Finance, Banking, Brokerages & Payments
    # ---------------------------------------------------------
    "chase": [
        {"title": "JPMorgan Chase Digital Services Agreement", "url": "https://www.chase.com/digital/resources/terms-of-use", "snippet": "Governs Chase online banking, Sapphire/Freedom credit cards, Zelle transfers, and J.P. Morgan."},
        {"title": "Chase Online Privacy Policy", "url": "https://www.chase.com/digital/resources/privacy-security/privacy/online-privacy-policy", "snippet": "Details Gramm-Leach-Bliley financial disclosures, credit reporting, and mobile telemetry."},
    ],
    "bankofamerica": [
        {"title": "Bank of America Online Banking Service Agreement", "url": "https://www.bankofamerica.com/online-banking/service-agreement.go", "snippet": "Governs checking/savings accounts, Merrill Edge investing, Erica AI, and wire limits."},
        {"title": "Bank of America Privacy Notice", "url": "https://www.bankofamerica.com/security-center/online-privacy-notice/", "snippet": "Details affiliate financial data sharing, biometric login, and fraud telemetry."},
    ],
    "capitalone": [
        {"title": "Capital One Terms & Conditions", "url": "https://www.capitalone.com/legal/terms-conditions/", "snippet": "Governs Venture/Quicksilver credit cards, 360 Checking, Eno virtual cards, and Auto Navigator."},
        {"title": "Capital One Online Privacy Policy", "url": "https://www.capitalone.com/privacy/online-privacy-policy/", "snippet": "Details credit bureau sharing, merchant offer tracking, and app security logs."},
    ],
    "americanexpress": [
        {"title": "American Express Online Privacy Disclosures", "url": "https://www.americanexpress.com/us/company/privacy-center/online-privacy-disclosures/", "snippet": "Covers cardholder spending insights, fraud analytics, and travel partner sharing."},
    ],
    "visa": [
        {"title": "Visa Legal & Terms of Use", "url": "https://www.visa.com/en-us/legal", "snippet": "Governs Visa payment network portals, Click to Pay, and Visa Direct developer APIs."},
        {"title": "Visa Global Privacy Notice", "url": "https://www.visa.com/en-us/legal/global-privacy-notice", "snippet": "Details card transaction routing metadata, tokenization, and fraud scoring."},
    ],
    "mastercard": [
        {"title": "Mastercard Global Privacy Notice", "url": "https://www.mastercard.com/us/en/global-privacy-notice.html", "snippet": "Details payment clearing analytics, fraud monitoring, and consumer opt-outs."},
    ],
    "fidelity": [
        {"title": "Fidelity Investments Terms of Use", "url": "https://www.fidelity.com/terms-of-use", "snippet": "Governs brokerage accounts, 401(k) plans, IRA retirement trading, and research tools."},
        {"title": "Fidelity Privacy Policy", "url": "https://www.fidelity.com/privacy-policy", "snippet": "Details SEC/FINRA financial recordkeeping, voice biometrics, and customer data security."},
    ],
    "schwab": [
        {"title": "Charles Schwab Online Services Agreement", "url": "https://www.schwab.com/legal/terms", "snippet": "Governs Schwab brokerage, thinkorswim trading, checking accounts, and advisory fees."},
        {"title": "Charles Schwab Privacy Overview", "url": "https://www.schwab.com/legal/privacy-overview", "snippet": "Covers financial regulatory disclosures, trade logs, and mobile app security."},
    ],
    "interactivebrokers": [
        {"title": "Interactive Brokers Privacy Policy", "url": "https://www.interactivebrokers.com/en/accounts/legalDocuments/privacy.php", "snippet": "Covers international regulatory reporting, KYC records, and trade audit logs."},
    ],
    "monzo": [
        {"title": "Monzo Terms & Conditions", "url": "https://monzo.com/legal/terms-and-conditions/", "snippet": "Governs UK/US app-based checking accounts, Pots savings, and fee-free foreign spend."},
        {"title": "Monzo Privacy Notice", "url": "https://monzo.com/legal/privacy-notice/", "snippet": "Details Open Banking connections, credit reference checks, and fraud detection."},
    ],
    "chime": [
        {"title": "Chime Privacy Notice", "url": "https://www.chime.com/policies/chime/privacy-policy/", "snippet": "Covers banking partner disclosures, transaction alerts, and identity verification."},
    ],
    "sofi": [
        {"title": "SoFi Terms of Use", "url": "https://www.sofi.com/terms-of-use/", "snippet": "Governs SoFi Checking & Savings, student/personal loans, and SoFi Invest brokerage."},
        {"title": "SoFi Privacy Policy", "url": "https://www.sofi.com/privacy-policy/", "snippet": "Details credit underwriting disclosures, Relay budget tracking, and affiliate sharing."},
    ],
    "mercury": [
        {"title": "Mercury Terms of Use", "url": "https://mercury.com/legal/terms", "snippet": "Governs startup business banking, Treasury accounts, IO credit cards, and API access."},
        {"title": "Mercury Privacy Policy", "url": "https://mercury.com/legal/privacy", "snippet": "Covers corporate KYC/KYB verification, partner bank disclosures, and audit logs."},
    ],
    "razorpay": [
        {"title": "Razorpay Terms of Use", "url": "https://razorpay.com/terms/", "snippet": "Governs Indian payment gateway, UPI/card settlements, RazorpayX banking, and payouts."},
        {"title": "Razorpay Privacy Policy", "url": "https://razorpay.com/privacy/", "snippet": "Details RBI/PCI-DSS transaction auditing, merchant KYC, and fraud risk telemetry."},
    ],
    "adyen": [
        {"title": "Adyen Terms and Conditions", "url": "https://www.adyen.com/legal/terms-and-conditions", "snippet": "Governs enterprise omnichannel payment acquiring, POS terminals, and global settlements."},
        {"title": "Adyen Privacy Statement", "url": "https://www.adyen.com/policies-and-disclaimer/privacy-policy", "snippet": "Covers payment card tokenization, RevenueProtect fraud scoring, and GDPR compliance."},
    ],

    # ---------------------------------------------------------
    # 25. Expanded News Networks, Tech Media & Knowledge Portals
    # ---------------------------------------------------------
    "npr": [
        {"title": "NPR Terms of Use", "url": "https://www.npr.org/about-npr/179876898/terms-of-use", "snippet": "Governs NPR public radio streams, podcasts, articles, and member station links."},
        {"title": "NPR Privacy Policy", "url": "https://www.npr.org/about-npr/179878450/privacy-policy", "snippet": "Covers podcast download metrics, listener donations, and sponsor measurement."},
    ],
    "economist": [
        {"title": "The Economist Terms of Use", "url": "https://www.economist.com/legal/terms-of-use", "snippet": "Governs Economist digital/print subscriptions, Espresso app, and archival access."},
        {"title": "The Economist Privacy Policy", "url": "https://www.economistgroup.com/privacy-policy", "snippet": "Covers subscriber reading profiles, event registrations, and targeted marketing."},
    ],
    "forbes": [
        {"title": "Forbes Terms of Service", "url": "https://www.forbes.com/terms/", "snippet": "Governs Forbes digital articles, contributor network, billionaire lists, and paywalls."},
        {"title": "Forbes Privacy Statement", "url": "https://www.forbes.com/privacy/", "snippet": "Covers programmatic ad-tech profiling, newsletter telemetry, and reader cookies."},
    ],
    "cnbc": [
        {"title": "NBCUniversal / CNBC Terms of Service", "url": "https://www.nbcuniversal.com/terms", "snippet": "Governs CNBC Investing Club, Pro subscriptions, live market streams, and financial news."},
        {"title": "NBCUniversal Privacy Policy", "url": "https://www.nbcuniversal.com/privacy", "snippet": "Covers market quote tracking, video streaming telemetry, and ad personalization."},
    ],
    "foxnews": [
        {"title": "Fox News Terms of Use", "url": "https://www.foxnews.com/terms-of-use", "snippet": "Governs Fox News digital broadcasts, Fox Nation subscriptions, and article comments."},
        {"title": "Fox News Privacy Policy", "url": "https://www.foxnews.com/privacy-policy", "snippet": "Covers video viewership metrics, device identifiers, and targeted advertising."},
    ],
    "aljazeera": [
        {"title": "Al Jazeera Terms and Conditions", "url": "https://www.aljazeera.com/terms-and-conditions/", "snippet": "Governs Al Jazeera English international news coverage, live streams, and republishing."},
        {"title": "Al Jazeera Privacy Policy", "url": "https://privacy.aljazeera.net/", "snippet": "Details cookie preferences, mobile app analytics, and reader correspondence."},
    ],
    "wired": [
        {"title": "Condé Nast (WIRED) User Agreement", "url": "https://www.condenast.com/user-agreement", "snippet": "Governs WIRED technology journalism, digital subscriptions, and Condé Nast publications."},
        {"title": "Condé Nast Privacy Policy", "url": "https://www.condenast.com/privacy-policy", "snippet": "Covers subscriber behavior profiling, affiliate commerce links, and ad tech."},
    ],
    "techcrunch": [
        {"title": "TechCrunch Terms of Service", "url": "https://techcrunch.com/terms-of-service/", "snippet": "Governs startup news, TechCrunch Disrupt events, and Crunchbase/Media integrations."},
        {"title": "TechCrunch Privacy Policy", "url": "https://techcrunch.com/privacy/", "snippet": "Covers newsletter subscriptions, event badge telemetry, and targeted advertising."},
    ],
    "theverge": [
        {"title": "Vox Media (The Verge) Terms of Use", "url": "https://www.voxmedia.com/legal/terms-of-use", "snippet": "Governs The Verge tech reviews, community comment threads, and Vox Media properties."},
        {"title": "Vox Media Privacy Notice", "url": "https://www.voxmedia.com/legal/privacy-notice", "snippet": "Details Coral comment moderation, affiliate link tracking, and ad measurement."},
    ],
    "hackernews": [
        {"title": "Y Combinator / Hacker News Terms of Use", "url": "https://www.ycombinator.com/legal/#tou", "snippet": "Governs Hacker News submissions, moderation guidelines, and Y Combinator portals."},
        {"title": "Y Combinator Privacy Policy", "url": "https://www.ycombinator.com/legal/#privacy", "snippet": "Details minimal account logging, upvote/karma integrity checks, and YC applications."},
    ],
    "archiveorg": [
        {"title": "Internet Archive Terms of Use", "url": "https://archive.org/about/terms.php", "snippet": "Governs Wayback Machine web snapshots, Open Library lending, and non-profit archiving."},
    ],

    # ---------------------------------------------------------
    # 26. Expanded Global Tech, Semiconductors, Fitness, Retail & SaaS
    # ---------------------------------------------------------
    "amd": [
        {"title": "AMD Terms of Use / Copyright", "url": "https://www.amd.com/en/legal/copyright.html", "snippet": "Governs Ryzen/EPYC/Radeon software drivers, ROCm developer tools, and site usage."},
        {"title": "AMD Privacy Notice", "url": "https://www.amd.com/en/legal/privacy.html", "snippet": "Details Adrenalin driver diagnostic telemetry, crash dumps, and partner disclosures."},
    ],
    "asus": [
        {"title": "ASUS Terms of Use Notice", "url": "https://www.asus.com/terms_of_use_notice_privacy_policy/official-site/", "snippet": "Governs ROG gaming hardware, MyASUS utilities, Armoury Crate, and warranty terms."},
        {"title": "ASUS Privacy Policy", "url": "https://www.asus.com/terms_of_use_notice_privacy_policy/privacy_policy/", "snippet": "Covers hardware serial registration, driver telemetry, and cloud backup services."},
    ],
    "logitech": [
        {"title": "Logitech Terms of Use", "url": "https://www.logitech.com/en-in/tos/terms", "snippet": "Governs Logi Options+, G HUB gaming peripherals, webcam software, and device sales."},
        {"title": "Logitech Privacy Policy", "url": "https://www.logitech.com/en-in/legal/privacy-policy", "snippet": "Details peripheral firmware updates, macro cloud sync, and optional usage telemetry."},
    ],
    "razer": [
        {"title": "Razer Terms of Service", "url": "https://www.razer.com/legal/terms-conditions", "snippet": "Governs Razer Synapse, Chroma RGB cloud profiles, Razer Gold currency, and hardware."},
        {"title": "Razer Privacy Policy", "url": "https://www.razer.com/legal/privacy-policy", "snippet": "Covers peripheral telemetry, Razer Gold payment verification, and game launcher data."},
    ],
    "garmin": [
        {"title": "Garmin Terms of Use", "url": "https://www.garmin.com/en-US/legal/terms-of-use/", "snippet": "Governs Garmin Connect fitness tracking, GPS navigation maps, and Connect IQ apps."},
        {"title": "Garmin Privacy Policy", "url": "https://www.garmin.com/en-US/privacy/connect/", "snippet": "Details biometric heart-rate/sleep metrics, GPS workout routes, and health data controls."},
    ],
    "peloton": [
        {"title": "Peloton Terms of Service", "url": "https://www.onepeloton.com/terms-of-service", "snippet": "Governs Bike/Tread All-Access memberships, live fitness classes, and mandatory arbitration."},
        {"title": "Peloton Privacy Policy", "url": "https://www.onepeloton.com/privacy-policy", "snippet": "Covers workout heart-rate telemetry, leaderboard profiles, and camera/mic permissions."},
    ],
    "nike": [
        {"title": "Nike Terms of Use", "url": "https://agreementservice.svs.nike.com/us/en_us/rest/agreement?agreementType=termsOfUse&uxId=com.nike.commerce.nikedotcom.web&country=US&language=en&requestType=redirect", "snippet": "Governs Nike.com, SNKRS app drops, Nike Run Club, and Nike Training Club."},
        {"title": "Nike Privacy Policy", "url": "https://agreementservice.svs.nike.com/us/en_us/rest/agreement?agreementType=privacyPolicy&uxId=com.nike.commerce.nikedotcom.web&country=US&language=en&requestType=redirect", "snippet": "Covers run GPS tracking, sneaker drop anti-bot checks, and personalized retail ads."},
    ],
    "ikea": [
        {"title": "IKEA Terms and Conditions", "url": "https://www.ikea.com/us/en/customer-service/terms-conditions/", "snippet": "Governs furniture orders, IKEA Family loyalty perks, Home Smart IoT, and returns."},
        {"title": "IKEA Privacy Notice", "url": "https://www.ikea.com/us/en/customer-service/privacy-policy/", "snippet": "Details room planner saves, smart home hub telemetry, and delivery tracking."},
    ],
    "khanacademy": [
        {"title": "Khan Academy Terms of Service", "url": "https://www.khanacademy.org/about/tos", "snippet": "Governs free K-12 & college educational courses, Khanmigo AI tutor, and teacher tools."},
        {"title": "Khan Academy Privacy Policy", "url": "https://www.khanacademy.org/about/privacy-policy", "snippet": "Covers COPPA/FERPA student privacy protections, learning progress, and zero ad sales."},
    ],
    "codecademy": [
        {"title": "Codecademy Terms of Service", "url": "https://www.codecademy.com/terms", "snippet": "Governs interactive coding workspaces, Pro career paths, and Skillsoft certifications."},
        {"title": "Codecademy Privacy Policy", "url": "https://www.codecademy.com/policy", "snippet": "Details code exercise telemetry, learner progress, and Skillsoft enterprise sharing."},
    ],
    "n8n": [
        {"title": "n8n Terms of Service", "url": "https://n8n.io/legal/", "snippet": "Governs n8n Cloud workflow automation, AI agent nodes, and Sustainable Use License."},
        {"title": "n8n Privacy Policy", "url": "https://n8n.io/legal/#privacy", "snippet": "Covers workflow execution metadata, encrypted OAuth credentials, and EU data residency."},
    ],
    "calendly": [
        {"title": "Calendly Customer Terms & Conditions", "url": "https://calendly.com/legal/customer-terms-conditions", "snippet": "Governs automated meeting scheduling, round-robin team routing, and Stripe payment links."},
        {"title": "Calendly Privacy Notice", "url": "https://calendly.com/legal/privacy-notice", "snippet": "Details calendar free/busy sync permissions, invitee booking data, and integrations."},
    ],
    "typeform": [
        {"title": "Typeform Terms of Service", "url": "https://www.typeform.com/terms-service/", "snippet": "Governs conversational forms, surveys, VideoAsk, and respondent data ownership."},
        {"title": "Typeform Privacy Policy", "url": "https://admin.typeform.com/to/dwk6gt", "snippet": "Covers form submission storage, respondent tracking opt-outs, and GDPR compliance."},
    ],
}

# Aliases and colloquial abbreviations mapping to canonical directory keys
DIRECTORY_ALIASES: Dict[str, str] = {
    # Tech Giants & Social
    "fb": "facebook",
    "ig": "instagram",
    "insta": "instagram",
    "yt": "youtube",
    "msft": "microsoft",
    "ms": "microsoft",
    "office": "microsoft",
    "office365": "microsoft",
    "microsoft365": "microsoft",
    "amzn": "amazon",
    "goog": "google",
    "alphabet": "google",
    "gsuite": "google",
    "googleworkspace": "google",
    "twtr": "twitter",
    "tweet": "twitter",
    "snap": "snapchat",
    "psn": "playstation",
    "playstationnetwork": "playstation",
    "xboxlive": "xbox",
    "gamepass": "xbox",
    "xboxgamepass": "xbox",

    # AI Platforms, Labs & Coding Agents
    "chatgpt": "openai",
    "gpt": "openai",
    "sora": "openai",
    "claude": "anthropic",
    "gemini": "google",
    "deepmind": "google",
    "copilot": "microsoft",
    "githubcopilot": "github",
    "anysphere": "cursor",
    "grok": "xai",
    "deepseekr1": "deepseek",
    "deepseekv3": "deepseek",
    "alibabaqwen": "qwen",
    "tongyi": "qwen",
    "codeium": "windsurf",
    "bolt": "stackblitz",
    "boltnew": "stackblitz",
    "devin": "cognition",
    "cognitionai": "cognition",
    "cody": "sourcegraph",
    "together": "togetherai",
    "fireworks": "fireworksai",
    "fal": "falai",
    "weightsandbiases": "wandb",
    "scale": "scaleai",
    "luma": "lumaai",
    "dreammachine": "lumaai",
    "pi": "inflection",
    "hf": "huggingface",

    # Gaming, Studios & Platforms
    "gta": "rockstargames",
    "gta5": "rockstargames",
    "gtav": "rockstargames",
    "gta6": "rockstargames",
    "gtavi": "rockstargames",
    "gtaonline": "rockstargames",
    "grandtheftauto": "rockstargames",
    "grand theft auto": "rockstargames",
    "rockstar": "rockstargames",
    "rockstar games": "rockstargames",
    "socialclub": "rockstargames",
    "reddead": "rockstargames",
    "red dead": "rockstargames",
    "rdr2": "rockstargames",
    "take2": "taketwo",
    "take2games": "taketwo",
    "taketwointeractive": "taketwo",
    "2k": "2kgames",
    "nba2k": "2kgames",
    "cod": "activision",
    "callofduty": "activision",
    "call of duty": "activision",
    "warzone": "activision",
    "zenimax": "bethesda",
    "elderscrolls": "bethesda",
    "fallout": "bethesda",
    "starfield": "bethesda",
    "cdpr": "cdprojektred",
    "cyberpunk": "cdprojektred",
    "witcher": "cdprojektred",
    "gogcom": "gog",
    "ffxiv": "squareenix",
    "finalfantasy": "squareenix",
    "pubg": "krafton",
    "clashofclans": "supercell",
    "brawlstars": "supercell",
    "clashroyale": "supercell",
    "mojang": "minecraft",
    "lol": "riotgames",
    "leagueoflegends": "riotgames",
    "valorant": "riotgames",
    "wow": "blizzard",
    "worldofwarcraft": "blizzard",
    "battlenet": "blizzard",
    "overwatch": "blizzard",
    "fortnite": "epicgames",
    "epic": "epicgames",
    "ue5": "unrealengine",
    "unreal": "unrealengine",
    "rustgame": "facepunch",
    "warthunder": "gaijin",
    "worldoftanks": "wargaming",
    "baldursgate": "larian",
    "paradoxplaza": "paradox",
    "overwolf": "curseforge",
    "itch": "itchio",
    "chess": "chesscom",
    "nvidia geforce now": "geforcenow",

    # Programming Languages & Foundations
    "py": "python",
    "pypi": "python",
    "psf": "python",
    "node": "nodejs",
    "openjs": "nodejs",
    "js": "nodejs",
    "javascript": "nodejs",
    "npmjs": "npm",
    "ts": "typescript",
    "rust": "rustlang",
    "crates": "rustlang",
    "cratesio": "rustlang",
    "go": "golang",
    "jdk": "java",
    "openjdk": "java",
    "csharp": "dotnet",
    "c#": "dotnet",
    ".net": "dotnet",
    "nuget": "dotnet",
    "c++": "cpp",
    "cplusplus": "cpp",
    "isocpp": "cpp",
    "rubygems": "ruby",
    "rails": "ruby",
    "packagist": "php",
    "composer": "php",
    "dart": "flutter",
    "pubdev": "flutter",
    "hexpm": "elixir",
    "erlang": "elixir",
    "julialang": "julia",
    "linux": "linuxfoundation",
    "cncf": "linuxfoundation",
    "ubuntu": "canonical",
    "rhel": "redhat",
    "openshift": "redhat",
    "arch": "archlinux",
    "aur": "archlinux",
    "brew": "homebrew",

    # Dev & Cloud
    "gh": "github",
    "gl": "gitlab",
    "bitbucket": "atlassian",
    "jira": "atlassian",
    "confluence": "atlassian",
    "cf": "cloudflare",
    "gcp": "googlecloud",
    "so": "stackoverflow",
    "ddg": "duckduckgo",
    "dockerhub": "docker",
    "wp": "wordpress",
    "automattic": "wordpress",
    "terraform": "hashicorp",
    "vault": "hashicorp",
    "visualstudio": "vscode",
    "visualstudiocode": "vscode",
    "sonar": "sonarqube",
    "sonarcloud": "sonarqube",
    "dev": "devto",
    "forem": "devto",
    "okta": "auth0",

    # VPNs, Privacy, Security & Browsers
    "protonvpn": "proton",
    "protonmail": "proton",
    "pia": "privateinternetaccess",
    "tor": "torproject",
    "warp": "cloudflarewarp",
    "1.1.1.1": "cloudflarewarp",
    "browsercompany": "arc",
    "firefox": "mozilla",

    # Media, Streaming & Entertainment
    "prime": "amazon",
    "primevideo": "primevideo",
    "prime video": "primevideo",
    "amazon prime": "primevideo",
    "amazon prime video": "primevideo",
    "applemusic": "apple",
    "appletv": "apple",
    "disney": "disneyplus",
    "disney+": "disneyplus",
    "hbo": "max",
    "hbomax": "max",
    "paramount": "paramountplus",
    "paramount+": "paramountplus",
    "everand": "scribd",
    "ko-fi": "kofi",

    # Crypto, Finance & Banking
    "gemini exchange": "geminiexchange",
    "consensys": "metamask",
    "eth": "ethereum",
    "sol": "solana",
    "jpmorgan": "chase",
    "bofa": "bankofamerica",
    "boa": "bankofamerica",
    "capone": "capitalone",
    "amex": "americanexpress",
    "charlesschwab": "schwab",
    "ibkr": "interactivebrokers",

    # News & Knowledge
    "theeconomist": "economist",
    "hn": "hackernews",
    "ycombinator": "hackernews",
    "wayback": "archiveorg",
    "internetarchive": "archiveorg",
    "condenast": "wired",
    "voxmedia": "theverge",

    # Rideshare & E-commerce
    "eats": "ubereats",
    "prime shipping": "amazon",
    "door dash": "doordash",
    "insta cart": "instacart",
    "myntra store": "myntra",
    "myntra app": "myntra",

    # Telecom, Media & SaaS
    "xfinity": "comcast",
    "spacex": "starlink",
    "nyt": "nytimes",
    "wapo": "washingtonpost",
    "guardian": "theguardian",
    "sf": "salesforce",
    "crm": "salesforce",
    "vzw": "verizon",
    "t-mobile": "tmobile",
    "tmo": "tmobile",
    "at&t": "att",

    # Additional E-commerce, Quick-Commerce & Retail Delivery
    "fk": "flipkart",
    "flipkart app": "flipkart",
    "meesho app": "meesho",
    "swiggy app": "swiggy",
    "swiggy instamart": "instamart",
    "swiggyinstamart": "instamart",
    "swiggy-instamart": "instamart",
    "grofers": "blinkit",
    "blinkit app": "blinkit",
    "zepto app": "zepto",
    "zeptonow": "zepto",
    "bb": "bigbasket",
    "bbdaily": "bigbasket",
    "big basket": "bigbasket",
    "snap deal": "snapdeal",
    "jio mart": "jiomart",
    "tata cliq": "tatacliq",
    "tata cli q": "tatacliq",
    "cliq": "tatacliq",

    # Additional Streaming & Entertainment
    "hotstar": "jiohotstar",
    "disney hotstar": "jiohotstar",
    "disneyhotstar": "jiohotstar",
    "jio hotstar": "jiohotstar",
    "jio cinema": "jiocinema",
    "jiotv": "jiocinema",
    "crunchy roll": "crunchyroll",
    "funimation": "crunchyroll",
    "sony liv": "sonyliv",
    "liv": "sonyliv",
    "zee 5": "zee5",
    "zee": "zee5",

    # Additional Telecom
    "reliance jio": "jio",
    "jio telecom": "jio",
    "reliance": "jio",
    "bharti airtel": "airtel",
    "airtel xstream": "airtel",
    "vodafone": "vi",
    "vodafone idea": "vi",
    "idea": "vi",
    "myvi": "vi",
    "vodafoneidea": "vi",

    # Additional Fintech, Travel & Rideshare
    "phone pe": "phonepe",
    "phone-pe": "phonepe",
    "pay tm": "paytm",
    "one97": "paytm",
    "cred club": "cred",
    "dreamplug": "cred",
    "groww app": "groww",
    "nextbillion": "groww",
    "kite": "zerodha",
    "zerodha kite": "zerodha",
    "ola cabs": "ola",
    "olacabs": "ola",
    "mmt": "makemytrip",
    "make my trip": "makemytrip",
}


def search_known_directory(query: str) -> List[Dict[str, str]]:
    """
    Search the authoritative directory for matching company policy documents.
    Supports exact matching, alias lookup, tokenized matching, and clean substring detection.
    """
    clean = query.strip().lower()
    if not clean:
        return []

    # Strip common web affixes: "www.", ".com", ".io", ".org", "https://", "http://", trailing path
    clean_domain = re.sub(r"^https?://", "", clean)
    clean_domain = re.sub(r"^www\.", "", clean_domain)
    clean_domain = re.sub(r"/.*$", "", clean_domain)
    clean_domain = re.sub(
        r"\.(com|org|net|io|ai|app|co|dev|so|me|tv|in|club|gg|sh|fm|tech|cloud|uk|de|fr|ch|jp|ca|au)$",
        "",
        clean_domain,
    ).strip()
    clean_alphanumeric = re.sub(r"[^a-z0-9]", "", clean)

    matched_key: Optional[str] = None

    # 1. Direct key match
    if clean in KNOWN_DIRECTORY:
        matched_key = clean
    elif clean_domain in KNOWN_DIRECTORY:
        matched_key = clean_domain
    elif clean_alphanumeric in KNOWN_DIRECTORY:
        matched_key = clean_alphanumeric

    # 2. Alias match
    if not matched_key:
        if clean in DIRECTORY_ALIASES:
            matched_key = DIRECTORY_ALIASES[clean]
        elif clean_alphanumeric in DIRECTORY_ALIASES:
            matched_key = DIRECTORY_ALIASES[clean_alphanumeric]
        elif clean_domain in DIRECTORY_ALIASES:
            matched_key = DIRECTORY_ALIASES[clean_domain]

    # 3. Token-based and substring match (e.g. "discord web" -> discord, "epic games store" -> epicgames)
    if not matched_key:
        tokens = re.findall(r"[a-z0-9]+", clean)
        for token in tokens:
            if token in KNOWN_DIRECTORY:
                matched_key = token
                break
            if token in DIRECTORY_ALIASES:
                matched_key = DIRECTORY_ALIASES[token]
                break

    # 4. Fallback substring boundary match
    if not matched_key:
        for k in KNOWN_DIRECTORY:
            # Check if key is a standalone word or major substring
            if k == clean_alphanumeric or (len(k) >= 4 and k in clean_alphanumeric) or (len(clean_alphanumeric) >= 4 and clean_alphanumeric in k):
                matched_key = k
                break

    if matched_key and matched_key in KNOWN_DIRECTORY:
        candidates = []
        for item in KNOWN_DIRECTORY[matched_key]:
            candidates.append({
                "title": item["title"],
                "url": item["url"],
                "snippet": item.get("snippet", ""),
                "source": "known_directory",
            })
        return candidates

    return []
