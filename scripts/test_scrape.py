"""Manual scraper test — run to verify scrapers work."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_indeed():
    from backend.scrapers.indeed import IndeedScraper
    scraper = IndeedScraper()
    jobs = await scraper.search_jobs(
        roles=["Data Scientist"],
        location="Redmond, WA",
        max_results=5,
    )
    print(f"\n=== Indeed: {len(jobs)} jobs ===")
    for j in jobs:
        print(f"  [{j.external_id}] {j.title} @ {j.company} | {j.location} | easy_apply={j.has_easy_apply}")
    return jobs


async def test_linkedin():
    from backend.scrapers.linkedin import LinkedInScraper
    scraper = LinkedInScraper()
    jobs = await scraper.search_jobs(
        roles=["Data Scientist"],
        location="Redmond, WA",
        max_results=5,
    )
    print(f"\n=== LinkedIn: {len(jobs)} jobs ===")
    for j in jobs:
        print(f"  [{j.external_id}] {j.title} @ {j.company} | {j.location} | easy_apply={j.has_easy_apply}")
    return jobs


if __name__ == "__main__":
    platform = sys.argv[1] if len(sys.argv) > 1 else "both"
    if platform in ("indeed", "both"):
        asyncio.run(test_indeed())
    if platform in ("linkedin", "both"):
        asyncio.run(test_linkedin())
