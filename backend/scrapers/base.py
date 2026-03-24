"""Abstract base scraper and shared data structures."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class RawJobData:
    source: str
    external_id: str
    url: str
    title: str
    company: str
    location: Optional[str] = None
    remote_type: Optional[str] = None     # remote | hybrid | onsite
    employment_type: Optional[str] = None
    seniority: Optional[str] = None
    description: Optional[str] = None
    salary_range: Optional[str] = None
    posted_date: Optional[str] = None
    has_easy_apply: bool = False


class AbstractScraper(ABC):
    @abstractmethod
    async def search_jobs(self, roles: list[str], location: str, max_results: int) -> list[RawJobData]:
        """Search for jobs and return raw job data."""
        pass

    def parse_remote_type(self, text: str) -> str:
        t = text.lower()
        if "remote" in t:
            return "remote"
        if "hybrid" in t:
            return "hybrid"
        return "onsite"

    def parse_employment_type(self, text: str) -> str:
        t = text.lower()
        if "full" in t:
            return "full-time"
        if "part" in t:
            return "part-time"
        if "contract" in t or "contractor" in t:
            return "contract"
        if "intern" in t:
            return "internship"
        return "full-time"

    def parse_seniority(self, title: str) -> str:
        t = title.lower()
        if any(k in t for k in ["senior", "sr.", "sr ", "lead", "principal", "staff", "director"]):
            return "senior"
        if any(k in t for k in ["junior", "jr.", "jr ", "entry", "associate", "graduate", "intern"]):
            return "entry"
        return "mid"
