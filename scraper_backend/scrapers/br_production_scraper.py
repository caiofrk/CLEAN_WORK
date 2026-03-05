import os
import json
import instructor
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional

class BrazilProductionLead(BaseModel):
    projeto: str
    tipo: str = Field(description="Ex: Longa-metragem, Série, Publicidade, Clipe")
    vagas_tecnicas: List[str] = Field(description="Rigger, Dublê, Efeitos Físicos, Efeitos Especiais, Duplo, Maquinista")
    uf: str = Field(description="Sigla do estado/distrito (ex: RJ, SP, MG, PT, Lisboa)")
    cidade: Optional[str] = None
    contato_producao: Optional[str] = Field(description="Email ou @ de quem está contratando", default=None)
    url_origem: Optional[str] = Field(description="URL da vaga", default=None)

def analyze_br_production(text_content: str, target_ufs: List[str]) -> Optional[BrazilProductionLead]:
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        print("WARNING: GEMINI_API_KEY not set. Cannot analyze without API key.")
        return None
        
    genai.configure(api_key=api_key)
    
    client = instructor.from_gemini(
        client=genai.GenerativeModel("gemini-2.5-flash"), 
        mode=instructor.Mode.GEMINI_JSON
    )
    
    try:
        lead = client.chat.completions.create(
            messages=[{
                "role": "system",
                "content": f"Extraia oportunidades de produção audiovisual no Brasil e em Portugal. "
                           f"Filtre apenas para as regiões/estados: {', '.join(target_ufs)}. "
                           "Ignore profissionais buscando trabalho; foque em produtoras contratando. "
                           "Dê preferência para vagas envolvendo: 'Rigging', 'Riggers', 'Levitação', 'Rigger de Efeitos', "
                           "'Dublê de ação', 'Duplo de ação', 'Coordenador de ação', 'Coordenador de dublês', "
                           "'Maquinaria e Elétrica', 'Diretor ou Técnico de Efeitos Físicos', 'Diretor ou Técnico de Efeitos Especiais/Visuais', "
                           "ou 'Coordenador de Efeitos Especiais'."
            },
            {"role": "user", "content": text_content}],
            response_model=BrazilProductionLead,
        )
        return lead
    except Exception as e:
        print(f"Error extracting production lead: {e}")
        return None

def scrape_production_leads():
    import requests
    print("Starting Production Scraper on LIVE Public Tenders (PNCP)...")
    
    keywords_to_scrape = ["audiovisual", "cenografia", "iluminação cênica", "rigger lisboa", "produção audiovisual lisboa"]
    target_ufs = ["RJ", "SP", "MG", "RS", "SC", "PR", "BA", "PT", "Lisboa"]
    
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
                        
                    url_origem = result.url_origem
                    if not url_origem:
                        orgao_cnpj = item.get('orgao_cnpj', '')
                        ano = item.get('ano', '')
                        numero = item.get('numero_sequencial', '')
                        
                        if orgao_cnpj and ano and numero:
                            url_origem = f"https://pncp.gov.br/app/editais/{orgao_cnpj}/{ano}/{numero}"
                        else:
                            url_origem = "https://pncp.gov.br/app/editais"
                            
                    leads.append({
                        "projeto_nome": result.projeto if result.projeto and result.projeto != "Projeto Extraído via Backend Regex" else item.get('orgao_nome', 'Órgão Público'),
                        "uf": item.get('uf') or result.uf.upper(),
                        "cidade": item.get('municipio_nome') or result.cidade,
                        "vagas": result.vagas_tecnicas if result.vagas_tecnicas else ["Equipe Técnica Geral"],
                        "descricao_original": desc,
                        "contato_producao": contato,
                        "url_origem": url_origem,
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

    if not unique_leads:
        print("No real live production leads found at the moment based on the targeted keywords and locations. (No mockups enabled)")
    else:
        print(f"Extracted {len(unique_leads)} valid live production leads.")
        
    return unique_leads

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    results = scrape_production_leads()
    print(json.dumps(results, indent=2))
