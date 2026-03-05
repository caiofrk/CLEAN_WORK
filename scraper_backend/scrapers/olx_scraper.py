import asyncio
import re
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape_olx(niche_keyword: str):
    """
    Scrapes OLX for service providers using stealth playwright and BS4.
    """
    logger.info(f"Starting OLX scraper for keyword: {niche_keyword}")
    results = []
    
    async with async_playwright() as p:
        # Launching non-headless can significantly improve bypass rates for Cloudflare
        # You can toggle headless=True later if it works consistently.
        browser = await p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        await Stealth().apply_stealth_async(page)
        
        search_url = f"https://www.olx.com.br/servicos?q={niche_keyword.replace(' ', '+')}"
        
        try:
            await page.goto(search_url, timeout=60000)
            logger.info(f"Navigated to {search_url}. Waiting for results...")
            
            # Wait a few seconds to let any Javascript or Cloudflare challenges resolve
            await page.wait_for_timeout(5000)
            
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # OLX Brazil uses section with id 'ad-list' and a tags for individual ads.
            # We look for links that look like an ad url to extract data.
            ad_cards = soup.find_all("a", href=True)
            
            for index, card in enumerate(ad_cards):
                href = card.get('href', '')
                
                # Check if this link points to an service ad
                if 'olx.com.br' in href and 'servicos' in href and re.search(r'-\d+$', href):
                    
                    title_elem = card.find("h2")
                    if not title_elem:
                        continue
                        
                    # Extract Data
                    title = title_elem.text.strip()
                    if niche_keyword.lower() not in title.lower() and "altura" not in title.lower() and "fachada" not in title.lower():
                        continue # Filter out completely irrelevant ads
                    
                    price = "N/A"
                    # Try to find price if exists
                    if card.parent:
                        price_elem = card.parent.find(lambda tag: tag.name and tag.has_attr('class') and any('price' in str(cls).lower() for cls in tag.get('class')))
                        if price_elem:
                             price = price_elem.text.strip()
                    
                    
                    results.append({
                        "business_name": title,
                        "category": "Rope Access" if "alpinismo" in title.lower() or "altura" in title.lower() else "Civil Construction",
                        "source_url": href,
                        "description": f"Price tag listed: {price}",
                        "is_claimed": False
                    })
            
            logger.info(f"Extracted {len(results)} leads from OLX.")
            
            if len(results) == 0:
                with open("olx_debug.html", "w", encoding="utf-8") as f:
                    f.write(html)
                logger.info("Saved HTML to olx_debug.html since 0 leads were found.")
            
        except Exception as e:
            logger.error(f"Error scraping OLX: {e}")
            
        finally:
            await browser.close()
            
    return results

if __name__ == "__main__":
    leads = asyncio.run(scrape_olx("alpinismo industrial"))
    for lead in leads:
        print(lead)

