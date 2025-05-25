import google.generativeai as genai
import pandas as pd
import time
import ast
import re

# 🔐 Gemini API key
genai.configure(api_key="AIzaSyDb74ulDO0VYMJt6aF_51Bk06l5_qpd1rM")  # Replace with your key

# Load the enriched dataset
df = pd.read_csv("reddit_posts_enriched.csv")

# Try to resume from previous scoring
try:
    scored_df = pd.read_csv("reddit_posts_scored.csv")
    print("📂 Existing scored file found. Resuming...")
except FileNotFoundError:
    scored_df = df.copy()
    scored_df["misinfo_label"] = None
    scored_df["misinfo_confidence"] = None
    scored_df["misinfo_reason"] = None
    scored_df["misinfo_category"] = None

# Add missing column if needed
if "misinfo_category" not in scored_df.columns:
    scored_df["misinfo_category"] = None

# Only score rows where either label or category is missing
unscored = scored_df[
    scored_df["misinfo_label"].isnull() |
    scored_df["misinfo_category"].isnull()
]

# Gemini model
model = genai.GenerativeModel("models/gemini-2.0-flash")

# Batch size (free tier safe)
batch_size = 10
batch = unscored.head(batch_size)

for index, row in batch.iterrows():
    title = row["title"]
    prompt = f"""You are a misinformation classification assistant.

Given this Reddit post title:
"{title}"

Respond in this exact JSON format:
{{
  "label": true or false,
  "confidence": float between 0 and 1,
  "reason": "short explanation",
  "category": "clickbait" | "unsupported claim" | "conspiracy" | "satire" | "misleading context" | "none"
}}

DO NOT explain anything. Only return the valid JSON object.
"""

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()

        block_match = re.search(r"\{.*\}", result_text, re.DOTALL)
        cleaned = block_match.group(0) if block_match else "{}"

        cleaned = re.sub(r'\btrue\b', 'True', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'\bfalse\b', 'False', cleaned, flags=re.IGNORECASE)
        result = ast.literal_eval(cleaned)

        scored_df.at[index, "misinfo_label"] = result.get("label")
        scored_df.at[index, "misinfo_confidence"] = result.get("confidence")
        scored_df.at[index, "misinfo_reason"] = result.get("reason")
        scored_df.at[index, "misinfo_category"] = result.get("category")

        print(f"✅ Scored: {title[:60]}...")
        time.sleep(4)  # Respect Gemini's free-tier limit

    except Exception as e:
        print(f"❌ Error: {e}")
        scored_df.at[index, "misinfo_label"] = scored_df.at[index, "misinfo_label"] or None
        scored_df.at[index, "misinfo_confidence"] = scored_df.at[index, "misinfo_confidence"] or None
        scored_df.at[index, "misinfo_reason"] = "Error or invalid response"
        scored_df.at[index, "misinfo_category"] = scored_df.at[index, "misinfo_category"] or None
        time.sleep(4)

# Save progress
scored_df.to_csv("reddit_posts_scored.csv", index=False)
print("✅ Batch complete. Saved to reddit_posts_scored.csv.")

# Show progress
remaining = scored_df["misinfo_category"].isnull().sum()
total = len(scored_df)
if remaining == 0:
    print(f"🎉 All {total} posts are fully scored with categories!")
else:
    print(f"🔄 {remaining} out of {total} posts still need categories.")
