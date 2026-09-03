"""yt-dlp network options: proxy, cookies, and browser impersonation.

Moved verbatim (behavior-preserving) from code/read_channel.py /
read_transcript.py so every script shares one implementation.

Config constants below are the defaults; a script may override them by
assigning to lib.net.<NAME> before calling the helpers, e.g.:

    from lib import net
    net.COOKIES_FILE = "code/cookies.txt"
"""

import os

# ---------------------------------------------------------------------------
# Cookies (needed when YouTube shows "Sign in to confirm you're not a bot").
# Set ONE; leave the other None.
#   COOKIES_FROM_BROWSER - a tuple like ("chrome", None). On Windows, Chrome
#       locks its cookie DB while running, so it often fails; prefer a file.
#   COOKIES_FILE - path to a Netscape cookies.txt (e.g. "code/cookies.txt").
#       Auto-detected below if present.
# ---------------------------------------------------------------------------
COOKIES_FROM_BROWSER = None
COOKIES_FILE = "code/cookies.txt" if os.path.exists("code/cookies.txt") else None

# ---------------------------------------------------------------------------
# Proxy handling. Some machines have HTTP_PROXY/HTTPS_PROXY set system-wide and
# yt-dlp picks them up. NO_PROXY=True forces a direct connection (bypass). To
# use a proxy explicitly, set NO_PROXY=False and PROXY_URL="http://user:pass@host:port".
# ---------------------------------------------------------------------------
NO_PROXY = True
PROXY_URL = None


def cookie_opts():
    """Return the yt-dlp option(s) to attach cookies, if any are configured."""
    opts = {}
    if COOKIES_FILE:
        opts["cookiefile"] = COOKIES_FILE
    elif COOKIES_FROM_BROWSER:
        opts["cookiesfrombrowser"] = COOKIES_FROM_BROWSER
    return opts


def proxy_opts():
    """Return the yt-dlp option(s) controlling proxy use.

    "proxy": "" explicitly tells yt-dlp/urllib to use NO proxy, overriding any
    HTTP_PROXY/HTTPS_PROXY environment variables picked up automatically.
    """
    if NO_PROXY:
        return {"proxy": ""}
    if PROXY_URL:
        return {"proxy": PROXY_URL}
    return {}


def impersonate_opts():
    """yt-dlp browser-impersonation opts (needs curl_cffi); empty if absent.

    Required so YouTube returns subtitle data instead of an empty body. Pass an
    ImpersonateTarget() instance (the string "chrome" raises AssertionError;
    empty lets yt-dlp auto-pick an available target).
    """
    try:
        import curl_cffi  # noqa: F401
        from yt_dlp.networking.impersonate import ImpersonateTarget
        return {"impersonate": ImpersonateTarget()}
    except Exception:
        return {}


def apply_no_proxy_env():
    """If NO_PROXY, strip proxy env vars for this process.

    yt-dlp's own "proxy": "" opt only affects yt-dlp's requests; libraries that
    read HTTP_PROXY/HTTPS_PROXY from the environment (and lowercase variants)
    would still use the proxy. Clearing them here makes ALL code bypass it.
    """
    if not NO_PROXY:
        return
    for var in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
                "ALL_PROXY", "all_proxy"):
        os.environ.pop(var, None)


def net_opts():
    """Merge proxy + cookies + impersonation into one yt-dlp options dict."""
    return {**proxy_opts(), **cookie_opts(), **impersonate_opts()}
