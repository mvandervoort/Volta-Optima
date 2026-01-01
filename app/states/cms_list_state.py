import reflex as rx
from app.services.cms_service import CMSService
import logging
from datetime import datetime, timezone


class CMSListState(rx.State):
    posts: list[dict[str, object]] = []
    search_query: str = ""
    filter_status: str = ""
    filter_language: str = ""
    filter_category: str = ""
    categories: list[dict[str, str]] = []
    selected_ids: list[str] = []

    @rx.event
    def on_load(self):
        self.categories = CMSService.list_categories()
        self.load_posts()

    def _format_relative_date(self, iso_str: str) -> str:
        if not iso_str:
            return "Never"
        try:
            if iso_str.endswith("Z"):
                iso_str = iso_str[:-1] + "+00:00"
            dt = datetime.fromisoformat(iso_str)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - dt
            seconds = diff.total_seconds()
            if seconds < 60:
                return "Just now"
            elif seconds < 3600:
                mins = int(seconds / 60)
                return f"{mins} min{('s' if mins != 1 else '')} ago"
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f"{hours} hour{('s' if hours != 1 else '')} ago"
            elif diff.days < 7:
                return f"{diff.days} day{('s' if diff.days != 1 else '')} ago"
            else:
                return dt.strftime("%b %d, %Y")
        except Exception as e:
            logging.exception(f"Date formatting error: {e}")
            return str(iso_str)[:10]

    @rx.event
    def load_posts(self):
        raw_posts = CMSService.list_content(
            language=self.filter_language if self.filter_language else None,
            status=self.filter_status if self.filter_status else None,
            search=self.search_query if self.search_query else None,
            category_id=self.filter_category if self.filter_category else None,
        )
        processed_posts = []
        for post in raw_posts:
            p = post.copy()
            p["updated_at_formatted"] = self._format_relative_date(
                p.get("updated_at", "")
            )
            processed_posts.append(p)
        self.posts = processed_posts
        self.selected_ids = []

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query
        self.load_posts()

    @rx.event
    def set_filter_status(self, status: str):
        self.filter_status = status
        self.load_posts()

    @rx.event
    def set_filter_language(self, lang: str):
        self.filter_language = lang
        self.load_posts()

    @rx.event
    def set_filter_category(self, cat_id: str):
        self.filter_category = cat_id
        self.load_posts()

    @rx.event
    def duplicate_post(self, post_id: str):
        post = CMSService.get_content(post_id)
        if post:
            new_data = post.copy()
            if "id" in new_data:
                del new_data["id"]
            if "created_at" in new_data:
                del new_data["created_at"]
            if "updated_at" in new_data:
                del new_data["updated_at"]
            new_data["title"] = f"{new_data.get('title', '')} (Copy)"
            new_data["slug"] = f"{new_data.get('slug', '')}-copy"
            new_data["status"] = "draft"
            try:
                CMSService.create_content(new_data)
                rx.toast.success("Post duplicated successfully")
                self.load_posts()
            except Exception as e:
                logging.exception(f"Error duplicating post: {e}")
                rx.toast.error("Failed to duplicate post")

    @rx.event
    def delete_post(self, post_id: str):
        if CMSService.delete_content(post_id):
            rx.toast.success("Post deleted")
            self.load_posts()
        else:
            rx.toast.error("Failed to delete post")

    @rx.event
    def toggle_selection(self, post_id: str):
        if post_id in self.selected_ids:
            self.selected_ids.remove(post_id)
        else:
            self.selected_ids.append(post_id)

    @rx.event
    def toggle_all_selection(self):
        if len(self.selected_ids) == len(self.posts):
            self.selected_ids = []
        else:
            self.selected_ids = [str(p.get("id")) for p in self.posts if p.get("id")]

    @rx.event
    def bulk_delete(self):
        count = 0
        for pid in self.selected_ids:
            if CMSService.delete_content(pid):
                count += 1
        self.selected_ids = []
        self.load_posts()
        rx.toast.success(f"Deleted {count} posts")