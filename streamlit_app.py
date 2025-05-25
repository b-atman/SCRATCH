import streamlit as st
import pandas as pd
import altair as alt

# Load scored dataset
df = pd.read_csv("reddit_posts_scored.csv")
df.dropna(subset=["misinfo_label", "misinfo_category"], inplace=True)

st.title("🧠 Misinformation Radar")
st.markdown("Explore trends and patterns in AI-flagged misinformation from Reddit posts.")

# Sidebar filters
st.sidebar.header("🔍 Filters")

sentiment_range = st.sidebar.slider("Sentiment Polarity", -1.0, 1.0, (-1.0, 1.0), 0.1)
confidence_thresh = st.sidebar.slider("Min Confidence", 0.0, 1.0, 0.0, 0.05)

label_filter = st.sidebar.selectbox("Label", ["All", "Likely Misinformation", "Not Misinformation"])
category_filter = st.sidebar.selectbox(
    "Misinformation Category",
    ["All", "clickbait", "unsupported claim", "conspiracy", "satire", "misleading context", "none"]
)

# Text search input
search_query = st.sidebar.text_input("🔎 Search in post titles", "")

# Apply search filter first
if search_query:
    df = df[df["title"].str.contains(search_query, case=False, na=False)]


# Apply filters
filtered_df = df[
    (df["sentiment"] >= sentiment_range[0]) &
    (df["sentiment"] <= sentiment_range[1]) &
    (df["misinfo_confidence"] >= confidence_thresh)
]

# Fix label string logic
if label_filter != "All":
    target_label = "True" if label_filter == "Likely Misinformation" else "False"
    filtered_df = filtered_df[filtered_df["misinfo_label"].astype(str) == target_label]

if category_filter != "All":
    filtered_df = filtered_df[filtered_df["misinfo_category"] == category_filter]

# Show filtered table
st.subheader("📝 Filtered Posts")
st.dataframe(filtered_df[["title", "sentiment", "misinfo_label", "misinfo_confidence", "misinfo_category", "misinfo_reason"]])

# Add download button
csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered CSV",
    data=csv,
    file_name="misinfo_filtered_posts.csv",
    mime="text/csv"
)


# Chart 1: Confidence vs Sentiment
st.subheader("📈 Confidence vs Sentiment")
chart = alt.Chart(filtered_df).mark_circle(size=60).encode(
    x="sentiment",
    y="misinfo_confidence",
    color=alt.Color("misinfo_category:N", legend=alt.Legend(title="Category")),
    tooltip=["title", "misinfo_reason", "misinfo_category"]
).interactive()
st.altair_chart(chart, use_container_width=True)

# Chart 2: Category Distribution
st.subheader("📊 Category Distribution")
category_counts = df["misinfo_category"].value_counts().reset_index()
category_counts.columns = ["Category", "Count"]

bar_chart = alt.Chart(category_counts).mark_bar().encode(
    x="Category",
    y="Count",
    color="Category"
)
st.altair_chart(bar_chart, use_container_width=True)

# Top 5 Clickbait / Conspiracies
st.subheader("🔥 Top High-Confidence Misinformation Posts")
top_misinfo = df[
    (df["misinfo_label"].astype(str) == "True") &
    (df["misinfo_confidence"] > 0.75)
].sort_values(by="misinfo_confidence", ascending=False).head(5)

st.table(top_misinfo[["title", "misinfo_category", "misinfo_confidence", "misinfo_reason"]])
