import re

def extract_lead_info(text):
    if not text:
        return {}

    text_lower = text.lower()
    data = {
        'budget': None,
        'timeline': None,
        'service': "General Inquiry",
        'urgency': "Normal"
    }

    # 1. Multi-Currency Budget Extraction
    # Rates (Static)
    RATES = {'usd': 83, 'aed': 22, 'eur': 90, 'inr': 1, '$': 83, '€': 90}
    
    budget_raw = None
    budget_inr = 0
    
    # Combined pattern for currency symbols/codes and values with suffixes
    # Support: $15k, 20000 AED, €50,000, 15 lakhs, 1 million usd
    currency_pattern = r'([\$€₹]|usd|aed|eur|inr|rs\.?)?\s*(\d+(?:,\d+)*(?:\.\d+)?)\s*(k|thousand|thousands|lakh|lakhs|lac|lacs|m|million|cr|crore)?\s*(usd|aed|eur|inr|rs\.?)?'
    
    match = re.search(currency_pattern, text_lower)
    if match:
        curr_prefix = match.group(1)
        val_str = match.group(2).replace(',', '')
        suffix = match.group(3)
        curr_suffix = match.group(4)
        
        val = float(val_str)
        
        # Apply suffix multipliers
        if suffix:
            if 'k' in suffix or 'thousand' in suffix: val *= 1000
            elif 'lakh' in suffix or 'lac' in suffix: val *= 100000
            elif 'm' in suffix or 'million' in suffix: val *= 1000000
            elif 'cr' in suffix or 'crore' in suffix: val *= 10000000
            
        # Determine currency
        currency = (curr_prefix or curr_suffix or 'inr').strip().lower().replace('.', '')
        rate = RATES.get(currency, 1)
        
        budget_inr = int(val * rate)
        budget_raw = f"{match.group(1) or ''}{match.group(2)}{match.group(3) or ''} {match.group(4) or ''}".strip()
        
    data['budget'] = budget_raw
    data['budget_inr_value'] = budget_inr

    # 2. Timeline Extraction (e.g., "2 months", "3 weeks")
    timeline_match = re.search(r'(\d+)\s*(month|months|week|weeks|day|days|year|years)', text_lower)
    if timeline_match:
        data['timeline'] = f"{timeline_match.group(1)} {timeline_match.group(2)}"

    # 3. Service Keyword Match
    services = {
        'Web Development': ['web', 'website', 'html', 'react', 'django'],
        'Mobile App': ['app', 'mobile', 'ios', 'android', 'flutter'],
        'UI/UX Design': ['design', 'ui', 'ux', 'logo', 'graphics'],
        'Digital Marketing': ['marketing', 'seo', 'ads', 'social media']
    }
    for service, keywords in services.items():
        if any(kw in text_lower for kw in keywords):
            data['service'] = service
            break

    # 4. Urgency Detection
    urgency_keywords = {
        'High': ['urgent', 'asap', 'immediately', 'now', 'fast', 'quick'],
        'Normal': ['whenever', 'next month', 'later', 'planned']
    }
    for level, keywords in urgency_keywords.items():
        if any(kw in text_lower for kw in keywords):
            data['urgency'] = level
            break

    # 5. Lead Scoring (Company Weighing)
    company_keywords = {
        "startup": 2,
        "enterprise": 4,
        "corporation": 5,
        "government": 5,
        "saas": 3,
        "ecommerce": 3,
        "fintech": 4,
        "healthcare": 4,
        "fortune 500": 10,
        "mnc": 8,
        "international": 6,
        "global": 6,
        "small business": 2,
        "agency": 3
    }
    
    score = 0
    for kw, weight in company_keywords.items():
        if kw in text_lower:
            score += weight
    
    data['lead_score'] = score
    
    # Map score to priority if not already set by urgency
    if data['urgency'] == 'Normal':
        if score >= 8:
            data['priority'] = 'High'
        elif score >= 4:
            data['priority'] = 'Medium'
        else:
            data['priority'] = 'Low'
    else:
        data['priority'] = 'High'

    return data
