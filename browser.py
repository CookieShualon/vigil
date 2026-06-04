import asyncio
import base64
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page, Browser, BrowserContext
from config import VIEWPORT_WIDTH, VIEWPORT_HEIGHT
from cookies import load_cookies, save_cookies


def _domain_from_url(url: str) -> str | None:
    try:
        host = urlparse(url).hostname or ""
        # strip leading www.
        return host.removeprefix("www.") if host else None
    except Exception:
        return None


class BrowserSession:
    def __init__(self, cookie_domain: str | None = None):
        self._playwright = None
        self._browser: Browser = None
        self._context: BrowserContext = None
        self.page: Page = None
        self._streaming = False
        self._cookie_domain = cookie_domain

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=True)
        self._context = await self._browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
        )
        if self._cookie_domain:
            stored = load_cookies(self._cookie_domain)
            if stored:
                await self._context.add_cookies(stored)
        self.page = await self._context.new_page()
        await self.page.goto("about:blank")
        self._streaming = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self._streaming = False
        if self._cookie_domain:
            try:
                updated = await self._context.cookies()
                if updated:
                    save_cookies(self._cookie_domain, updated)
            except Exception:
                pass
        await self._browser.close()
        await self._playwright.stop()

    async def screenshot(self) -> str:
        png_bytes = await self.page.screenshot(type="png")
        return base64.b64encode(png_bytes).decode("utf-8")

    async def navigate(self, url: str) -> str:
        await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
        return f"Navigated to {url}"

    async def click(self, selector: str) -> str:
        await self.page.click(selector, timeout=10000)
        return f"Clicked {selector}"

    async def type_text(self, selector: str, text: str) -> str:
        await self.page.click(selector, timeout=10000)
        await self.page.fill(selector, text)
        return f"Typed into {selector}"

    async def scroll(self, direction: str) -> str:
        delta = 400 if direction == "down" else -400
        await self.page.mouse.wheel(0, delta)
        return f"Scrolled {direction}"

    async def wait(self, ms: int) -> str:
        await self.page.wait_for_timeout(ms)
        return f"Waited {ms}ms"

    async def start_screenshot_stream(self, callback, interval_ms=500):
        while self._streaming:
            try:
                screenshot = await self.screenshot()
                callback(screenshot)
            except Exception:
                pass
            await asyncio.sleep(interval_ms / 1000)

    async def extract(self, selector: str, description: str) -> str:
        try:
            elements = await self.page.query_selector_all(selector)
            texts = []
            for el in elements[:20]:
                text = await el.inner_text()
                if text.strip():
                    texts.append(text.strip())
            content = "\n".join(texts) if texts else "(no text found)"
        except Exception as e:
            content = f"(extraction error: {e})"
        return f"Extracted [{description}]: {content}"
