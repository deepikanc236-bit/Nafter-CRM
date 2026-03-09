from textblob import TextBlob

def analyze_sentiment(text):
    if not text:
        return 0.0, "Neutral"

    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity

    if polarity > 0.2:
        label = "Positive"
    elif polarity < -0.2:
        label = "Negative"
    else:
        label = "Neutral"

    return polarity, label