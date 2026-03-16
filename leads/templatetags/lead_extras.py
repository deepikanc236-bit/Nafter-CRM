from django import template

register = template.Library()

@register.filter
def smart_rupee(value):
    """
    Formats large numbers in Indian Numbering System (Lakhs/Crores).
    """
    try:
        num = float(value)
    except (ValueError, TypeError):
        return value

    if num >= 10_000_000: # 1 Crore
        return f"{num / 10_000_000:.1f} Cr"
    elif num >= 100_000: # 1 Lakh
        return f"{num / 100_000:.1f} L"
    elif num >= 1_000: # 1 Thousand
        return f"{num / 1_000:.1f} K"
    
    return str(int(num))
