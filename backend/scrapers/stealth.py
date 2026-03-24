"""Playwright stealth helpers — anti-detection layer."""
import random
from pathlib import Path
from playwright.async_api import async_playwright, BrowserContext, Page

PROFILE_DIR = Path(__file__).parent.parent / "data" / "browser_profile"
SCREENSHOTS_DIR = Path(__file__).parent.parent / "data" / "screenshots"

VIEWPORTS = [
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1366, "height": 768},
    {"width": 1536, "height": 864},
    {"width": 1280, "height": 800},
]

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
]


async def create_stealth_context(playwright) -> BrowserContext:
    """Create a persistent Playwright browser context with stealth settings."""
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

    viewport = random.choice(VIEWPORTS)
    user_agent = random.choice(USER_AGENTS)

    context = await playwright.chromium.launch_persistent_context(
        str(PROFILE_DIR),
        headless=True,
        viewport=viewport,
        user_agent=user_agent,
        locale="en-US",
        timezone_id="America/Los_Angeles",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
        ],
    )

    # Patch navigator.webdriver to undefined
    await context.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3] });
        Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
        window.chrome = { runtime: {} };
    """)

    return context


async def human_delay(min_s: float = 1.5, max_s: float = 4.0):
    import asyncio
    await asyncio.sleep(random.uniform(min_s, max_s))


async def human_scroll(page: Page, times: int = 3):
    """Simulate human scrolling behavior."""
    for _ in range(times):
        await page.mouse.wheel(0, random.randint(300, 700))
        await human_delay(0.5, 1.5)


async def is_challenge_page(page: Page) -> bool:
    """Detect CAPTCHA or bot challenge pages."""
    title = await page.title()
    url = page.url
    title_lower = title.lower()
    return any(kw in title_lower or kw in url for kw in [
        "security check", "captcha", "are you a robot", "challenge", "verify you"
    ])


async def take_screenshot(page: Page, label: str):
    """Save a screenshot for debugging."""
    path = SCREENSHOTS_DIR / f"{label}.png"
    await page.screenshot(path=str(path))
    print(f"[stealth] Screenshot saved: {path}")
