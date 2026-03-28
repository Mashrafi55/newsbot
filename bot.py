from google import genai
from dotenv import load_dotenv
import requests
import os

# Load keys from .env file
load_dotenv()
NEWS_API_KEY=os.getenv("NEWS_API_KEY")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")


# Setup Gemini
client = genai.Client(api_key=GEMINI_API_KEY)

def get_news(country_code):
    url = f"https://newsapi.org/v2/top-headlines?country={country_code}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        return f"Error fetching news: {response.status_code}"

    articles = response.json().get('articles', [])

    if not articles:
        return "No news found for this country."

    news_text = ""
    for a in articles[:5]:
        title = a.get('title', 'No title')
        description = a.get('description', 'No description')
        news_text += f"- {title}: {description}\n"

    return news_text

def summarize(news_text):
    prompt = f"""Based ONLY on the following news articles, provide:
1. A 3-sentence neutral summary
2. The main topics covered

News data:
{news_text}"""

    response = client.models.generate_content(
        model="gemini-2.0-flash-lite",
        contents=prompt
    )
    return response.text

# Main program
print("=== NewsBot ===")
country = input("Enter country code (bd = Bangladesh, us = USA, gb = UK): ")
print("\nFetching news...\n")

raw_news = get_news(country)
print("--- Raw Headlines ---")
print(raw_news)

print("--- AI Summary ---")
print(summarize(raw_news))


