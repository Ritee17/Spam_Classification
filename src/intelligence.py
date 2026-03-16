import whois
from datetime import datetime, timedelta

async def perform_intelligence_audit(url):
    try:
        domain = url.split("//")[-1].split("/")[0]
        w = whois.whois(domain)
        
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        # Check if domain was created in the last 30 days
        is_new = False
        if creation_date:
            days_old = (datetime.now() - creation_date).days
            if days_old < 30:
                is_new = True
                
        return {
            "domain": domain,
            "age_days": (datetime.now() - creation_date).days if creation_date else "Unknown",
            "is_new_domain": is_new,
            "registrar": w.registrar
        }
    except:
        return {"is_new_domain": True, "reason": "Failed to fetch WHOIS (High Risk)"}