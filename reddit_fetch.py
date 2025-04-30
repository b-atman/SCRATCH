import praw
import pandas as pd

# 🔐 Replace with your Reddit credentials
reddit = praw.Reddit(
    client_id="5deX_rNo05ASkZVQHt7b8g",
    client_secret="8qiFecX77I80iGoDoOToF_9sZT4fhg",
    user_agent="misinfoRadar by u/SelectTour9182"
)

# 🔍 Pull top posts from a few relevant subreddits
subreddits = ["worldnews", "news", "politics", "technology"]
posts = []

for subreddit in subreddits:
    for post in reddit.subreddit(subreddit).hot(limit=50):
        posts.append({
            "title": post.title,
            "score": post.score,
            "id": post.id,
            "subreddit": subreddit,
            "url": post.url,
            "num_comments": post.num_comments,
            "created": post.created_utc,
            "selftext": post.selftext
        })

# Save to CSV
df = pd.DataFrame(posts)
df.to_csv("reddit_posts.csv", index=False)
print("✅ Data saved to reddit_posts.csv")
