import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from .sentiment import analyze_sentiment

def get_urgency_score_tfidf(text):
    """
    Feature 4: Uses TF-IDF to score urgency based on key project details keywords.
    Returns a score multiplier (0.0 to 1.0).
    """
    if not text:
        return 0.0

    # Define urgency keywords for TF-IDF
    urgency_vocabulary = ["urgent", "asap", "immediately", "quickly", "priority", "critical", "soon"]
    
    # Initialize TF-IDF Vectorizer with specific vocabulary
    vectorizer = TfidfVectorizer(vocabulary=urgency_vocabulary, stop_words='english')
    
    try:
        tfidf_matrix = vectorizer.fit_transform([text.lower()])
        # Sum of TF-IDF scores for the vocabulary
        score = np.sum(tfidf_matrix.toarray())
        # Normalize score to a reasonable multiplier (capped at 1.0)
        return min(float(score) * 2.0, 1.0) 
    except Exception:
        return 0.0

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
