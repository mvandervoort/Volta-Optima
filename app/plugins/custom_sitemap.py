import reflex as rx
from app.services.sitemap_service import SitemapService


def custom_sitemap_task(unevaluated_pages):
    """
    Task to generate the sitemap XML file using our custom service.
    Returns a tuple of (filename, content).
    """
    content = SitemapService.get_sitemap_xml()
    return ("sitemap.xml", content)


def custom_robots_task(unevaluated_pages):
    """
    Task to generate the robots.txt file using our custom service.
    Returns a tuple of (filename, content).
    """
    content = SitemapService.get_robots_txt()
    return ("robots.txt", content)


class CustomSitemapPlugin(rx.plugins.SitemapPlugin):
    def pre_compile(self, **context):
        """
        Override the pre_compile method to register our custom sitemap and robots tasks.
        This ensures these files are generated during the build process (reflex export).
        """
        unevaluated_pages = context.get("unevaluated_pages", [])
        context["add_save_task"](custom_sitemap_task, unevaluated_pages)
        context["add_save_task"](custom_robots_task, unevaluated_pages)