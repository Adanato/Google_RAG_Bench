import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def scrape_google(query: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        await stealth_async(page)  # Activate stealth

        print("Navigating to google.com...")
        await page.goto("https://www.google.com/", timeout=30000)

        # Interact with Google's search box (textarea)
        await page.click("textarea[name='q']")
        await page.keyboard.type(query, delay=223)
        await page.keyboard.press("Enter")

        # Wait for normal results
        try:
            await page.wait_for_selector("div.g", timeout=15000)
        except:
            print("Likely got captcha/blocked, returning empty.")
            await browser.close()
            return {"results_data": [], "ai_overview": ""}

        # Scrape standard SERP results
        result_divs = await page.query_selector_all("div.g")
        results_data = []
        for idx, div in enumerate(result_divs, start=1):
            title_el = await div.query_selector("h3")
            if not title_el:
                continue
            title_text = await title_el.inner_text()
            link_el = await div.query_selector("a")
            link_href = await link_el.get_attribute("href") if link_el else None
            snippet_el = await div.query_selector("div[data-sncf]")
            snippet_text = await snippet_el.inner_text() if snippet_el else ""
            results_data.append({
                "position": idx,
                "title": title_text,
                "link": link_href,
                "snippet": snippet_text
            })

        # Try to find "Show more"
        try:
            # 1) Wait for it
            locator = page.locator("text=Show more")
            await locator.wait_for(state="visible", timeout=5000)

            # 2) Sometimes you need to scroll it into view
            await locator.scroll_into_view_if_needed()

            # 3) Click it
            await locator.click()
            print("Successfully clicked 'Show more'!")
        except Exception as e:
            print("Couldn't click 'Show more':", e)

        # Try to capture AI Overview text (if present)
        ai_overview = ""
        try:
            # Wait for the container
            await page.wait_for_selector("div.zNsLfb.Jzkafd", timeout=5000)

            # Attempt to click "Show more"
            try:
                await page.wait_for_selector("div.kHtcsd", timeout=2000)
                await page.click("div.kHtcsd")
            except:
                pass  # "Show more" not found or not clickable

            # Now read the container text (with possible extra lines revealed)
            ai_overview = await page.inner_text("div.YzCcne")
        except:
            pass  # No AI Overview or timed out

        await browser.close()

        return {
            "results_data": results_data,
            "ai_overview": ai_overview
        }

async def main():
    query_str = "how many birds in 12 days of christmas?"
    data = await scrape_google(query_str)
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())
