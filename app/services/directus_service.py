import os
import logging
import requests
from typing import Optional
from cachetools import TTLCache
import threading


class DirectusService:
    """
    Service for fetching content from Directus CMS.
    Uses DIRECTUS_URL and DIRECTUS_API_KEY environment variables.
    """

    _instance = None
    _lock = threading.Lock()
    _cache = TTLCache(maxsize=100, ttl=300)

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(DirectusService, cls).__new__(cls)
                cls._instance._url = os.getenv("DIRECTUS_URL", "").rstrip("/")
                cls._instance._key = os.getenv("DIRECTUS_API_KEY", "")
                if not cls._instance._url:
                    logging.warning(
                        "DIRECTUS_URL not configured. DirectusService will fail."
                    )
            return cls._instance

    def get_advice_module(
        self, slug: str
    ) -> Optional[dict[str, str | int | float | bool | None]]:
        """
        Fetches advice module content by slug from the 'advice_modules' collection.
        Returns None if not found or on error.
        """
        if not self._url:
            return None
        cache_key = f"advice_module:{slug}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            headers = {
                "Authorization": f"Bearer {self._key}",
                "Content-Type": "application/json",
            }
            endpoint = f"{self._url}/items/advice_modules"
            params = {"filter[slug][_eq]": slug, "limit": 1}
            response = requests.get(
                endpoint, headers=headers, params=params, timeout=10
            )
            if response.status_code == 200:
                data = response.json().get("data", [])
                if data and len(data) > 0:
                    result = data[0]
                    self._cache[cache_key] = result
                    return result
            else:
                logging.error(
                    f"Directus API Error ({response.status_code}): {response.text}"
                )
        except Exception as e:
            logging.exception(
                f"Failed to fetch advice module '{slug}' from Directus: {e}"
            )
        return None