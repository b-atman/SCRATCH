import pandas as pd
import spacy
from textblob import TextBlob

# Load NLP model
nlp = spacy.load("en_core_web_sm")

# Load data
df = pd.read_csv("reddit_posts.csv")

# Add sentiment and entities
sentiments = []
entities_list = []

for text in df['title']:
    # Sentiment
    blob = TextBlob(text)
    sentiments.append(blob.sentiment.polarity)  # -1 to 1

    # Named Entity Recognition
    doc = nlp(text)
    entities = [ent.text for ent in doc.ents]
    entities_list.append(", ".join(entities))

# Add to DataFrame
df['sentiment'] = sentiments
df['entities'] = entities_list

# Save enriched data
df.to_csv("reddit_posts_enriched.csv", index=False)
print("✅ NLP enrichment complete — saved to reddit_posts_enriched.csv")
