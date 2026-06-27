import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

url = "https://www.googleapis.com/youtube/v3/videos"

params = {
    "part": "snippet,statistics",
    "chart": "mostPopular",
    "regionCode": "IN",
    "maxResults": 10,
    "key": API_KEY
}

response = requests.get(url, params=params)

print(response.status_code)
print(response.json())