import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_KEY", "")

if not url or not key:
    print("WARNING: SUPABASE_URL or SUPABASE_KEY not set in environment.")

try:
    supabase: Client = create_client(url, key)
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    supabase = None

import asyncio
from scrapers.br_production_scraper import scrape_production_leads

async def run_scraper():
    print("Marketplace Scraper Backend Initialized")
    
    # 1. Scrape Leads
    leads = scrape_production_leads()
    print(f"Scraped {len(leads)} leads. Integrating with Supabase...")
    
    # 2. Insert into Supabase
    if supabase and leads:
        try:
            # Insert validated production leads into the br_production_leads table
            response = supabase.table("br_production_leads").insert(leads).execute()
            print(f"Successfully inserted {len(response.data)} market leads into Supabase!")
        except Exception as e:
            print(f"Failed to insert leads into Supabase: {e}")
    else:
        print("Skipping Supabase integration: Please configure .env keys or no leads were found.")

def main():
    asyncio.run(run_scraper())
    
if __name__ == "__main__":
    main()
