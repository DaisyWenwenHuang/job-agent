"""Indeed Quick Apply handler."""
from playwright.async_api import Page
from backend.appliers.base import AbstractApplier, ApplyResult
from backend.scrapers.stealth import human_delay, take_screenshot, is_challenge_page


class IndeedApplier(AbstractApplier):

    async def apply(self, page: Page, job_url: str, resume_path: str) -> ApplyResult:
        method = "quick_apply"
        try:
            await page.goto(job_url, wait_until="domcontentloaded", timeout=30000)
            await human_delay(2, 3)

            if await is_challenge_page(page):
                return ApplyResult(success=False, method=method, status="requires_manual",
                                   error_detail="Challenge/CAPTCHA page encountered")

            # Click Indeed Apply button
            apply_btn = await page.query_selector(
                "[data-testid='indeedApplyButton'], "
                "button[id*='indeedApplyButton'], "
                ".ia-IndeedApplyButton"
            )
            if not apply_btn:
                return ApplyResult(success=False, method=method, status="requires_manual",
                                   error_detail="Indeed Apply button not found")

            await apply_btn.click()
            await human_delay(2, 3)

            # Step through Indeed apply form
            max_steps = 10
            for step in range(max_steps):
                # Check for success
                success_el = await page.query_selector(
                    "[data-testid='applicationSubmittedPage'], "
                    ".ia-JobActionConfirmation"
                )
                if success_el:
                    text = await success_el.inner_text()
                    return ApplyResult(success=True, method=method, status="submitted",
                                       confirmation_text=text[:500])

                # Handle resume upload
                upload_input = await page.query_selector("input[type='file'][accept*='pdf'], input[type='file'][accept*='doc']")
                if upload_input:
                    await upload_input.set_input_files(resume_path)
                    await human_delay(1, 2)

                # Fill required text fields that are empty
                required_inputs = await page.query_selector_all("input[required]:not([type='file']):not([type='radio']):not([type='checkbox'])")
                for inp in required_inputs[:5]:
                    val = await inp.input_value()
                    if not val.strip():
                        label_el = await page.query_selector(f"label[for='{await inp.get_attribute('id')}']")
                        label_text = (await label_el.inner_text()).lower() if label_el else ""
                        # Fill phone if empty
                        if "phone" in label_text:
                            await inp.fill("5555555555")

                # Continue / Next / Submit
                for btn_text in ["Submit your application", "Submit", "Continue", "Next"]:
                    btn = await page.query_selector(
                        f"button:has-text('{btn_text}'), "
                        f"[data-testid='submit-btn'], "
                        f"[data-testid='continue-btn']"
                    )
                    if btn:
                        is_visible = await btn.is_visible()
                        if is_visible:
                            await btn.click()
                            await human_delay(1.5, 2.5)
                            break

            return ApplyResult(success=False, method=method, status="requires_manual",
                               error_detail="Could not complete Indeed apply form")

        except Exception as e:
            await take_screenshot(page, f"indeed_apply_error")
            return ApplyResult(success=False, method=method, status="failed", error_detail=str(e))
