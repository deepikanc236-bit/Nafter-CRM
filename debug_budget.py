import re

def extract_smart_budget(text):
    if not text:
        return 0
    text = text.lower().replace(',', '')
    multipliers = {
        'lakh': 100_000, 'lakhs': 100_000, 'lac': 100_000, 'lacs': 100_000,
        'cr': 10_000_000, 'crore': 10_000_000, 'crores': 10_000_000,
        'm': 1_000_000, 'million': 1_000_000, 'millions': 1_000_000,
        'k': 1_000
    }
    rates = {'$': 83, 'usd': 83, 'aed': 22, 'eur': 90, '€': 90, '£': 105, 'inr': 1, '₹': 1}
    # Original pattern from views.py
    pattern = r'(?P<currency>[\$€₹]|usd|aed|eur|gbp|inr)?\s*(?P<number>\d+(?:\.\d+)?)\s*(?P<suffix>lakhs?|lacs?|crores?|cr|millions?|m|k)?\b'
    
    match = re.search(pattern, text)
    if match:
        val = float(match.group('number'))
        suffix = match.group('suffix')
        currency = match.group('currency')
        print(f"DEBUG: matched number={val}, suffix={suffix}, currency={currency}")
        if suffix:
            val *= multipliers.get(suffix, 1)
        rate = rates.get(currency, 1)
        return int(val * rate)
    return 0

test_cases = [
    "Looking for workflow automation. Budget is 15 lakhs.",
    "Budget is 5 lakhs",
    "Estimated budget: 15L",
    "Budget is 15000",
    "Project budget is 15k"
]

for tc in test_cases:
    print(f"Input: '{tc}' -> Result: {extract_smart_budget(tc)}")
