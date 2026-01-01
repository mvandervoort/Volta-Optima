import reflex as rx
import json
from typing import Optional

BASE_URL = "https://www.energie-insight.nl"
COMPANY_NAME = "Energie Insight"
LOGO_URL = f"{BASE_URL}/logo.png"
JsonValue = dict | list | str | int | float | bool | None


def json_ld_script(data: dict[str, JsonValue]) -> rx.Component:
    """
    Generates a script tag with JSON-LD structured data.
    """
    json_string = json.dumps(data, indent=2)
    return rx.el.script(json_string, type="application/ld+json")


def organization_schema() -> dict[str, JsonValue]:
    """
    Returns the Organization schema.
    """
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": COMPANY_NAME,
        "url": BASE_URL,
        "logo": LOGO_URL,
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "",
            "contactType": "customer service",
        },
    }


def breadcrumb_schema(items: list[tuple[str, str]]) -> dict[str, JsonValue]:
    """
    Returns BreadcrumbList schema.
    items: List of (name, url) tuples.
    """
    item_list_element = []
    for i, (name, url) in enumerate(items):
        item_list_element.append(
            {
                "@type": "ListItem",
                "position": i + 1,
                "name": name,
                "item": f"{BASE_URL}{url}" if url.startswith("/") else url,
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list_element,
    }


def software_application_schema(
    name: str,
    description: str,
    url: str,
    application_category: str = "UtilitiesApplication",
    operating_system: str = "Web",
) -> dict[str, JsonValue]:
    """
    Returns SoftwareApplication schema for tools/calculators.
    """
    full_url = f"{BASE_URL}{url}" if url.startswith("/") else url
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": name,
        "description": description,
        "url": full_url,
        "applicationCategory": application_category,
        "operatingSystem": operating_system,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"},
        "author": {"@type": "Organization", "name": COMPANY_NAME},
    }


def faq_schema(faqs: list[tuple[str, str]]) -> dict[str, JsonValue]:
    """
    Returns FAQPage schema.
    faqs: List of (question, answer) tuples.
    """
    main_entity = []
    for question, answer in faqs:
        main_entity.append(
            {
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {"@type": "Answer", "text": answer},
            }
        )
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": main_entity,
    }


def article_schema(
    headline: str,
    description: str,
    image_url: Optional[str] = None,
    date_published: Optional[str] = None,
    author_name: str = COMPANY_NAME,
) -> dict[str, JsonValue]:
    """
    Returns Article schema.
    """
    schema = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": headline,
        "description": description,
        "author": {"@type": "Organization", "name": author_name},
        "publisher": {
            "@type": "Organization",
            "name": COMPANY_NAME,
            "logo": {"@type": "ImageObject", "url": LOGO_URL},
        },
    }
    if image_url:
        schema["image"] = image_url
    if date_published:
        schema["datePublished"] = date_published
    return schema