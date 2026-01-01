import reflex as rx
from .base_state import State
from app.services.cms_service import CMSService
import logging


class BlogState(State):
    posts: list[dict[str, object]] = []
    current_post: dict[str, object] = {}
    is_loading: bool = False

    @rx.event
    def load_posts(self):
        from app.utils.html_utils import encode_html_images, clean_cms_html

        self.is_loading = True
        try:
            categories = CMSService.list_categories()
            blog_cat = next((c for c in categories if c.get("slug") == "blog"), None)
            if blog_cat:
                raw_posts = CMSService.list_content(
                    status="published", category_id=blog_cat["id"]
                )
            else:
                raw_posts = []
            processed_posts = []
            for p in raw_posts:
                cat_name = "Uncategorized"
                if p.get("categories"):
                    cat_name = p["categories"].get("name", "Uncategorized")
                processed_posts.append(
                    {
                        "title": p.get("title", "Untitled"),
                        "date": str(p.get("created_at", ""))[:10],
                        "excerpt": p.get("excerpt", ""),
                        "slug": p.get("slug", ""),
                        "category": cat_name,
                        "content_html": clean_cms_html(
                            encode_html_images(p.get("content_html", ""))
                        ),
                        "id": p.get("id"),
                    }
                )
            self.posts = processed_posts
        except Exception as e:
            logging.exception(f"Error loading blog posts: {e}")
            self.posts = []
        finally:
            self.is_loading = False

    @rx.event
    def load_current_post(self):
        from app.utils.html_utils import clean_cms_html

        params = self.router.page.params
        slug = params.get("slug")
        if not slug:
            return
        self.is_loading = True
        try:
            post = CMSService.get_content_by_slug(slug)
            if post:
                cat_name = "Uncategorized"
                if post.get("categories"):
                    cat_name = post["categories"].get("name", "Uncategorized")
                self.current_post = {
                    "title": post.get("title", "Untitled"),
                    "date": str(post.get("created_at", ""))[:10],
                    "excerpt": post.get("excerpt", ""),
                    "slug": post.get("slug", ""),
                    "category": cat_name,
                    "content_html": clean_cms_html(post.get("content_html", "")),
                    "id": post.get("id"),
                    "author": "Volta Expert",
                }
            else:
                self.current_post = None
        except Exception as e:
            logging.exception(f"Error loading post {slug}: {e}")
            self.current_post = None
        finally:
            self.is_loading = False