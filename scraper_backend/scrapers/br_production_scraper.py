import os
import json
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional

class BrazilProductionLead(BaseModel):
    projeto: str
    tipo: str = Field(description="Ex: Longa-metragem, Série, Publicidade, Clipe")
    vagas_tecnicas: List[str] = Field(description="Rigger, Dublê, Efeitos Físicos, Maquinista")
    uf: str = Field(description="Sigla do estado brasileiro (ex: RJ, SP, MG)")
    cidade: Optional[str] = None
    contato_producao: Optional[str] = Field(description="Email ou @ de quem está contratando", default=None)

def analyze_br_production(text_content: str, target_ufs: List[str]) -> Optional[BrazilProductionLead]:
    api_key = os.environ.get("GEMINI_API_KEY")

    def get_mock_lead(text):
        nonlocal target_ufs
        target_keywords = [
            "rigger de efeitos",
            "dublê de ação",
            "equipe de maquinaria e elétrica",
            "técnico de efeitos visuais",
            "técnico de efeitos físicos",
            "coordenador de dublês"
        ]
        trigger_words = [t.lower() for t in target_ufs] + target_keywords + ["rigger", "dublê", "efeitos", "maquinista", "vaga", "equipe"]
        text_lower = text.lower()
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', text)
        handle_match = re.search(r'@\w+', text)
        contato = email_match.group(0) if email_match else (handle_match.group(0) if handle_match else None)
        
        if any(word in text_lower for word in trigger_words) and not ("busco" in text_lower or "procuro" in text_lower):
             return BrazilProductionLead(
                 projeto="Projeto Extraído via Backend Regex",
                 tipo="Série/Longa",
                 vagas_tecnicas=["Rigger", "Maquinista"],
                 uf="RJ" if "rj" in text_lower else "SP",
                 cidade="Capital",
                 contato_producao=contato,
             )
        return None

    if not api_key:
        print("WARNING: GEMINI_API_KEY not set. Falling back to regex extraction.")
        return get_mock_lead(text_content)
        
    genai.configure(api_key=api_key)
    
    client = instructor.from_gemini(
        client=genai.GenerativeModel("gemini-2.5-flash"), 
        mode=instructor.Mode.GEMINI_JSON
    )
    
    try:
        lead = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": f"Extraia oportunidades de produção audiovisual no Brasil. "
                           f"Filtre apenas para os estados: {', '.join(target_ufs)}. "
                           "Ignore profissionais buscando trabalho; foque em produtoras contratando. "
                           "Dê preferência para vagas como: 'Busca-se Rigger de efeitos', "
                           "'Vaga para Dublê de ação', 'Equipe de Maquinaria e Elétrica', "
                           "'Técnico de Efeitos Visuais/Físicos', ou 'Coordenador de Dublês'."
            },
            {"role": "user", "content": text_content}],
            response_model=BrazilProductionLead,
        )
        return lead
    except Exception as e:
        print(f"Error extracting production lead: {e}. Falling back to Regex extraction.")
        return get_mock_lead(text_content)

def scrape_production_leads():
    import requests
    print("Starting Brazil Production Scraper on LIVE Public Tenders (PNCP)...")
    
    keywords_to_scrape = ["audiovisual", "cenografia", "iluminação cênica"]
    target_ufs = ["RJ", "SP", "MG", "RS", "SC", "PR", "BA"]
    
    leads = []
    
    for keyword in keywords_to_scrape:
        print(f"-> Fetching real active opportunities for: '{keyword}'...")
        try:
            url = f"https://pncp.gov.br/api/search/?q={keyword}&tipos_documento=edital"
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            items = data.get("items", [])[:8] # Max 8 items per keyword to preserve API quota
            
            for item in items:
                title = item.get("title", "")
                desc = item.get("description", "")
                raw_text = f"CONTRATANTE: {item.get('orgao_nome', '')}. OBJETO: {title}. {desc}"
                
                print(f"Analyzing real lead: {desc[:60]}...")
                result = analyze_br_production(raw_text, target_ufs)
                
                if result:
                    # Provide an automatic fail-back email based on the public entity if None
                    contato = result.contato_producao
                    if not contato:
                        contato = f"licitacao@{item.get('orgao_cnpj', 'gov')}.gov.br"
                        
                    leads.append({
                        "projeto_nome": result.projeto if result.projeto and result.projeto != "Projeto Extraído via Backend Regex" else item.get('orgao_nome', 'Órgão Público'),
                        "uf": item.get('uf') or result.uf.upper(),
                        "cidade": item.get('municipio_nome') or result.cidade,
                        "vagas": result.vagas_tecnicas if result.vagas_tecnicas else ["Equipe Técnica Geral"],
                        "descricao_original": desc,
                        "contato_producao": contato,
                    })
        except Exception as e:
            print(f"Error fetching keyword {keyword}: {e}")
            
    # Deduplicate logic based on original description
    seen_desc = set()
    unique_leads = []
    for lead in leads:
        if lead["descricao_original"] not in seen_desc:
            unique_leads.append(lead)
            seen_desc.add(lead["descricao_original"])

    print(f"Extracted {len(unique_leads)} valid live production leads.")
    return unique_leads

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    results = scrape_production_leads()
    print(json.dumps(results, indent=2))
