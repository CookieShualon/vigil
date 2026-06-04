import asyncio
import base64
import logging
from urllib.parse import urlparse
from playwright.async_api import (
    async_playwright,
    Page,
    Browser,
    BrowserContext,
    Error as PlaywrightError,
    TimeoutError as PlaywrightTimeoutError,
)
from config import VIEWPORT_WIDTH, VIEWPORT_HEIGHT
from cookies import load_cookies, save_cookies

logger = logging.getLogger(__name__)


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
        logger.info(
            "Launching Chromium headless=True executable=%s",
            self._playwright.chromium.executable_path,
        )
        self._browser = await self._playwright.chromium.launch(headless=True)
        logger.info("Chromium launched")
        self._context = await self._browser.new_context(
            viewport={"width": VIEWPORT_WIDTH, "height": VIEWPORT_HEIGHT}
        )
        logger.info("Browser context created viewport=%sx%s", VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        if self._cookie_domain:
            stored = load_cookies(self._cookie_domain)
            if stored:
                logger.info("Loading %s stored cookies for %s", len(stored), self._cookie_domain)
                await self._context.add_cookies(stored)
        self.page = await self._context.new_page()
        self._attach_page_diagnostics(self.page)
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
                    logger.info("Saved %s cookies for %s", len(updated), self._cookie_domain)
            except Exception:
                logger.exception("Failed to save cookies for %s", self._cookie_domain)
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    def _attach_page_diagnostics(self, page: Page) -> None:
        page.on(
            "console",
            lambda msg: logger.warning(
                "Browser console %s: %s", msg.type, msg.text
            ) if msg.type in ("error", "warning") else logger.debug(
                "Browser console %s: %s", msg.type, msg.text
            ),
        )
        page.on("pageerror", lambda exc: logger.error("Browser page error: %s", exc))
        page.on("crash", lambda: logger.error("Browser page crashed url=%s", page.url))
        page.on("close", lambda: logger.info("Browser page closed url=%s", page.url))
        page.on(
            "requestfailed",
            lambda request: logger.error(
                "Browser request failed method=%s url=%s failure=%s",
                request.method,
                request.url,
                request.failure,
            ),
        )
        page.on(
            "response",
            lambda response: logger.info(
                "Browser document response status=%s url=%s",
                response.status,
                response.url,
            ) if response.request.resource_type == "document" else None,
        )

    async def screenshot(self) -> str:
        png_bytes = await self.page.screenshot(type="png")
        logger.debug(
            "Captured screenshot bytes=%s url=%s",
            len(png_bytes),
            self.page.url,
        )
        return base64.b64encode(png_bytes).decode("utf-8")

    async def navigate(self, url: str) -> str:
        if "://" not in url:
            url = f"https://{url}"

        logger.info("Navigating to %s from %s", url, self.page.url)
        try:
            response = await self.page.goto(url, wait_until="domcontentloaded", timeout=30000)
            try:
                await self.page.wait_for_load_state("load", timeout=10000)
            except PlaywrightTimeoutError:
                logger.warning("Timed out waiting for load state after %s", url)
            await self.page.wait_for_timeout(300)
        except PlaywrightError as e:
            logger.exception("Navigation failed url=%s current_url=%s", url, self.page.url)
            raise RuntimeError(
                f"Navigation failed for {url}: {e}. Current browser URL: {self.page.url}"
            ) from e

        status = response.status if response else "no response"
        final_url = self.page.url
        logger.info("Navigation complete url=%s final_url=%s status=%s", url, final_url, status)
        return f"Navigated to {final_url} (status {status})"

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
                logger.exception(
                    "Screenshot stream capture failed url=%s",
                    self.page.url if self.page else None,
                )
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

    async def click_coordinates(self, x: int, y: int) -> str:
        await self.page.mouse.click(x, y)
        return f"Clicked at ({x}, {y})"

    async def type_keys(self, text: str) -> str:
        await self.page.keyboard.type(text)
        return "Typed text"

    async def press_key(self, key: str) -> str:
        await self.page.keyboard.press(key)
        return f"Pressed {key}"
