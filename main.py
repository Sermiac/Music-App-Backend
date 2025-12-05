from requests import auth
from fastapi import FastAPI, Depends
import requests, json, base64, os, secrets, time
from dotenv import load_dotenv
from fastapi.responses import RedirectResponse
from urllib.parse import urlencode


from fastapi.middleware.cors import CORSMiddleware


if os.environ.get("RENDER") != "true":
    load_dotenv("credentials.env")

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID");
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET");
REDIRECT_URI = os.getenv("REDIRECT_URI")
URL= os.getenv("URL")
TOKEN_URL = "https://accounts.spotify.com/api/token"



app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        URL,
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

@app.on_event("startup")
def startup_event():
    global token
    token = get_token()



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

    value = res.json()
    if "access_token" not in value:
        print("ERROR AL OBTENER TOKEN:", value)
        raise RuntimeError("No se pudo obtener el access_token")

    start=time.time()

    return value

token = None
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
            f"https://api.spotify.com/v1/search?q={search}&type=track&limit=50",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        new_offset += 50
        data = res.json()
        merged_data.extend(data["tracks"]["items"])

    tracks = merged_data
    albums = {}
    for track in tracks:
        album = track["album"]
        album_id = album["id"]
        albums[album_id] = album   # Guardamos por ID para evitar duplicados
    return list(albums.values())


def generate_random_string(length=16):
    return secrets.token_urlsafe(length)[:length]


@app.get("/backend/login")
def login():
    state = generate_random_string()
    scope = "user-read-private user-read-email"

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "scope": scope,
        "state": state,
    }

    url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    return RedirectResponse(url)

user_token = None
@app.get("/backend/callback")
def callback(code: str | None = None, state: str | None = None):
    global user_token

    if code is None:
        return "Error: no se recibió el código de Spotify", 400

    # Intercambiar el "code" por tokens
    token_url = "https://accounts.spotify.com/api/token"

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    response = requests.post(token_url, data=payload)
    token_info = response.json()

    # Token recibido
    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")

    user_token = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": token_info.get("token_type"),
        "expires_in": token_info.get("expires_in")
    }

    return RedirectResponse(URL)

@app.get("/backend/basic-login")
def basicLogin():
    global user_token
    if user_token:
        access_token = user_token["access_token"]

        res = requests.get(
             f"https://api.spotify.com/v1/me",
              headers={"Authorization": f"Bearer {access_token}"},
         )

        data = res.json()
        image = data["images"][1]["url"]
        print(data)

        return image