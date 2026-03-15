import asyncio
from playwright.async_api import async_playwright

async def investigate_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # If it takes more than 10 seconds, it's likely a dead scam link
            response = await page.goto(url, wait_until="load", timeout=10000)
            
            # If the page doesn't exist (404) or crashed (500)
            if response.status >= 400:
                return {"is_malicious": True, "reason": "Broken Link"}

            page_title = (await page.title()).lower()
            
            # Strict Production Red Flags
            red_flags = ["login", "verify", "kyc", "bank", "job", "earn", "prize", "update", "sbi", "hdfc"]
            is_malicious = any(flag in page_title for flag in red_flags)

            return {"is_malicious": is_malicious, "final_url": page.url}

        except Exception as e:
            return {
            "final_url": url, 
            "is_malicious": True, 
            "reason": f"Timeout/Unreachable ({str(e)})"
        }
        
        finally:
            await browser.close()