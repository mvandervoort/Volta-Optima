import reflex as rx
import json
from app.constants import BASE_URL


def get_url(path: str | rx.Var) -> str | rx.Var:
    if isinstance(path, rx.Var):
        return f"{BASE_URL}" + path
    return f"{BASE_URL}{path}"


def generate_meta_tags(
    title: str | rx.Var,
    description: str | rx.Var,
    image: str | rx.Var = "/og-image.png",
    url: str | rx.Var = "/",
    type: str = "website",
    twitter_card: str = "summary_large_image",
) -> list[dict]:
    """
    Generate a list of meta tags for SEO.
    """
    full_url = get_url(url)
    full_image = get_url(image)
    return [
        {"name": "description", "content": description},
        {"property": "og:title", "content": title},
        {"property": "og:description", "content": description},
        {"property": "og:image", "content": full_image},
        {"property": "og:url", "content": full_url},
        {"property": "og:type", "content": type},
        {"property": "og:site_name", "content": "Energie Insight"},
        {"name": "twitter:card", "content": twitter_card},
        {"name": "twitter:title", "content": title},
        {"name": "twitter:description", "content": description},
        {"name": "twitter:image", "content": full_image},
    ]


def organization_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": "Energie Insight",
        "url": BASE_URL,
        "logo": f"{BASE_URL}/logo.png",
        "description": "Datagestuurde energie-inzichten voor de Nederlandse markt.",
        "address": {
            "@type": "PostalAddress",
            "addressLocality": "Amsterdam",
            "addressCountry": "NL",
        },
        "sameAs": [
            "https://linkedin.com/company/energie-insight",
            "https://twitter.com/energieinsight",
        ],
    }


def webpage_schema(title: str, description: str, url: str) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": f"{BASE_URL}{url}",
        "publisher": {"@type": "Organization", "name": "Energie Insight"},
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict:
    """items: list of (name, url)"""
    item_list = []
    for i, (name, url) in enumerate(items):
        item_list.append(
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"{BASE_URL}{url}",
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list,
    }


def faq_schema(items: list[dict[str, str]]) -> dict:
    """items: list of dicts with 'question' and 'answer' keys"""
    faq_items = []
    for item in items:
        faq_items.append(
            {
                "@type": "Question",
                "name": item.get("question", ""),
                "acceptedAnswer": {"@type": "Answer", "text": item.get("answer", "")},
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": faq_items,
    }