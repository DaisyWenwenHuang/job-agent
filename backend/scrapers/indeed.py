"""Indeed job scraper using Playwright."""
import asyncio
from urllib.parse import quote_plus

from playwright.async_api import async_playwright

from backend.scrapers.base import AbstractScraper, RawJobData
from backend.scrapers.stealth import (
    create_stealth_context, human_delay, human_scroll,
    is_challenge_page, take_screenshot,
)


class IndeedScraper(AbstractScraper):

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
                print(f"[indeed] Scraper error: {e}")
                await take_screenshot(page, "indeed_error")
            finally:
                await context.close()

        print(f"[indeed] Found {len(results)} jobs")
        return results

    async def _search_role(self, page, role: str, location: str, limit: int, seen_ids: set) -> list[RawJobData]:
        results = []
        encoded_role = quote_plus(role)
        encoded_loc = quote_plus(location)
        url = f"https://www.indeed.com/jobs?q={encoded_role}&l={encoded_loc}&sc=0kf%3Aattr(DSQF7)%3B&sort=date"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await human_delay(2, 4)

            if await is_challenge_page(page):
                print(f"[indeed] Challenge page detected for role '{role}' — skipping")
                await take_screenshot(page, f"indeed_challenge_{role[:20]}")
                return results

            await human_scroll(page, times=3)

            # Extract job cards
            job_cards = await page.query_selector_all("[data-jk]")
            print(f"[indeed] Found {len(job_cards)} cards for '{role}'")

            for card in job_cards[:limit]:
                if len(results) >= limit:
                    break
                try:
                    job_key = await card.get_attribute("data-jk")
                    if not job_key or job_key in seen_ids:
                        continue

                    title_el = await card.query_selector("[data-testid='jobTitle'] span, .jobTitle span, h2 span")
                    company_el = await card.query_selector("[data-testid='company-name'], .companyName")
                    location_el = await card.query_selector("[data-testid='text-location'], .companyLocation")

                    title = await title_el.inner_text() if title_el else "Unknown Title"
                    company = await company_el.inner_text() if company_el else "Unknown Company"
                    location_text = await location_el.inner_text() if location_el else ""

                    # Check for Easy Apply
                    easy_apply_el = await card.query_selector("[data-testid='indeedApplyButton'], .indeedApply")
                    has_easy_apply = easy_apply_el is not None

                    if not has_easy_apply:
                        # Also check button text
                        apply_btn = await card.query_selector("button[aria-label*='apply'], a[aria-label*='apply']")
                        if apply_btn:
                            btn_text = await apply_btn.inner_text()
                            has_easy_apply = "easily apply" in btn_text.lower() or "indeed apply" in btn_text.lower()

                    job_url = f"https://www.indeed.com/viewjob?jk={job_key}"
                    description = await self._get_job_description(page, job_url)

                    seen_ids.add(job_key)
                    results.append(RawJobData(
                        source="indeed",
                        external_id=job_key,
                        url=job_url,
                        title=title.strip(),
                        company=company.strip(),
                        location=location_text.strip(),
                        remote_type=self.parse_remote_type(location_text),
                        employment_type=self.parse_employment_type("full-time"),
                        seniority=self.parse_seniority(title),
                        description=description,
                        has_easy_apply=has_easy_apply,
                    ))
                    await human_delay(1, 2)

                except Exception as e:
                    print(f"[indeed] Error parsing card: {e}")
                    continue

        except Exception as e:
            print(f"[indeed] Error searching role '{role}': {e}")

        return results

    async def _get_job_description(self, page, job_url: str) -> str:
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=20000)
            await human_delay(1.5, 3)

            if await is_challenge_page(page):
                return ""

            desc_el = await page.query_selector("#jobDescriptionText, .jobsearch-jobDescriptionText")
            if desc_el:
                return await desc_el.inner_text()
        except Exception as e:
            print(f"[indeed] Error fetching description from {job_url}: {e}")
        return ""
