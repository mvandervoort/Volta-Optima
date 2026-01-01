import reflex as rx
from app.services.cms_service import CMSService
from app.utils.html_utils import encode_html_images, clean_cms_html
import logging


class ContextCMSState(rx.State):
    challenge_title: str = ""
    challenge_content: str = ""
    faq_items: list[dict[str, str]] = []
    is_loading: bool = False

    @rx.event
    def on_load(self):
        self.is_loading = True
        try:
            challenge_slug = "de-uitdaging"
            challenge_data = CMSService.get_content_by_slug(challenge_slug)
            if challenge_data:
                self.challenge_title = str(challenge_data.get("title") or "")
                raw_content = str(challenge_data.get("content_html") or "")
                self.challenge_content = clean_cms_html(encode_html_images(raw_content))
            categories = CMSService.list_categories()
            faq_cat = next(
                (c for c in categories if c.get("slug") == "aanleiding-faq"), None
            )
            if faq_cat:
                raw_faqs = CMSService.list_content(
                    category_id=faq_cat["id"], status="published"
                )
                self.faq_items = [
                    {
                        "question": str(item.get("title") or ""),
                        "answer": clean_cms_html(item.get("content_html") or ""),
                    }
                    for item in raw_faqs
                ]
            else:
                self.faq_items = []
        except Exception as e:
            logging.exception(f"Error loading context page content: {e}")
        finally:
            self.is_loading = False