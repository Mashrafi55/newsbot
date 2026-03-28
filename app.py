from flask import Flask, request, jsonify, render_template
from groq import Groq
from dotenv import load_dotenv
import requests
import os

# Load keys
load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Setup Groq
client = Groq(api_key=GROQ_API_KEY)

# Setup Flask
app = Flask(__name__)

# Country codes and names
COUNTRY_NAMES = {
    "au": "Australia", "br": "Brazil", "ca": "Canada", "cn": "China",
    "eg": "Egypt", "fr": "France", "de": "Germany", "gr": "Greece",
    "hk": "Hong Kong", "in": "India", "ie": "Ireland", "il": "Israel",
    "it": "Italy", "jp": "Japan", "nl": "Netherlands", "no": "Norway",
    "pk": "Pakistan", "pe": "Peru", "ph": "Philippines", "pt": "Portugal",
    "ro": "Romania", "ru": "Russia", "sg": "Singapore", "es": "Spain",
    "se": "Sweden", "ch": "Switzerland", "tw": "Taiwan", "ua": "Ukraine",
    "gb": "UK", "us": "USA"
}

def get_news(query):
    if query.lower() in COUNTRY_NAMES:
        url = f"https://gnews.io/api/v4/top-headlines?country={query}&apikey={NEWS_API_KEY}&lang=en"
    else:
        url = f"https://gnews.io/api/v4/search?q={query}&apikey={NEWS_API_KEY}&lang=en"

    response = requests.get(url)

    if response.status_code != 200:
        return None

    articles = response.json().get('articles', [])
    return articles[:10]

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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/results")
def results():
    return render_template("results.html")

@app.route("/search", methods=["POST"])
def search():
    query = request.json.get("query", "")
    articles = get_news(query)

    if not articles:
        return jsonify({"error": "No news found. Try a different search term."})

    news_text = ""
    for a in articles:
        title = a.get('title', 'No title')
        description = a.get('description', 'No description')
        date = a.get('publishedAt', 'Unknown date')[:10]
        news_text += f"- [{date}] {title}: {description}\n"

    summary = summarize(news_text)

    return jsonify({
        "articles": articles,
        "summary": summary
    })

if __name__ == "__main__":
    app.run(debug=True)