import json
import os

COOKIE_DIR = os.path.join(os.path.dirname(__file__), "data", "cookies")

# Fields accepted by Playwright's add_cookies / BrowserContext.add_cookies
_PLAYWRIGHT_COOKIE_FIELDS = {
    "name", "value", "domain", "path", "expires",
    "httpOnly", "secure", "sameSite",
}

_VALID_SAMESITE = {"Strict", "Lax", "None"}


def _sanitize_cookie(cookie: dict) -> dict:
    """Strip unknown fields and normalize sameSite for Playwright."""
    out = {k: v for k, v in cookie.items() if k in _PLAYWRIGHT_COOKIE_FIELDS}
    if "sameSite" in out and out["sameSite"] not in _VALID_SAMESITE:
        out["sameSite"] = "None"
    return out


def _path(domain: str) -> str:
    os.makedirs(COOKIE_DIR, exist_ok=True)
    safe = domain.replace("/", "_").replace(":", "_")
    return os.path.join(COOKIE_DIR, f"{safe}.json")


def save_cookies(domain: str, cookies: list) -> None:
    with open(_path(domain), "w") as f:
        json.dump(cookies, f, indent=2)


def load_cookies(domain: str) -> list:
    path = _path(domain)
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [_sanitize_cookie(c) for c in json.load(f)]


def delete_cookies(domain: str) -> bool:
    path = _path(domain)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False


def list_domains() -> list[str]:
    if not os.path.exists(COOKIE_DIR):
        return []
    return [
        f[:-5]  # strip .json
        for f in os.listdir(COOKIE_DIR)
        if f.endswith(".json")
    ]
