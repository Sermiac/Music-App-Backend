# **Music App – Backend (FastAPI)**

A lightweight backend built with **FastAPI** that connects to the **Spotify Web API** using the Client Credentials Flow.
It provides endpoints for browsing new releases and searching tracks, with automatic token regeneration and CORS support for a separate frontend.

## **Frontend Repo**

> https://github.com/Sermiac/Music-App-Frontend


## **Features**

* Fetch latest music releases from Spotify.
* Search tracks by name.
* Automatic Spotify access token handling (refresh on expiration).
* CORS configured for a specific frontend domain.
* Ready for deployment on **Render**.
* Simple, clean API responses for frontend consumption.


## **Tech Stack**

* **Python 3.10+**
* **FastAPI**
* **Uvicorn**
* **Requests**
* **Dotenv** (development only)
* **Spotify Web API**


## **Environment Variables**

### **Local development**

Create a file called:

```
credentials.env
```

Inside include:

```
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
URL=http://localhost:5173
```

> The `URL` variable is used to configure allowed origins in CORS.

## **Installation**

### **1. Create virtual environment**

```
python3 -m venv venv
source venv/bin/activate
```

### **2. Install dependencies**

```
pip install -r requirements.txt
```


## **Run Locally**

```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at:

```
http://localhost:8000
```


## **API Endpoints**

### **1. New Releases**

```
GET /backend/new-releases
```

Returns a list of new albums based on Spotify’s “New Releases” endpoint.

### **2. Search Tracks**

```
GET /backend/search-tracks?search=<query>
```

Returns track search results, normalized for frontend usage.



## **Spotify Token Management**

This backend uses Spotify’s **Client Credentials Flow**:

* On first request, it fetches an `access_token`.
* It stores a timestamp.
* Before each request, it checks if the token is expired.
* If expired, it automatically generates a new one.

This avoids hitting Spotify’s rate limits and prevents 401 errors.

## **License**

This project is for personal and educational use.