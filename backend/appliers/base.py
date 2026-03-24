"""Abstract base class for job appliers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from playwright.async_api import Page
from backend.scrapers.stealth import take_screenshot


@dataclass
class ApplyResult:
    success: bool
    method: str
    status: str           # submitted | failed | requires_manual
    confirmation_text: Optional[str] = None
    error_detail: Optional[str] = None


class AbstractApplier(ABC):
    @abstractmethod
    async def apply(self, page: Page, job_url: str, resume_path: str) -> ApplyResult:
        pass

    async def _handle_unexpected(self, page: Page, label: str) -> None:
        await take_screenshot(page, label)
        print(f"[applier] Unexpected state at {page.url} — screenshot saved as {label}")
