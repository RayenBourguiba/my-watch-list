# 🎬 My Watch List

A Django web application that allows users to build and manage a TV
series watchlist.

This project integrates the TMDB API to automatically import top-rated
TV shows from Netflix, Prime Video and Apple TV+.

------------------------------------------------------------------------

## 🚀 Features

-   Manual task creation (original todo functionality)
-   Import top 10 TV series per platform:
    -   Netflix
    -   Prime Video
    -   Apple TV+
-   TMDB Discover TV integration
-   Anti-duplicate logic using (platform, provider_id) constraint
-   Pagination per platform (click twice → 20 different shows)
-   Delete all entries (for testing)
-   SQLite database

------------------------------------------------------------------------

## 🛠 Tech Stack

-   Python 3.13
-   Django 6
-   SQLite
-   TMDB API (v4 Bearer Token)
-   Bootstrap

------------------------------------------------------------------------

## 📦 Installation

### 1️⃣ Clone the repository

git clone `https://github.com/RayenBourguiba/my-watch-list.git`{=html} cd my-watch-list

### 2️⃣ Create a virtual environment

python -m venv venv

Activate it:

Windows (PowerShell): venv`\Scripts`{=tex}`\activate`{=tex}

Mac/Linux: source venv/bin/activate

### 3️⃣ Install dependencies

pip install -r requirements.txt

If you don't have one yet:

pip freeze \> requirements.txt

------------------------------------------------------------------------

## 🔑 TMDB Configuration

Define your TMDB v4 Read Access Token.

Windows PowerShell: \$env:TMDB_BEARER_TOKEN="YOUR_TOKEN_HERE" python
manage.py runserver

Mac/Linux: export TMDB_BEARER_TOKEN="YOUR_TOKEN_HERE" python manage.py
runserver

------------------------------------------------------------------------

## ▶️ Run the Project

python manage.py migrate python manage.py runserver

Open: http://127.0.0.1:8000/

------------------------------------------------------------------------

## 🧠 Anti-Duplicate Strategy

Duplicates are prevented using:

models.UniqueConstraint(fields=\["platform", "provider_id"\])

Data insertion uses:

update_or_create(platform=..., provider_id=...)

------------------------------------------------------------------------

## 📹 Rendu 1

Exercises 1 to 4 implemented. TMDB integration working. Anti-duplicate
logic verified.
