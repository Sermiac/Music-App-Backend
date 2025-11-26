from fastapi import FastAPI, Depends
import requests
import json
import base64
import os
from dotenv import load_dotenv
import json

from fastapi.middleware.cors import CORSMiddleware

# To debug
import time

load_dotenv("credentials.env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID");
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET");
TOKEN_URL = "https://accounts.spotify.com/api/token"

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://192.168.1.16:5174",
        "http://192.168.1.11:5174",
        "http://localhost:5174",
        "http://127.0.0.1:8000",
        "https://music-app-miguel.netlify.app/",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

def is_token_expired(token):
    new = time.time()
    new -= start

    if new >= 3600:
        access_token = token["access_token"]
        res = requests.get(
            "https://api.spotify.com/v1/browse/new-releases?limit=1",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        print(res.status_code)
        return res.status_code == 401
    else: return False

start: float
def get_token():
    global start
    auth_string = f"{CLIENT_ID}:{CLIENT_SECRET}"
    b64_auth = base64.b64encode(auth_string.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = { "grant_type": "client_credentials" }

    res = requests.post(TOKEN_URL, headers=headers, data=data)

    start=time.time()

    return res.json()

token=get_token()

@app.get("/backend/new-releases")
def new_releases():
    global token
    if is_token_expired(token):
        print ("RE-GENERAR TOKEN")
        token = get_token()

    access_token = token["access_token"]


    merged_data = []
    new_offset = 0
    for i in range(1):
        res = requests.get(
            f"https://api.spotify.com/v1/browse/new-releases?limit=50&offset={new_offset}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        new_offset += 50
        data = res.json()
        merged_data.extend(data["albums"]["items"])
    return merged_data


@app.get("/backend/search-tracks")
def search_tracks(search):
    global token
    if is_token_expired(token):
        print ("RE-GENERAR TOKEN")
        token = get_token()

    access_token = token["access_token"]

    merged_data = []
    new_offset = 0
    for i in range(1):
        res = requests.get(
            f"https://api.spotify.com/v1/search?q={search}&type=album&limit=50",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        new_offset += 50
        data = res.json()
        merged_data.extend(data["albums"]["items"])
    return merged_data