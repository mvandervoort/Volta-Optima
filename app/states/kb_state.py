import reflex as rx
from .base_state import State
from app.services.cms_service import CMSService
import logging
import datetime


class KnowledgeBaseState(State):
    search_query: str = ""
    articles: list[dict[str, object]] = []
    categories: list[dict[str, str]] = []
    selected_category: str = "All"

    @rx.event
    async def load_articles(self):
        from app.utils.html_utils import encode_html_images, clean_cms_html

        try:
            raw_articles = CMSService.get_kb_articles()
            self.articles = []
            for a in raw_articles:
                created_at = a.get("created_at", "")
                date_str = str(created_at)[:10] if created_at else "Unknown Date"
                article = {
                    "id": str(a.get("id", "")),
                    "title": str(a.get("title", "")),
                    "category": str(
                        a.get("categories", {}).get("name", "Uncategorized")
                    )
                    if a.get("categories")
                    else "Uncategorized",
                    "content": clean_cms_html(
                        encode_html_images(a.get("content_html", ""))
                    ),
                    "excerpt": str(a.get("excerpt", "")),
                    "slug": str(a.get("slug", "")),
                    "requires_auth": bool(a.get("requires_auth", False)),
                    "required_role": str(a.get("required_role", "any")),
                    "date": date_str,
                    "author": "Volta Expert",
                }
                self.articles.append(article)
            self.categories = CMSService.list_categories()
        except Exception as e:
            logging.exception(f"Error loading KB articles: {e}")
            self.articles = []

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.event
    def select_category(self, category: str):
        if self.selected_category == category:
            self.selected_category = "All"
        else:
            self.selected_category = category

    @rx.var
    def filtered_articles(self) -> list[dict[str, object]]:
        filtered = self.articles
        if self.selected_category != "All":
            filtered = [
                a for a in filtered if a.get("category") == self.selected_category
            ]
        if self.search_query:
            query = self.search_query.lower()
            filtered = [
                a
                for a in filtered
                if query in str(a.get("title", "")).lower()
                or query in str(a.get("content", "")).lower()
            ]
        return filtered

    @rx.var
    def category_counts(self) -> dict[str, int]:
        counts = {}
        for a in self.articles:
            cat = a.get("category", "Uncategorized")
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    @rx.var
    def current_article(self) -> dict[str, object]:
        """
        Retrieves the current article based on the route parameter 'article_id'.
        """
        params = self.router.page.params
        article_id = params.get("article_id", "")
        if not article_id:
            return {}
        article_id_str = str(article_id)
        for a in self.articles:
            if str(a.get("id", "")) == article_id_str:
                return a
        return {}

    @rx.var
    def related_articles(self) -> list[dict[str, object]]:
        """
        Finds related articles based on the current article's category.
        """
        params = self.router.page.params
        article_id = params.get("article_id", "")
        current_id_str = str(article_id) if article_id else ""
        current_cat = ""
        for a in self.articles:
            if str(a.get("id", "")) == current_id_str:
                current_cat = a.get("category", "")
                break
        related = [
            a
            for a in self.articles
            if str(a.get("id", "")) != current_id_str
            and (a.get("category") == current_cat or not current_cat)
        ]
        return related[:3]

    @rx.var
    def recent_articles(self) -> list[dict[str, object]]:
        return self.articles[:5]