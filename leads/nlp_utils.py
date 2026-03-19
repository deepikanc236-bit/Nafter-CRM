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
    RATES = {'usd': 83, 'aed': 22, 'eur': 90, 'inr': 1, '$': 83, '€': 90, '₹': 1}
    
    budget_raw = None
    budget_inr = 0
    
    # Improved regex for budget extraction
    # Requires either:
    # 1. A currency symbol/code
    # 2. A units suffix (lakh, k, etc.)
    # 3. Or being preceded by "budget"
    # or being preceded by "budget"
    # Also added negative lookahead to skip numbers followed by timeline units (mon, weeks, days)
    pattern = r'(?:budget[:\s]+(?:is|of)?\s*)?(?P<currency>[\$€₹]|usd|aed|eur|gbp|inr)?\s*(?P<number>[\d,]+(?:\.\d+)?)\s*(?P<suffix>lakhs?|lacs?|crores?|cr|millions?|m|k|thousands?|k)?\b(?!\s*(?:month|week|day|year))'
    
    match = re.search(pattern, text_lower)
    if match:
        val_str = match.group('number').replace(',', '')
        val = float(val_str)
        suffix = match.group('suffix')
        currency = match.group('currency')
        
        # If we have neither currency nor suffix, we check if it was explicitly called "budget"
        has_context = "budget" in text_lower[:match.start()] or "budget" in text_lower[match.end():match.end()+20]
        
        if not currency and not suffix and not has_context:
            return data # Skip plain numbers that aren't clearly budgets
            
        currency = (currency or 'inr').strip().lower().replace('.', '')
        # Handle the case where currency might be just the symbol
        if currency not in RATES and currency == '₹':
            currency = '₹'
        
        multipliers = {
            'lakh': 100000, 'lakhs': 100000, 'lac': 100000, 'lacs': 100000,
            'cr': 10000000, 'crore': 10000000, 'crores': 10000000,
            'm': 1000000, 'million': 1000000, 'millions': 1000000,
            'k': 1000, 'thousand': 1000, 'thousands': 1000
        }
        
        if suffix and suffix in multipliers:
            val *= multipliers[suffix]
            
        rate = RATES.get(currency, 1)
        budget_inr = int(val * rate)
        budget_raw = f"{match.group(1) or ''}{match.group(2)}{match.group(3) or ''}".strip()
        
    data['budget'] = budget_raw
    data['budget_inr_value'] = budget_inr

    # 2. Timeline Extraction (e.g., "2 months", "3 weeks")
    timeline_match = re.search(r'(\d+)\s*(month|months|week|weeks|day|days|year|years)', text_lower)
    if timeline_match:
        data['timeline'] = f"{timeline_match.group(1)} {timeline_match.group(2)}"

    # 3. Service Keyword Match
    services = {
        'AI Strategy & Consulting': ['strategy', 'consulting', 'startup', 'advisor'],
        'Generative AI Solutions': ['generative', 'genai', 'llm', 'chatgpt', 'openai'],
        'AI Engineering & MLOps': ['engineering', 'mlops', 'machine learning', 'model'],
        'Autonomous Agents': ['agent', 'autonomous', 'crewai', 'autogen'],
        'Workflows & Automation': ['workflow', 'automation', 'automate', 'process'],
        'Autonomous Drone Solutions': ['drone', 'uav', 'aerial', 'vision'],
        'Full Stack Development': ['web', 'app', 'react', 'django', 'development', 'full stack'],
        'AI Digital Marketing': ['marketing', 'seo', 'ads', 'social media', 'content']
    }
    for service, keywords in services.items():
        if any(kw in text_lower for kw in keywords):
            data['service'] = service
            break

    # 4. Urgency Detection using TF-IDF
    from .ml_utils import get_urgency_score_tfidf
    urgency_score = get_urgency_score_tfidf(text_lower)
    
    if urgency_score > 0.7:
        data['urgency'] = 'High'
    elif urgency_score > 0.3:
        data['urgency'] = 'Normal'
    else:
        # Fallback to keyword check if TF-IDF is low but some words exist
        urgency_keywords = ['asap', 'urgent', 'immediately', 'now']
        if any(kw in text_lower for kw in keywords):
            data['urgency'] = 'High'
        else:
            data['urgency'] = 'Normal'

    # 5. Lead Scoring (Company Weighing)
    company_keywords = {
        "startup": 2, "enterprise": 4, "corporation": 5, "government": 5,
        "saas": 3, "ecommerce": 3, "fintech": 4, "healthcare": 4,
        "fortune 500": 10, "mnc": 8, "international": 6, "global": 6,
        "small business": 2, "agency": 3
    }
    
    score = 0
    # A. Company Base Score (Capped at 30)
    company_score = 0
    for kw, weight in company_keywords.items():
        if kw in text_lower:
            company_score += weight
    score += min(company_score * 3, 30) 

    # B. Budget Score (Up to 40)
    if budget_inr >= 1000000: score += 40
    elif budget_inr >= 500000: score += 30
    elif budget_inr >= 100000: score += 20
    elif budget_inr >= 10000: score += 10
    
    # C. Urgency & Service Score (Up to 30)
    if data.get('urgency') == 'High': score += 20
    elif data.get('urgency') == 'Normal': score += 10
    
    # Always award points for matching a specific AI service
    if data.get('service') and data.get('service') != "General Inquiry":
        score += 10

    # D. Final Cap
    data['lead_score'] = min(score, 100)
    
    # Map score to priority
    if data['lead_score'] >= 70 or data['urgency'] == 'High':
        data['priority'] = 'High'
    elif data['lead_score'] >= 40:
        data['priority'] = 'Medium'
    else:
        data['priority'] = 'Low'

    return data
