import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
import os
import json

# To use real Gemini, you would generally import google-genai
# and initialize the client with your GEMINI_API_KEY.
# For now, we will structure the validation function to be ready for the real API.
try:
    from google import genai
    from google.genai import types
    gemini_available = True
except ImportError:
    gemini_available = False
    print("WARNING: google-genai not installed. Gemini validation will be mocked.")

class TenderLead(BaseModel):
    org_name: str
    object_description: str
    deadline: str
    is_rope_access_relevant: bool

def validate_with_gemini(description: str) -> bool:
    """
    Uses Gemini to validate if a description implies a demand for Rope Access services.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key or not gemini_available:
        # Mock validation logic if API key is not set
        trigger_words = ["nr-35", "trabalho em altura", "cadeirinha", "acesso por corda", "alpinismo"]
        return any(word in description.lower() for word in trigger_words)
        
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"""
        Analyze this tender description. Identify if it mentions 'NR-35', 'Trabalho em Altura', 
        'Cadeirinha', or 'Acesso por Corda'. 
        If it's an organization (Hospital, School, Govt Building, etc.) ASKING for these services, 
        respond with exactly 'VALID'. 
        If it's a company selling these services or if it's completely unrelated, respond with 'INVALID'.
        
        Description:
        {description}
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return "VALID" in response.text.upper()
    except Exception as e:
        print(f"Gemini API Error: {e}. Falling back to local keyword validation.")
        # Fallback to local regex/keyword matching if the API fails
        trigger_words = ["nr-35", "trabalho em altura", "cadeirinha", "acesso por corda", "alpinismo"]
        return any(word in description.lower() for word in trigger_words)

def scrape_compras_net(keyword: str = "alpinismo"):
    print(f"Starting Real PNCP Tender Scraper for keyword: {keyword}")
    
    # Use the official Brazilian PNCP API for open public tenders
    search_url = f"https://pncp.gov.br/api/search/?q={keyword}&tipos_documento=edital"
    
    try:
        response = requests.get(search_url, timeout=15)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
    except Exception as e:
        print(f"Failed to fetch from PNCP: {e}")
        return []
    
    leads = []
    
    for item in items:
        # Construct a readable string for the AI from the returned fields
        title = item.get("title", "")
        desc = item.get("description", "")
        full_text = f"{title}. {desc}"
        
        print(f"Analyzing: {full_text[:60]}...")
        
        # Use Gemini (or fallback logic) to validate if the tender requires Rope Access
        is_relevant = validate_with_gemini(full_text) 
        
        if is_relevant:
            # Build the public link to the PNCP Opportunity
            # item_url looks like /compras/92242080000100/2023/8
            rel_url = item.get("item_url", "")
            raw_url = f"https://pncp.gov.br/app/editais/{rel_url.split('/compras/')[-1]}" if "/compras/" in rel_url else search_url
            
            # Format the deadline safely
            deadline_str = item.get("data_fim_vigencia")
            if deadline_str and "T" in deadline_str:
                deadline_str = deadline_str.split("T")[0]
            elif not deadline_str:
                deadline_str = "2026-12-31" # Fallback
            
            leads.append({
                "client_name": item.get("orgao_nome", "Unknown Public Entity"),
                "opportunity_desc": desc if desc else title,
                "budget_estimate": None, 
                "deadline": deadline_str,
                "status": "open",
                "source_url": raw_url 
            })
            
    print(f"Scraped and validated {len(leads)} active tender leads from PNCP.")
    return leads

if __name__ == "__main__":
    results = scrape_compras_net()
    print(json.dumps(results, indent=2))
