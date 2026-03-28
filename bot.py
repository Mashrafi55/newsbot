from groq import Groq
from dotenv import load_dotenv
import requests
import os

# Load keys from .env file
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Setup Groq
client = Groq(api_key=GROQ_API_KEY)

# Country codes that GNews supports
COUNTRY_CODES = ["au", "br", "ca", "cn", "eg", "fr", "de", "gr", "hk", "in",
                 "ie", "il", "it", "jp", "nl", "no", "pk", "pe", "ph", "pt",
                 "ro", "ru", "sg", "es", "se", "ch", "tw", "ua", "gb", "us"]

def get_news(query):
    # If it's a supported country code, use top-headlines
    if query.lower() in COUNTRY_CODES:
        url = f"https://gnews.io/api/v4/top-headlines?country={query}&apikey={NEWS_API_KEY}&lang=en"
    else:
        # Otherwise search by keyword (e.g. "bangladesh", "climate change")
        url = f"https://gnews.io/api/v4/search?q={query}&apikey={NEWS_API_KEY}&lang=en"

    response = requests.get(url)

    if response.status_code != 200:
        return f"Error fetching news: {response.status_code}"

    articles = response.json().get('articles', [])

    if not articles:
        return "No news found. Try a different search term."

    news_text = ""
    for a in articles[:5]:
        title = a.get('title', 'No title')
        description = a.get('description', 'No description')
        date = a.get('publishedAt', 'Unknown date')[:10]
        news_text += f"- [{date}] {title}: {description}\n"

    return news_text

def summarize(news_text):
    prompt = f"""Based ONLY on the following news articles, provide:
1. A 3-sentence neutral summary
2. The main topics covered

News data:
{news_text}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# Main program
print("=== NewsBot ===")
print("Tip: Enter a country code (us, gb, in) OR any topic (bangladesh, climate, crypto)")
query = input("Search: ")
print("\nFetching news...\n")

raw_news = get_news(query)
print("--- Raw Headlines ---")
print(raw_news)

print("--- AI Summary ---")
print(summarize(raw_news))