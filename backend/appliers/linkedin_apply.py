"""LinkedIn Easy Apply handler."""
from playwright.async_api import Page
from backend.appliers.base import AbstractApplier, ApplyResult
from backend.scrapers.stealth import human_delay, take_screenshot, is_challenge_page


class LinkedInApplier(AbstractApplier):

    async def apply(self, page: Page, job_url: str, resume_path: str) -> ApplyResult:
        method = "easy_apply"
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            await human_delay(2, 3)

            if await is_challenge_page(page):
                return ApplyResult(success=False, method=method, status="requires_manual",
                                   error_detail="Challenge/CAPTCHA page encountered")

            # Click Easy Apply button
            apply_btn = await page.query_selector(
                "button[data-control-name='jobdetails_topcard_inapply'], "
                ".jobs-apply-button--top-card, "
                "button[aria-label*='Easy Apply']"
            )
            if not apply_btn:
                return ApplyResult(success=False, method=method, status="requires_manual",
                                   error_detail="Easy Apply button not found")

            await apply_btn.click()
            await human_delay(1.5, 2.5)

            # Step through form
            max_steps = 10
            for step in range(max_steps):
                # Check for success
                success_el = await page.query_selector(
                    "[data-test-modal-container] h3, .artdeco-modal__header h2"
                )
                if success_el:
                    text = await success_el.inner_text()
                    if any(w in text.lower() for w in ["submitted", "applied", "sent"]):
                        return ApplyResult(success=True, method=method, status="submitted",
                                           confirmation_text=text)

                # Handle resume step
                resume_section = await page.query_selector("[id*='resume'], [aria-label*='resume']")
                if resume_section:
                    upload_btn = await page.query_selector("input[type='file']")
                    if upload_btn:
                        await upload_btn.set_input_files(resume_path)
                        await human_delay(1, 2)

                # Handle Yes/No radio questions (authorization, etc.)
                radios = await page.query_selector_all("input[type='radio'][value='Yes'], input[type='radio'][value='true']")
                for radio in radios[:3]:
                    is_visible = await radio.is_visible()
                    if is_visible:
                        await radio.click()
                        await human_delay(0.3, 0.7)

                # Try "Next" or "Review" or "Submit" button
                for btn_text in ["Submit application", "Review", "Next", "Continue"]:
                    btn = await page.query_selector(
                        f"button[aria-label='{btn_text}'], "
                        f"button span:text-is('{btn_text}')"
                    )
                    if btn:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            await btn.click()
                            await human_delay(1.5, 2.5)
                            break

                # Check if modal closed (application done)
                modal = await page.query_selector(".artdeco-modal--layer-confirmation, [data-test-modal]")
                if not modal:
                    # Check for confirmation in page
                    conf_el = await page.query_selector(".jobs-post-apply-modal, .artdeco-inline-feedback")
                    if conf_el:
                        text = await conf_el.inner_text()
                        return ApplyResult(success=True, method=method, status="submitted",
                                           confirmation_text=text)
                    break

            return ApplyResult(success=False, method=method, status="requires_manual",
                               error_detail="Could not complete Easy Apply form")

        except Exception as e:
            await take_screenshot(page, f"linkedin_apply_error_{job_url[-10:]}")
            return ApplyResult(success=False, method=method, status="failed", error_detail=str(e))
