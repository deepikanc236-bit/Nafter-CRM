import re

def test_extraction(text):
    text_lower = text.lower()
    RATES = {'usd': 83, 'aed': 22, 'eur': 90, 'inr': 1, '$': 83, '€': 90}
    
    # Current regex in nlp_utils.py
    pattern = r'(?:budget[:\s]+(?:is|of)?\s*)?(?P<currency>[\$€₹]|usd|aed|eur|gbp|inr)?\s*(?P<number>[\d,]+(?:\.\d+)?)\s*(?P<suffix>lakhs?|lacs?|crores?|cr|millions?|m|k|thousands?)?\b'
    
    match = re.search(pattern, text_lower)
    if match:
        val_str = match.group('number').replace(',', '')
        val = float(val_str)
        suffix = match.group('suffix')
        currency = match.group('currency')
        
        # Current context logic
        has_context = "budget" in text_lower[:match.start()] or "budget" in text_lower[match.end():match.end()+20]
        
        print(f"Match found!")
        print(f"  Number: {val}")
        print(f"  Suffix: '{suffix}'")
        print(f"  Currency: '{currency}'")
        print(f"  Has Context: {has_context}")
        
        if not currency and not suffix and not has_context:
            print("  Result: Skip (No context/units)")
            return 0
            
        multipliers = {
            'lakh': 100000, 'lakhs': 100000, 'lac': 100000, 'lacs': 100000,
            'cr': 10000000, 'crore': 10000000, 'crores': 10000000,
            'm': 1000000, 'million': 1000000, 'millions': 1000000,
            'k': 1000, 'thousand': 1000, 'thousands': 1000
        }
        
        if suffix and suffix in multipliers:
            val *= multipliers[suffix]
            
        print(f"  Multiplied Val: {val}")
        return val
    else:
        print("No match found.")
        return 0

print("Testing: 'Interested in autonomous agent orchestration. Timeline is 3 months.'")
test_extraction("Interested in autonomous agent orchestration. Timeline is 3 months.")
