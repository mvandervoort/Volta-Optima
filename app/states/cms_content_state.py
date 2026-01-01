import reflex as rx
from app.services.cms_service import CMSService
import logging


class CMSContentState(rx.State):
    content_cache: dict[str, dict[str, str]] = {}
    loading_slugs: list[str] = []

    @rx.event
    async def get_content(self, slug: str):
        if slug in self.content_cache:
            return
        self.loading_slugs.append(slug)
        try:
            content = CMSService.get_content_by_slug(slug)
            if content:
                self.content_cache[slug] = content
        except Exception as e:
            logging.exception(f"Failed to fetch content for slug {slug}: {e}")
        finally:
            if slug in self.loading_slugs:
                self.loading_slugs.remove(slug)

    @rx.event
    def is_loading(self, slug: str) -> bool:
        return slug in self.loading_slugs