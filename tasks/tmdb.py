import os
import requests

TMDB_BASE = "https://api.themoviedb.org/3"

def discover_tv_top10(provider_id: int, region: str = "FR", page: int = 1, language: str = "fr-FR"):
    """
    Returns a list of up to 10 TV shows from TMDB Discover filtered by watch provider.
    Requires TMDB_BEARER_TOKEN in environment (v4 Read Access Token).
    """
    token = os.getenv("TMDB_BEARER_TOKEN")
    if not token:
        raise RuntimeError("Missing TMDB_BEARER_TOKEN env var (TMDB v4 Read Access Token)")

    url = f"{TMDB_BASE}/discover/tv"
    params = {
        "language": language,
        "watch_region": region,
        "with_watch_providers": str(provider_id),
        "with_watch_monetization_types": "flatrate",
        "sort_by": "vote_average.desc",
        "vote_count.gte": 200,
        "page": page,
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "accept": "application/json",
    }

    r = requests.get(url, params=params, headers=headers, timeout=15)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])[:10]
