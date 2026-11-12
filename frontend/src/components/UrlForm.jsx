import React, { useState, useEffect, useMemo } from "react";
import {
  ArrowRight,
  Loader2,
  Globe,
  Search,
  Shield,
  AlertCircle,
  X,
  FileText,
} from "lucide-react";

const SAMPLE_POLICIES = [
  {
    name: "GitHub Terms",
    url: "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
  },
  { name: "Discord Terms", url: "https://discord.com/terms" },
  {
    name: "Reddit Agreement",
    url: "https://redditinc.com/policies/user-agreement",
  },
  {
    name: "Spotify Terms",
    url: "https://www.spotify.com/legal/end-user-agreement/",
  },
];

function deriveTitleFromUrl(urlStr) {
  if (!urlStr) return "";
  try {
    const clean = urlStr.trim();
    if (clean.startsWith("/")) {
      const seg = clean.replace(/^\/+|\/+$/g, "").split("/")[0] || "Terms";
      return seg.charAt(0).toUpperCase() + seg.slice(1);
    }
    const parsed = new URL(
      clean.startsWith("http://") || clean.startsWith("https://")
        ? clean
        : `https://${clean}`,
    );
    const host = parsed.hostname.replace(/^www\./, "");
    const parts = host.split(".");
    let brand =
      parts.length > 2 ? parts[parts.length - 2] : parts[0] || "";
    if (brand) {
      brand = brand.charAt(0).toUpperCase() + brand.slice(1);
    }
    const path = parsed.pathname.toLowerCase();
    let docType = "Terms of Service";
    if (path.includes("privacy")) {
      docType = "Privacy Policy";
    } else if (path.includes("cookie")) {
      docType = "Cookie Policy";
    } else if (path.includes("security")) {
      docType = "Security Policy";
    } else if (
      path.includes("user-agreement") ||
      path.includes("user_agreement")
    ) {
      docType = "User Agreement";
    } else if (path.includes("acceptable") || path.includes("aup")) {
      docType = "Acceptable Use Policy";
    } else if (
      path.includes("terms") ||
      path.includes("tos") ||
      path.includes("legal")
    ) {
      docType = "Terms of Service";
    } else {
      docType = "Policy Agreement";
    }
    const derived = brand ? `${brand} ${docType}` : docType;
    return derived.slice(0, 200);
  } catch {
    return "";
  }
}

function canonicalizeUrl(urlStr) {
  if (!urlStr) return "";
  let clean = urlStr.trim();
  if (clean.startsWith("/")) {
    const cleanPath = clean
      .replace(/\/+/g, "/")
      .replace(/\/+$/, "")
      .toLowerCase();
    return cleanPath || "/";
  }
  if (!clean.startsWith("http://") && !clean.startsWith("https://")) {
    clean = "https://" + clean;
  }
  try {
    const parsed = new URL(clean);
    let host = parsed.hostname.toLowerCase();
    if (host.startsWith("www.")) {
      host = host.slice(4);
    }
    let path = parsed.pathname
      .replace(/\/+/g, "/")
      .replace(/\/+$/, "")
      .toLowerCase();
    if (!path) {
      path = "/";
    }
    return `https://${host}${path}`;
  } catch {
    return clean.toLowerCase().replace(/\/+$/, "");
  }
}

export default function UrlForm({
  onAnalyze,
  loading,
  onOpenDiscovery,
  trackedPolicies = [],
}) {
  const [mode, setMode] = useState("url"); // 'url' | 'paste'
  const [url, setUrl] = useState("");
  const [pastedUrl, setPastedUrl] = useState("");
  const [pastedTitle, setPastedTitle] = useState("");
  const [userModifiedTitle, setUserModifiedTitle] = useState(false);
  const [rawText, setRawText] = useState("");
  const [error, setError] = useState("");
  const [elapsed, setElapsed] = useState(0);

  const systemUrls = useMemo(() => {
    const set = new Set();
    SAMPLE_POLICIES.forEach((s) => {
      const c = canonicalizeUrl(s.url);
      if (c) set.add(c);
    });
    set.add(canonicalizeUrl("/terms"));
    set.add(canonicalizeUrl("/privacy"));
    (trackedPolicies || []).forEach((pol) => {
      const isUser =
        pol.provenance === "user_pasted" ||
        pol.latest_analysis?.provenance === "user_pasted" ||
        pol.canonical_url?.startsWith("user://");
      if (!isUser) {
        if (pol.canonical_url) set.add(canonicalizeUrl(pol.canonical_url));
        if (pol.raw_url) set.add(canonicalizeUrl(pol.raw_url));
      }
    });
    return set;
  }, [trackedPolicies]);

  const isSystemUrl = (urlStr) => {
    if (!urlStr) return false;
    const canon = canonicalizeUrl(urlStr);
    return Boolean(canon && systemUrls.has(canon));
  };

  useEffect(() => {
    if (!loading) {
      return;
    }
    const start = Date.now();
    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - start) / 1000));
    }, 500);
    return () => clearInterval(timer);
  }, [loading]);

  const handleSubmitUrl = (e) => {
    e.preventDefault();
    setError("");

    const clean = url.trim();
    if (!clean) {
      setError("Enter a policy URL");
      return;
    }

    if (clean.length > 2048) {
      setError(
        "Policy URL exceeds maximum supported length (2,048 characters)",
      );
      return;
    }

    if (
      !clean.startsWith("http://") &&
      !clean.startsWith("https://") &&
      !clean.startsWith("/")
    ) {
      setError("Enter a valid URL (starting with https://, http://, or /)");
      return;
    }

    setElapsed(0);
    onAnalyze(clean);
  };

  const handlePastedUrlChange = (e) => {
    const newUrl = e.target.value;
    setPastedUrl(newUrl);

    if (isSystemUrl(newUrl)) {
      setError(
        "This URL already exists as a system-maintained policy. User text paste is reserved for policies that cannot be retrieved automatically. Use the System Maintained tab or URL Link analysis instead.",
      );
      return;
    }
    if (error) setError("");

    if (!userModifiedTitle || !pastedTitle.trim()) {
      const derived = deriveTitleFromUrl(newUrl);
      if (derived) {
        setPastedTitle(derived);
      }
    }
  };

  const handlePastedTitleChange = (e) => {
    setPastedTitle(e.target.value);
    setUserModifiedTitle(e.target.value.trim().length > 0);
  };

  const handleSubmitPaste = (e) => {
    e.preventDefault();
    setError("");

    const cleanUrl = pastedUrl.trim();
    if (!cleanUrl) {
      setError("Policy URL is mandatory (e.g. https://company.com/terms)");
      return;
    }

    if (cleanUrl.length > 2048) {
      setError(
        "Policy URL exceeds maximum supported length (2,048 characters)",
      );
      return;
    }

    if (
      !cleanUrl.startsWith("http://") &&
      !cleanUrl.startsWith("https://") &&
      !cleanUrl.startsWith("/")
    ) {
      setError("Enter a valid URL (starting with https://, http://, or /)");
      return;
    }

    if (isSystemUrl(cleanUrl)) {
      setError(
        "This URL already exists as a system-maintained policy. User text paste is reserved for policies that cannot be retrieved automatically. Use the System Maintained tab or URL Link analysis instead.",
      );
      return;
    }

    if (pastedTitle.trim().length > 200) {
      setError(
        "Agreement title exceeds maximum allowed length (200 characters)",
      );
      return;
    }

    const cleanText = rawText.trim();
    if (!cleanText) {
      setError("Please paste the policy agreement text");
      return;
    }

    if (cleanText.length < 100) {
      setError(
        `Pasted text is too short (${cleanText.length} chars). Minimum 100 characters required for clause risk auditing.`,
      );
      return;
    }

    const finalTitle =
      pastedTitle.trim() || deriveTitleFromUrl(cleanUrl) || "Policy Agreement";
    setElapsed(0);
    onAnalyze({
      url: cleanUrl,
      raw_text: cleanText,
      title: finalTitle,
    });
  };

  const handleSelectSample = (sampleUrl) => {
    setUrl(sampleUrl);
    setError("");
  };

  const getActiveSelfUrl = (path) => {
    if (typeof window !== "undefined" && window.location?.origin) {
      return `${window.location.origin}${path}`;
    }
    return `https://easyfineprint.vercel.app${path}`;
  };

  const handleTestSelfPolicy = (path) => {
    const fullUrl = getActiveSelfUrl(path);
    setUrl(fullUrl);
    setError("");
    onAnalyze(fullUrl);
  };

  return (
    <div className="w-full">
      <div className="panel rounded-xl p-4 sm:p-6 shadow-sm">
        {/* Input Mode Selector (URL Link vs Direct Paste) */}
        <div className="flex items-center gap-1.5 p-1 bg-[#e5ddcf] dark:bg-zinc-950 rounded-lg border border-[#d5cbba] dark:border-zinc-800 w-fit mb-4">
          <button
            type="button"
            onClick={() => {
              setMode("url");
              setError("");
            }}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === "url"
                ? "bg-[#f5eedf] dark:bg-zinc-800 text-[#1c1917] dark:text-zinc-100 font-medium shadow-xs border border-[#d5cbba] dark:border-zinc-700/60"
                : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#ded6c6]/50 dark:hover:bg-zinc-900/50"
            }`}
          >
            <Globe className="w-3.5 h-3.5" />
            <span>URL Link</span>
          </button>
          <button
            type="button"
            onClick={() => {
              setMode("paste");
              setError("");
            }}
            className={`px-3 py-1.5 rounded-md text-xs font-mono transition-all cursor-pointer flex items-center gap-1.5 ${
              mode === "paste"
                ? "bg-[#f5eedf] dark:bg-zinc-800 text-[#1c1917] dark:text-zinc-100 font-medium shadow-xs border border-[#d5cbba] dark:border-zinc-700/60"
                : "text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 hover:bg-[#ded6c6]/50 dark:hover:bg-zinc-900/50"
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>Paste Text</span>
          </button>
        </div>

        {mode === "url" ? (
          /* URL Form */
          <form
            onSubmit={handleSubmitUrl}
            className="space-y-3.5 sm:space-y-3"
            noValidate
          >
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-2.5">
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-[#78716c] dark:text-zinc-500">
                  <Globe className="w-4 h-4 shrink-0" />
                </div>
                <input
                  type="text"
                  value={url}
                  onChange={(e) => {
                    setUrl(e.target.value);
                    if (error) setError("");
                  }}
                  disabled={loading}
                  maxLength={2048}
                  placeholder="Paste Terms or Privacy Policy URL (or /terms, /privacy)..."
                  autoCapitalize="none"
                  autoCorrect="off"
                  spellCheck="false"
                  className="w-full pl-10 pr-10 py-3 sm:py-2.5 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-black hover:border-black/80 dark:border-zinc-300 dark:hover:border-zinc-200 text-[#1c1917] dark:text-zinc-100 placeholder-[#78716c] dark:placeholder-zinc-500 text-base sm:text-sm focus:outline-none focus:border-black dark:focus:border-white focus:ring-1 focus:ring-black/40 dark:focus:ring-white/40 transition-colors disabled:opacity-50 font-mono min-h-[44px] shadow-xs"
                />
                {url && !loading && (
                  <button
                    type="button"
                    onClick={() => {
                      setUrl("");
                      if (error) setError("");
                    }}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-[#78716c] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                    title="Clear URL input"
                    aria-label="Clear URL input"
                  >
                    <X className="w-4 h-4 shrink-0" />
                  </button>
                )}
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto px-5 py-3 sm:py-2.5 rounded-lg bg-[#1c1917] hover:bg-[#292524] active:bg-black text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:active:bg-zinc-200 dark:text-zinc-950 font-medium text-sm sm:text-xs font-mono flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer shrink-0 min-h-[44px] active:scale-[0.99] border border-[#1c1917] dark:border-zinc-300 shadow-xs"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 sm:w-3.5 sm:h-3.5 animate-spin" />
                    <span>Processing...</span>
                  </>
                ) : (
                  <>
                    <span>Analyze Policy</span>
                    <ArrowRight className="w-4 h-4 sm:w-3.5 sm:h-3.5" />
                  </>
                )}
              </button>
            </div>

            {loading && (
              <div className="p-3.5 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-[#d5cbba] dark:border-zinc-800 space-y-2.5 font-mono text-xs">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 text-[#1c1917] dark:text-zinc-300">
                  <span className="flex items-start sm:items-center gap-2">
                    <Loader2 className="w-3.5 h-3.5 animate-spin text-[#78716c] dark:text-zinc-400 shrink-0 mt-0.5 sm:mt-0" />
                    <span className="leading-tight">
                      {elapsed < 4
                        ? "Fetching document & validating security rules..."
                        : elapsed < 8
                          ? "Extracting text & calculating baseline hash..."
                          : elapsed < 30
                            ? "Evaluating policy clauses with Gemma 4..."
                            : "Verifying verbatim citations against source text..."}
                    </span>
                  </span>
                  <span className="text-[#5c5549] dark:text-zinc-400 font-semibold self-end sm:self-auto shrink-0 bg-[#e5ddcf] dark:bg-zinc-900 px-2 py-0.5 rounded border border-[#d5cbba] dark:border-zinc-800">
                    {elapsed}s
                  </span>
                </div>
                <div className="flex flex-col xs:flex-row xs:items-center justify-between gap-1 text-[11px] text-[#78716c] dark:text-zinc-500">
                  <span>Single-pass clause evaluation (Gemma 4)</span>
                  <span>
                    {elapsed < 30
                      ? "Realistic estimate: ~20-30s"
                      : "Deep verification in progress..."}
                  </span>
                </div>
                <div className="w-full bg-[#e5ddcf] dark:bg-zinc-900 h-1.5 rounded-full overflow-hidden border border-[#d5cbba] dark:border-zinc-800/80">
                  <div
                    className="bg-[#1c1917] dark:bg-zinc-300 h-full transition-all duration-300"
                    style={{
                      width: `${Math.min(96, Math.max(8, (elapsed / 35) * 100))}%`,
                    }}
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-900/60 text-rose-800 dark:text-rose-300 text-xs font-mono flex items-center justify-between gap-3 break-words">
                <div className="flex items-center gap-2 min-w-0">
                  <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
                  <span>{error}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setError("")}
                  className="text-rose-600 dark:text-rose-400 hover:text-rose-800 dark:hover:text-rose-200 cursor-pointer p-1 -mr-1 rounded-md hover:bg-rose-500/20 dark:hover:bg-rose-900/40 shrink-0 min-w-[28px] min-h-[28px] flex items-center justify-center active:scale-95 transition-colors"
                  title="Dismiss error"
                  aria-label="Dismiss error"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            {/* Quick samples and discovery */}
            <div className="pt-1 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs text-[#5c5549] dark:text-zinc-400">
              <div className="flex flex-col sm:flex-row sm:items-center gap-2 sm:gap-2 w-full sm:w-auto">
                <span className="text-[#78716c] dark:text-zinc-500 text-[11px] font-mono shrink-0">
                  Samples:
                </span>
                <div className="grid grid-cols-2 gap-2 sm:flex sm:items-center sm:gap-1.5 w-full sm:w-auto">
                  {SAMPLE_POLICIES.map((item) => (
                    <button
                      key={item.name}
                      type="button"
                      onClick={() => handleSelectSample(item.url)}
                      disabled={loading}
                      className="w-full sm:w-auto justify-center px-2.5 py-1.5 sm:py-0.5 rounded-md bg-[#faf5ec] dark:bg-zinc-900 hover:bg-[#e2d9c7] dark:hover:bg-zinc-800 active:bg-[#ded6c6] dark:active:bg-zinc-750 text-[#5c5549] dark:text-zinc-300 hover:text-[#1c1917] dark:hover:text-white transition-colors border border-[#d5cbba] dark:border-zinc-800 cursor-pointer text-xs sm:text-[11px] min-h-[34px] sm:min-h-0 flex items-center active:scale-95 text-center font-mono shadow-2xs"
                    >
                      <span>{item.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              <button
                type="button"
                onClick={onOpenDiscovery}
                className="inline-flex items-center justify-center sm:justify-start gap-1.5 text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-zinc-200 active:text-black dark:active:text-white transition-colors text-xs sm:text-[11px] cursor-pointer w-full sm:w-auto py-1.5 sm:py-0 rounded-md sm:rounded-none bg-[#faf5ec]/60 dark:bg-zinc-950/60 sm:bg-transparent border border-[#d5cbba] dark:border-zinc-800/80 sm:border-0 active:scale-95 min-h-[34px] sm:min-h-0 font-mono shadow-2xs sm:shadow-none"
              >
                <Search className="w-3.5 h-3.5 sm:w-3 sm:h-3 text-[#78716c] dark:text-zinc-500 shrink-0" />
                <span>Lookup by company name</span>
              </button>
            </div>

            {/* Self-Policy Verification */}
            <div className="pt-2 flex flex-wrap items-center gap-2 text-[11px] font-mono text-[#78716c] dark:text-zinc-500">
              <span>Or audit our own policies:</span>
              <div className="flex items-center gap-1.5">
                <button
                  type="button"
                  onClick={() => handleTestSelfPolicy("/terms")}
                  disabled={loading}
                  className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white underline underline-offset-3 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white transition-colors cursor-pointer disabled:opacity-50"
                >
                  Terms of Use
                </button>
                <span className="text-[#bfb4a0] dark:text-zinc-700">&middot;</span>
                <button
                  type="button"
                  onClick={() => handleTestSelfPolicy("/privacy")}
                  disabled={loading}
                  className="text-[#5c5549] dark:text-zinc-400 hover:text-[#1c1917] dark:hover:text-white underline underline-offset-3 decoration-[#bfb4a0] dark:decoration-zinc-700 hover:decoration-[#1c1917] dark:hover:decoration-white transition-colors cursor-pointer disabled:opacity-50"
                >
                  Privacy Policy
                </button>
              </div>
            </div>
          </form>
        ) : (
          /* Direct Text Paste Form */
          <form
            onSubmit={handleSubmitPaste}
            className="space-y-3.5 sm:space-y-3"
            noValidate
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-2.5">
              <div>
                <label className="block text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 mb-1">
                  <span>Policy URL</span> <span className="text-rose-500 dark:text-rose-400">*</span>{" "}
                  <span className="text-[#78716c] dark:text-zinc-500">(max 2,048 chars)</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    required
                    value={pastedUrl}
                    onChange={handlePastedUrlChange}
                    disabled={loading}
                    maxLength={2048}
                    placeholder="https://company.com/terms (mandatory for tracking)"
                    className="w-full pl-3 pr-8 py-2 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-black dark:border-zinc-700 text-[#1c1917] dark:text-zinc-100 placeholder-[#8c8273] dark:placeholder-zinc-500 text-xs focus:outline-none focus:border-black dark:focus:border-zinc-400 font-mono shadow-xs"
                  />
                  {pastedUrl && !loading && (
                    <button
                      type="button"
                      onClick={() => {
                        setPastedUrl("");
                        if (!userModifiedTitle) {
                          setPastedTitle("");
                        }
                        if (error) setError("");
                      }}
                      className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-[#78716c] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                      title="Clear Policy URL"
                      aria-label="Clear Policy URL"
                    >
                      <X className="w-3.5 h-3.5 shrink-0" />
                    </button>
                  )}
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 mb-1 flex items-center justify-between">
                  <span>Agreement Title <span className="text-[#78716c] dark:text-zinc-500">(Optional)</span></span>
                  <span className="text-[#78716c] dark:text-zinc-500 text-[10px]">{pastedTitle.length}/200</span>
                </label>
                <div className="relative">
                  <input
                    type="text"
                    value={pastedTitle}
                    onChange={handlePastedTitleChange}
                    disabled={loading}
                    maxLength={200}
                    placeholder="e.g. Acme Terms of Service"
                    className="w-full pl-3 pr-8 py-2 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-black dark:border-zinc-700 text-[#1c1917] dark:text-zinc-100 placeholder-[#8c8273] dark:placeholder-zinc-500 text-xs focus:outline-none focus:border-black dark:focus:border-zinc-400 font-mono shadow-xs"
                  />
                  {pastedTitle && !loading && (
                    <button
                      type="button"
                      onClick={() => {
                        setPastedTitle("");
                        setUserModifiedTitle(false);
                        if (error) setError("");
                      }}
                      className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-[#78716c] hover:text-[#1c1917] dark:text-zinc-400 dark:hover:text-zinc-100 transition-colors cursor-pointer"
                      title="Clear Agreement Title"
                      aria-label="Clear Agreement Title"
                    >
                      <X className="w-3.5 h-3.5 shrink-0" />
                    </button>
                  )}
                </div>
              </div>
            </div>

            <div>
              <div className="flex items-center justify-between gap-2 text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 mb-1.5">
                <span>Agreement Full Text Body</span>
                <span
                  className={`shrink-0 font-mono ${
                    rawText.trim().length >= 100
                      ? "text-emerald-700 dark:text-emerald-400"
                      : "text-[#78716c] dark:text-zinc-500"
                  }`}
                >
                  {rawText.trim().length} chars (min. 100)
                </span>
              </div>
              <div className="relative">
                <textarea
                  value={rawText}
                  onChange={(e) => {
                    setRawText(e.target.value);
                    if (error) setError("");
                  }}
                  disabled={loading}
                  rows={7}
                  maxLength={500000}
                  placeholder="Paste the raw terms of service or privacy agreement text directly here..."
                  className="w-full p-3 pr-16 rounded-lg bg-[#faf5ec] dark:bg-zinc-950 border border-black dark:border-zinc-700 text-[#1c1917] dark:text-zinc-100 placeholder-[#8c8273] dark:placeholder-zinc-500 text-xs focus:outline-none focus:border-black dark:focus:border-zinc-400 font-mono resize-y min-h-[140px] shadow-xs"
                />
                {rawText && !loading && (
                  <button
                    type="button"
                    onClick={() => {
                      setRawText("");
                      if (error) setError("");
                    }}
                    className="absolute top-2.5 right-2.5 z-10 px-2 py-0.5 rounded bg-[#e5ddcf] hover:bg-[#ded6c6] text-[#5c5549] hover:text-[#1c1917] text-[10px] font-mono border border-[#d5cbba] dark:bg-zinc-900/90 dark:hover:bg-zinc-800 dark:text-zinc-400 dark:hover:text-zinc-200 dark:border-zinc-700/80 transition-colors cursor-pointer shadow-xs"
                    title="Clear agreement text body"
                    aria-label="Clear agreement text body"
                  >
                    clear
                  </button>
                )}
              </div>
            </div>

            {/* Provenance Notice */}
            <div className="p-2.5 rounded-lg bg-[#e5ddcf]/60 dark:bg-zinc-900/60 border border-[#d5cbba] dark:border-zinc-800 text-[11px] font-mono text-[#5c5549] dark:text-zinc-400 flex items-start gap-2">
              <Shield className="w-3.5 h-3.5 text-[#5c5549] dark:text-zinc-400 shrink-0 mt-0.5" />
              <span>
                Provenance Notice: User-pasted agreements are audited
                statelessly and tagged with a &quot;User-Provided Content&quot;
                notice in compliance and diff records.
              </span>
            </div>

            {error && (
              <div className="p-3 rounded-lg bg-rose-500/10 dark:bg-rose-950/40 border border-rose-300 dark:border-rose-900/60 text-rose-800 dark:text-rose-300 text-xs font-mono flex items-center justify-between gap-3 break-words">
                <div className="flex items-center gap-2 min-w-0">
                  <AlertCircle className="w-4 h-4 text-rose-600 dark:text-rose-400 shrink-0" />
                  <span>{error}</span>
                </div>
                <button
                  type="button"
                  onClick={() => setError("")}
                  className="text-rose-600 hover:text-rose-800 dark:text-rose-400 dark:hover:text-rose-200 cursor-pointer p-1 -mr-1 rounded-md hover:bg-rose-500/20 dark:hover:bg-rose-900/40 shrink-0"
                >
                  <X className="w-3.5 h-3.5" />
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={
                loading ||
                !pastedUrl.trim() ||
                rawText.trim().length < 100 ||
                isSystemUrl(pastedUrl)
              }
              className="w-full sm:w-auto px-5 py-2.5 rounded-lg bg-[#1c1917] hover:bg-[#292524] active:bg-black text-[#faf5ec] dark:bg-zinc-100 dark:hover:bg-white dark:active:bg-zinc-200 dark:text-zinc-950 font-medium text-xs font-mono flex items-center justify-center gap-2 transition-all disabled:opacity-50 cursor-pointer min-h-[42px] border border-[#1c1917] dark:border-zinc-300 shadow-xs"
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>Auditing Pasted Text...</span>
                </>
              ) : (
                <>
                  <span>Audit Pasted Agreement</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>
        )}

        {/* Scope / Privacy note */}
        <div className="mt-4 pt-3 border-t border-[#d5cbba] dark:border-zinc-800/80 flex items-center gap-2 text-[11px] text-[#5c5549] dark:text-zinc-500 font-mono leading-relaxed">
          <Shield className="w-3.5 h-3.5 text-[#78716c] dark:text-zinc-500 shrink-0" />
          <span>
            Supports public Terms &amp; Privacy Policies. Analyzed statelessly
            without storing personal data.
          </span>
        </div>
      </div>
    </div>
  );
}
