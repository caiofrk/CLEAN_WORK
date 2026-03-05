import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    async with async_playwright() as p:
        # Launching with specific args can help bypass cloudflare
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        await stealth_async(page)
        
        await page.goto("https://www.olx.com.br/servicos?q=alpinismo+industrial")
        await page.wait_for_timeout(10000) # give it extra time
        
        html = await page.content()
        with open("olx_sample.html", "w", encoding="utf-8") as f:
            f.write(html)
        await browser.close()
        print("HTML saved to olx_sample.html")

if __name__ == "__main__":
    asyncio.run(main())
