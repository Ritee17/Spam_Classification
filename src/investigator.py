import asyncio
from playwright.async_api import async_playwright

async def investigate_url(url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        
        try:
            # 15 second timeout for reality
            await page.goto(url, timeout=15000, wait_until="load")
            page_title = (await page.title()).lower()
            
            red_flags = ["login", "verify", "kyc", "bank", "job", "earn", "prize", "update"]
            is_malicious = any(flag in page_title for flag in red_flags)
            
            return {"is_malicious": is_malicious, "final_url": page.url, "reason": "Analyzed Title"}
            
        except Exception as e:
            return {
                "final_url": url, 
                "is_malicious": True, 
                "reason": f"Unreachable/Suspicious ({str(e)})"
            }
        finally:
            await browser.close()