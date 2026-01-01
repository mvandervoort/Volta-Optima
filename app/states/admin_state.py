import reflex as rx
from .base_state import State
from app.services.cms_service import CMSService
import logging


class AdminState(State):
    total_posts: int = 0
    published_posts: int = 0
    draft_posts: int = 0
    total_categories: int = 0
    recent_activity: list[dict] = []

    @rx.event
    def load_stats(self):
        try:
            posts = CMSService.list_content()
            self.total_posts = len(posts)
            self.published_posts = len(
                [p for p in posts if p.get("status") == "published"]
            )
            self.draft_posts = len([p for p in posts if p.get("status") == "draft"])
            categories = CMSService.list_categories()
            self.total_categories = len(categories)
            sorted_posts = sorted(
                posts, key=lambda x: x.get("updated_at", ""), reverse=True
            )[:5]
            self.recent_activity = []
            for p in sorted_posts:
                created = p.get("created_at")
                updated = p.get("updated_at")
                action = (
                    "Post Updated"
                    if updated and created and (updated != created)
                    else "Post Created"
                )
                time_val = p.get("updated_at", "")
                time_str = (
                    str(time_val)[:16].replace("T", " ") if time_val else "Unknown"
                )
                self.recent_activity.append(
                    {
                        "action": action,
                        "title": p.get("title", "Untitled"),
                        "time": time_str,
                        "status": p.get("status", "unknown"),
                    }
                )
        except Exception as e:
            logging.exception(f"Error loading admin stats: {e}")