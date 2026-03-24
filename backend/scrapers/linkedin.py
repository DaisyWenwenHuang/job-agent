"""LinkedIn job scraper using Playwright."""
import asyncio
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from backend.scrapers.base import AbstractScraper, RawJobData
from backend.scrapers.stealth import (
    create_stealth_context, human_delay, human_scroll,
    is_challenge_page, take_screenshot,
)

# LinkedIn work type filter values: 1=onsite, 2=remote, 3=hybrid
WORK_TYPE_FILTER = "f_WT=1%2C2%2C3"


class LinkedInScraper(AbstractScraper):

    async def search_jobs(self, roles: list[str], location: str, max_results: int) -> list[RawJobData]:
        results: list[RawJobData] = []
        seen_ids: set[str] = set()

        async with async_playwright() as pw:
            context = await create_stealth_context(pw)
            page = await context.new_page()

            try:
                for role in roles:
                    if len(results) >= max_results:
                        break
                    role_results = await self._search_role(page, role, location, max_results - len(results), seen_ids)
                    results.extend(role_results)
            except Exception as e:
                print(f"[linkedin] Scraper error: {e}")
                await take_screenshot(page, "linkedin_error")
            finally:
                await context.close()

        print(f"[linkedin] Found {len(results)} jobs")
        return results

    async def _search_role(self, page, role: str, location: str, limit: int, seen_ids: set) -> list[RawJobData]:
        results = []
        encoded_role = quote_plus(role)
        encoded_loc = quote_plus(location)
        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={encoded_role}&location={encoded_loc}"
            f"&{WORK_TYPE_FILTER}&sortBy=DD"
        )

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await human_delay(2, 4)

            if await is_challenge_page(page):
                print(f"[linkedin] Challenge page detected for role '{role}' — skipping")
                await take_screenshot(page, f"linkedin_challenge_{role[:20]}")
                return results

            # Scroll to load more cards
            await human_scroll(page, times=4)
            await human_delay(1, 2)

            # Extract job cards
            job_cards = await page.query_selector_all(
                "li[data-occludable-job-id], li.jobs-search-results__list-item"
            )
            print(f"[linkedin] Found {len(job_cards)} cards for '{role}'")

            for card in job_cards[:limit]:
                if len(results) >= limit:
                    break
                try:
                    job_id = await card.get_attribute("data-occludable-job-id")
                    if not job_id:
                        # Try nested element
                        inner = await card.query_selector("[data-job-id], [data-entity-urn]")
                        if inner:
                            job_id = await inner.get_attribute("data-job-id") or await inner.get_attribute("data-entity-urn")
                            if job_id and ":" in job_id:
                                job_id = job_id.split(":")[-1]

                    if not job_id or job_id in seen_ids:
                        continue

                    title_el = await card.query_selector(".job-card-list__title, .base-search-card__title, a.job-card-container__link")
                    company_el = await card.query_selector(".job-card-container__company-name, .base-search-card__subtitle")
                    location_el = await card.query_selector(".job-card-container__metadata-item, .job-search-card__location")
                    easy_apply_el = await card.query_selector(
                        ".job-card-container__apply-method, [aria-label*='Easy Apply'], .jobs-apply-button--top-card"
                    )

                    title = await title_el.inner_text() if title_el else "Unknown Title"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    location_text = await location_el.inner_text() if location_el else ""
                    has_easy_apply = easy_apply_el is not None

                    if has_easy_apply:
                        easy_text = await easy_apply_el.inner_text()
                        has_easy_apply = "easy apply" in easy_text.lower()

                    job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"
                    description = await self._get_job_description(page, job_url)

                    # Parse salary if present
                    salary_el = await card.query_selector(".job-card-container__salary-info, [class*='salary']")
                    salary = await salary_el.inner_text() if salary_el else None

                    seen_ids.add(job_id)
                    results.append(RawJobData(
                        source="linkedin",
                        external_id=job_id,
                        url=job_url,
                        title=title.strip(),
                        company=company.strip(),
                        location=location_text.strip(),
                        remote_type=self.parse_remote_type(location_text),
                        employment_type=self.parse_employment_type("full-time"),
                        seniority=self.parse_seniority(title),
                        description=description,
                        salary_range=salary,
                        has_easy_apply=has_easy_apply,
                    ))
                    await human_delay(1, 2.5)

                except Exception as e:
                    print(f"[linkedin] Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"[linkedin] Error searching role '{role}': {e}")

        return results

    async def _get_job_description(self, page, job_url: str) -> str:
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=20000)
            await human_delay(1.5, 3)

            if await is_challenge_page(page):
                return ""

            # Try to expand "Show more" button
            show_more = await page.query_selector("button.show-more-less-html__button--more")
            if show_more:
                await show_more.click()
                await human_delay(0.5, 1)

            desc_el = await page.query_selector("#job-details, .jobs-description-content__text, .show-more-less-html__markup")
            if desc_el:
                return await desc_el.inner_text()
        except Exception as e:
            print(f"[linkedin] Error fetching description from {job_url}: {e}")
        return ""
