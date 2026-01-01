import os
import logging
import reflex as rx
from supabase import create_client, Client
from typing import Optional
import json
from cachetools import TTLCache
import threading


class CMSService:
    _client: Optional[Client] = None
    _content_cache = TTLCache(maxsize=1000, ttl=300)
    _list_cache = TTLCache(maxsize=100, ttl=300)
    _category_cache = TTLCache(maxsize=10, ttl=300)
    _lock = threading.RLock()

    @classmethod
    def get_client(cls) -> Client:
        """Get the Supabase client, reusing existing instance or creating a new one."""
        if cls._client:
            return cls._client
        try:
            from app.services.supabase_client import supabase

            if supabase:
                cls._client = supabase
                return cls._client
        except (ImportError, AttributeError) as e:
            logging.exception(
                f"Could not import 'supabase' from app.services.supabase_client. Falling back to env vars. Error: {e}"
            )
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            logging.error(
                "SUPABASE_URL or SUPABASE_KEY missing from environment variables."
            )
            raise ValueError("Supabase credentials not configured")
        cls._client = create_client(url, key)
        return cls._client

    @classmethod
    def _invalidate_content_caches(cls, content_id: str = None, slug: str = None):
        """Invalidate content caches safely."""
        with cls._lock:
            cls._list_cache.clear()
            if content_id:
                key_id = f"id:{content_id}"
                if key_id in cls._content_cache:
                    del cls._content_cache[key_id]
            if slug:
                key_slug = f"slug:{slug}"
                if key_slug in cls._content_cache:
                    del cls._content_cache[key_slug]
            if content_id and (not slug):
                keys_to_remove = []
                for k, v in cls._content_cache.items():
                    if v and str(v.get("id")) == str(content_id):
                        keys_to_remove.append(k)
                for k in keys_to_remove:
                    if k in cls._content_cache:
                        del cls._content_cache[k]

    @classmethod
    def _invalidate_category_caches(cls):
        """Invalidate category caches."""
        with cls._lock:
            cls._category_cache.clear()

    @classmethod
    def list_content(
        cls,
        language: str = None,
        status: Optional[str] = None,
        search: str = None,
        category_id: str = None,
    ) -> list[dict[str, object]]:
        """List content items with optional filtering."""
        cache_key = f"list:{language}:{status}:{search}:{category_id}"
        with cls._lock:
            if cache_key in cls._list_cache:
                return cls._list_cache[cache_key]
        try:
            client = cls.get_client()
            query = client.table("cms_content").select(
                "*, categories:category_id(name, slug)"
            )
            if language:
                query = query.eq("language", language)
            if status:
                query = query.eq("status", status)
            if category_id:
                query = query.eq("category_id", category_id)
            if search:
                query = query.ilike("title", f"%{search}%")
            response = query.order("created_at", desc=True).execute()
            data = response.data if response else []
            with cls._lock:
                cls._list_cache[cache_key] = data
            return data
        except Exception as e:
            logging.exception(f"Error listing content: {e}")
            return []

    @classmethod
    def get_kb_articles(cls) -> list[dict[str, object]]:
        """List published articles that are explicitly visible in KB."""
        cache_key = "kb_articles"
        with cls._lock:
            if cache_key in cls._list_cache:
                return cls._list_cache[cache_key]
        try:
            client = cls.get_client()
            response = (
                client.table("cms_content")
                .select("*, categories:category_id(name, slug)")
                .eq("status", "published")
                .eq("show_in_kb", True)
                .order("created_at", desc=True)
                .execute()
            )
            data = response.data if response else []
            with cls._lock:
                cls._list_cache[cache_key] = data
            return data
        except Exception as e:
            logging.exception(f"Error listing KB articles: {e}")
            return []

    @classmethod
    def get_content(cls, content_id: str) -> Optional[dict[str, object]]:
        cache_key = f"id:{content_id}"
        with cls._lock:
            if cache_key in cls._content_cache:
                return cls._content_cache[cache_key]
        try:
            client = cls.get_client()
            response = (
                client.table("cms_content")
                .select("*, categories:category_id(name, slug)")
                .eq("id", content_id)
                .maybe_single()
                .execute()
            )
            data = response.data if response else None
            with cls._lock:
                if data:
                    cls._content_cache[cache_key] = data
                    if data.get("slug"):
                        cls._content_cache[f"slug:{data['slug']}"] = data
            return data
        except Exception as e:
            logging.exception(f"Error getting content {content_id}: {e}")
            return None

    @classmethod
    def get_content_by_slug(cls, slug: str) -> Optional[dict[str, object]]:
        cache_key = f"slug:{slug}"
        with cls._lock:
            if cache_key in cls._content_cache:
                return cls._content_cache[cache_key]
        try:
            client = cls.get_client()
            response = (
                client.table("cms_content")
                .select("*, categories:category_id(name, slug)")
                .eq("slug", slug)
                .maybe_single()
                .execute()
            )
            data = response.data if response else None
            with cls._lock:
                if data:
                    cls._content_cache[cache_key] = data
                    if data.get("id"):
                        cls._content_cache[f"id:{data['id']}"] = data
            return data
        except Exception as e:
            logging.exception(f"Error getting content by slug {slug}: {e}")
            return None

    @classmethod
    def create_content(cls, data: dict[str, object]) -> dict[str, object]:
        try:
            client = cls.get_client()
            response = client.table("cms_content").insert(data).execute()
            if response and response.data:
                result = response.data[0]
                cls._invalidate_content_caches(
                    content_id=result.get("id"), slug=result.get("slug")
                )
                return result
            return None
        except Exception as e:
            logging.exception(f"Error creating content: {e}")
            raise e

    @classmethod
    def update_content(
        cls, content_id: str, data: dict[str, object]
    ) -> dict[str, object]:
        try:
            client = cls.get_client()
            data["updated_at"] = "now()"
            response = (
                client.table("cms_content").update(data).eq("id", content_id).execute()
            )
            if response and response.data:
                result = response.data[0]
                cls._invalidate_content_caches(
                    content_id=content_id, slug=result.get("slug")
                )
                return result
            return None
        except Exception as e:
            logging.exception(f"Error updating content {content_id}: {e}")
            raise e

    @classmethod
    def delete_content(cls, content_id: str) -> bool:
        try:
            client = cls.get_client()
            client.table("cms_content").delete().eq("id", content_id).execute()
            cls._invalidate_content_caches(content_id=content_id)
            return True
        except Exception as e:
            logging.exception(f"Error deleting content {content_id}: {e}")
            return False

    @classmethod
    def list_categories(cls) -> list[dict[str, str]]:
        cache_key = "all_categories"
        with cls._lock:
            if cache_key in cls._category_cache:
                return cls._category_cache[cache_key]
        try:
            client = cls.get_client()
            response = (
                client.table("cms_categories").select("*").order("name").execute()
            )
            data = response.data if response else []
            with cls._lock:
                cls._category_cache[cache_key] = data
            return data
        except Exception as e:
            logging.exception(f"Error listing categories: {e}")
            return []

    @classmethod
    def create_category(cls, data: dict[str, object]) -> dict[str, object]:
        try:
            client = cls.get_client()
            response = client.table("cms_categories").insert(data).execute()
            if response and response.data:
                cls._invalidate_category_caches()
                return response.data[0]
            return None
        except Exception as e:
            logging.exception(f"Error creating category: {e}")
            raise e

    @classmethod
    def update_category(
        cls, category_id: str, data: dict[str, object]
    ) -> dict[str, object]:
        try:
            client = cls.get_client()
            data["updated_at"] = "now()"
            response = (
                client.table("cms_categories")
                .update(data)
                .eq("id", category_id)
                .execute()
            )
            if response and response.data:
                cls._invalidate_category_caches()
                return response.data[0]
            return None
        except Exception as e:
            logging.exception(f"Error updating category {category_id}: {e}")
            raise e

    @classmethod
    def delete_category(cls, category_id: str) -> bool:
        try:
            client = cls.get_client()
            client.table("cms_categories").delete().eq("id", category_id).execute()
            cls._invalidate_category_caches()
            return True
        except Exception as e:
            logging.exception(f"Error deleting category {category_id}: {e}")
            return False