import json
import os

COOKIE_DIR = os.path.join(os.path.dirname(__file__), "data", "cookies")


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
        return json.load(f)


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
