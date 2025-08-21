#this is all my imports :( 
from dotenv import load_dotenv
from dotenv import dotenv_values
import os
import base64
import json
import requests
import urllib.parse
from requests import post
from openai import OpenAI
load_dotenv()

#these are all my .env variables
client = OpenAI(api_key = os.getenv("API_KEY"))
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_url = os.getenv("SPOTIFY_REDIRECT_URL")

#here is Spotify Auth to authenticate the user
def get_auth_url():
    scope = "user-top-read"
    auth= "https://accounts.spotify.com/authorize"
    params={
        "client_id":client_id,
        "response_type":"code",
        "redirect_uri":redirect_url,
        "scope":scope 
    }
    url=f"{auth}?{urllib.parse.urlencode(params)}"
    return (url)

#this is where I will get the token to access Spotify user profile
def get_token(auth_code):
    token_url= 'https://accounts.spotify.com/api/token'
    data = {
        'code': auth_code,
        'grant_type': 'authorization_code',
        'redirect_uri': redirect_url,
        'client_id': client_id,
        'client_secret':client_secret
    }
    response = requests.post(token_url, data = data)
    return response.json()

#this is a simple function to get the header to access API
def get_header(token):
    return {"Authorization":"Bearer "+ token}

#this is the function to get a specific user's top tracks or artists
def get_top_artists(token, time_range="long_term", limit = 20):
    headers={
        "Authorization": f"Bearer {token}"
    }
    params = {
        "time_range": time_range,
        "limit": limit
    }
    response = requests.get("https://api.spotify.com/v1/me/top/artists", headers = headers, params=params)
    artists = response.json().get("items", [])
    genres = []
    for artist in artists:
        genres.extend(artist.get("genres",[]))
    return list(set(genres)) or ["none"]

#this is where the chatbot handles logic and responds to the user
def chat_with_gpt(prompt, genres):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": "You're a helpful assistant. Answer the user's general questions normally. If the question is about music or preferences, you may refer to the user's Spotify genres."},
            {"role": "assistant", "content": f"User's top Spotify genres: {', '.join(genres[:5])}"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=300
    )
    return response.choices[0].message.content.strip()

if __name__== "__main__":
    print("Visit this URL to connect your Spotify account")
    print(get_auth_url())
    auth_code = input("Paste the redirect code here: ").strip()
    token_info = get_token(auth_code)
    if "access_token" not in token_info:
        print("Failed to get user token")
        exit()

    access_token = token_info["access_token"]
    genres = get_top_artists(access_token)
    print(f"Got your top genres: {', '.join(genres[:5])}")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "exit", "bye"]:
            break
        response = chat_with_gpt(user_input, genres)
        print("ChatBot: ", response)