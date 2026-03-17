import re
from .sentiment import analyze_sentiment

def get_urgency_score_tfidf(text):
    """
    Feature 4: Uses keyword frequency to score urgency based on key project details keywords.
    Replaces scikit-learn TF-IDF to speed up builds.
    Returns a score multiplier (0.0 to 1.0).
    """
    if not text:
        return 0.0

    # Define urgency keywords
    urgency_keywords = ["urgent", "asap", "immediately", "quickly", "priority", "critical", "soon"]
    
    text = text.lower()
    matches = 0
    for word in urgency_keywords:
        # Simple word boundary check
        if re.search(rf'\b{word}\b', text):
            matches += 1
    
    # Normalize score: 1 match = 0.5, 2+ matches = 1.0 (approximates the previous TF-IDF intent)
    score = (matches / 2.0)
    return min(float(score), 1.0)


def calculate_conversion_probability(lead, sentiment_score):
    """
    Feature 3: Predicts conversion probability based on budget, returning status, sentiment, and TF-IDF urgency.
    """
    probability = 10 # Base probability
    
    # 1. Budget Impact
    if lead.budget_inr_value:
        if lead.budget_inr_value > 1_000_000:
            probability += 40
        elif lead.budget_inr_value > 500_000:
            probability += 20
            
    # 2. Returning Status & Engagement
    if lead.is_returning:
        probability += 25
    
    # Engagement Score (adds up to 15%)
    engagement_bonus = int((lead.engagement_score / 100) * 15)
    probability += min(engagement_bonus, 15)
        
    # 3. Sentiment Impact
    if sentiment_score > 0: # Positive
        probability += 25
    elif sentiment_score < 0: # Negative
        probability -= 15
        
    # 4. TF-IDF Urgency Score
    urgency_multiplier = get_urgency_score_tfidf(lead.project_details or "")
    probability += int(urgency_multiplier * 15) 
    
    # Safety: Clamp between 0 and 100
    return max(0, min(100, probability))
