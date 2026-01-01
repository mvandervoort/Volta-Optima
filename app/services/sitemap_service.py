import os
import datetime
from supabase import create_client, Client
import logging
from app.constants import BASE_URL


class SitemapService:
    STATIC_ROUTES = [
        {"loc": "/", "priority": 1.0, "changefreq": "daily"},
        {"loc": "/aanleiding", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/faq", "priority": 0.6, "changefreq": "monthly"},
        {"loc": "/solar", "priority": 0.9, "changefreq": "weekly"},
        {"loc": "/advice-themes", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/battery", "priority": 0.9, "changefreq": "weekly"},
        {"loc": "/advice/simple/battery", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/advice/advanced/battery", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/advice/solar-theme", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/dakscan", "priority": 0.9, "changefreq": "weekly"},
        {"loc": "/warm-water", "priority": 0.9, "changefreq": "weekly"},
        {"loc": "/kb", "priority": 0.8, "changefreq": "daily"},
        {"loc": "/wiki", "priority": 0.8, "changefreq": "weekly"},
        {"loc": "/blog", "priority": 0.8, "changefreq": "daily"},
        {"loc": "/contact-about", "priority": 0.7, "changefreq": "monthly"},
        {"loc": "/about", "priority": 0.7, "changefreq": "monthly"},
        {"loc": "/algemene-voorwaarden", "priority": 0.3, "changefreq": "yearly"},
        {"loc": "/privacybeleid", "priority": 0.3, "changefreq": "yearly"},
        {"loc": "/login", "priority": 0.4, "changefreq": "monthly"},
        {"loc": "/signup", "priority": 0.4, "changefreq": "monthly"},
        {"loc": "/forgot-password", "priority": 0.3, "changefreq": "monthly"},
        {"loc": "/reset-password", "priority": 0.3, "changefreq": "monthly"},
    ]

    @staticmethod
    def get_sitemap_xml() -> str:
        """
        Generates the sitemap.xml content as a string.
        """
        base_url = BASE_URL
        try:
            logging.info("Generating sitemap XML...")
            urls = []
            today_iso = datetime.date.today().isoformat()
            for route in SitemapService.STATIC_ROUTES:
                urls.append(
                    {
                        "loc": f"{base_url}{route['loc']}",
                        "lastmod": today_iso,
                        "priority": str(route["priority"]),
                        "changefreq": route["changefreq"],
                    }
                )
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_KEY")
            if supabase_url and supabase_key:
                try:
                    supabase: Client = create_client(supabase_url, supabase_key)
                    try:
                        kb_response = (
                            supabase.table("cms_content")
                            .select("id, updated_at")
                            .eq("status", "published")
                            .eq("show_in_kb", True)
                            .execute()
                        )
                        for item in kb_response.data:
                            if item.get("id"):
                                urls.append(
                                    {
                                        "loc": f"{base_url}/kb/{item.get('id')}",
                                        "lastmod": SitemapService._parse_date(
                                            item.get("updated_at")
                                        )
                                        or today_iso,
                                        "priority": "0.7",
                                        "changefreq": "weekly",
                                    }
                                )
                    except Exception as e:
                        logging.exception(
                            f"Error fetching KB articles for sitemap: {e}"
                        )
                    try:
                        blog_response = (
                            supabase.table("cms_content")
                            .select("slug, updated_at")
                            .eq("status", "published")
                            .execute()
                        )
                        for item in blog_response.data:
                            if item.get("slug"):
                                urls.append(
                                    {
                                        "loc": f"{base_url}/blog/{item.get('slug')}",
                                        "lastmod": SitemapService._parse_date(
                                            item.get("updated_at")
                                        )
                                        or today_iso,
                                        "priority": "0.7",
                                        "changefreq": "weekly",
                                    }
                                )
                    except Exception as e:
                        logging.exception(
                            f"Error fetching blog articles for sitemap: {e}"
                        )
                except Exception as e:
                    logging.exception(f"Failed to initialize Supabase for sitemap: {e}")
            else:
                logging.warning(
                    "Supabase credentials missing - skipping dynamic routes for sitemap."
                )
            xml_lines = [
                '<?xml version="1.0" encoding="UTF-8"?>',
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
            ]
            for url in urls:
                xml_lines.append("  <url>")
                xml_lines.append(f"    <loc>{url['loc']}</loc>")
                xml_lines.append(f"    <lastmod>{url['lastmod']}</lastmod>")
                xml_lines.append(f"    <changefreq>{url['changefreq']}</changefreq>")
                xml_lines.append(f"    <priority>{url['priority']}</priority>")
                xml_lines.append("  </url>")
            xml_lines.append("</urlset>")
            return """
""".join(xml_lines)
        except Exception as e:
            logging.exception(f"Critical error generating sitemap: {e}")
            return ""

    @staticmethod
    def get_robots_txt() -> str:
        """
        Returns content for robots.txt
        """
        base_url = BASE_URL
        return f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n"

    @staticmethod
    def _parse_date(date_str: str | None) -> str | None:
        """Helper to parse ISO dates safely."""
        if not date_str:
            return None
        try:
            if date_str.endswith("Z"):
                date_str = date_str[:-1] + "+00:00"
            dt = datetime.datetime.fromisoformat(date_str)
            return dt.date().isoformat()
        except Exception as e:
            logging.exception(f"Error parsing date {date_str}: {e}")
            return None