from textblob import TextBlob

def analyze_sentiment(text):
    if not text:
        return 0.0, "Neutral"

    try:
        analysis = TextBlob(text)
        polarity = analysis.sentiment.polarity
    except Exception as e:
        print(f">>> [SENTIMENT] Error: {e}. Defaulting to neutral.")
        return 0.0, "Neutral"

    if polarity > 0.2:
        label = "Positive"
    elif polarity < -0.2:
        label = "Negative"
    else:
        label = "Neutral"

    return polarity, label