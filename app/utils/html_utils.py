import re
import logging
from urllib.parse import urlparse, urlunparse, quote


def encode_html_images(html: str) -> str:
    """
    Parses HTML content, finds <img> tags, and URL-encodes the path part of the src attribute.
    This fixes issues where Directus image URLs containing spaces or special characters fail to render.
    """
    if not html or not isinstance(html, str):
        return ""

    def replace_src(match):
        prefix = match.group(1)
        url = match.group(2)
        suffix = match.group(3)
        try:
            parsed = urlparse(url)
            encoded_path = quote(parsed.path, safe="/")
            new_url = urlunparse(
                (
                    parsed.scheme,
                    parsed.netloc,
                    encoded_path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment,
                )
            )
            return f"{prefix}{new_url}{suffix}"
        except Exception as e:
            logging.exception(f"Error encoding image URL {url}: {e}")
            return match.group(0)

    pattern = '(src=")([^"]+)(")'
    return re.sub(pattern, replace_src, html)


def clean_cms_html(html: str) -> str:
    """
    Radically cleans and configures CMS HTML content to solve text-wrapping and word-breaking issues.
    1. Injects a global style override block inside the HTML string.
    2. Removes problematic inline styles (justify, word-break, etc).
    3. Enforces strict line-breaking rules on all text-bearing elements.
    """
    if not html or not isinstance(html, str):
        return ""
    style_block = """<style>
    .cms-content {
        width: 100% !important;
        max-width: 100% !important;
    }
    /* Global text settings for CMS content */
    .cms-content * {
        word-break: normal !important;
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        hyphens: none !important;
        -webkit-hyphens: none !important;
        white-space: normal !important;
        text-align: left !important;
        box-sizing: border-box !important;
    }
    /* Ensure block elements behave as blocks and handle overflow */
    .cms-content p, 
    .cms-content div, 
    .cms-content li, 
    .cms-content h1, 
    .cms-content h2, 
    .cms-content h3, 
    .cms-content h4, 
    .cms-content h5, 
    .cms-content h6 {
        display: block !important;
        max-width: 100% !important;
        width: auto !important;
    }
    .cms-content img {
        max-width: 100% !important;
        height: auto !important;
        display: block !important;
    }
    </style>"""
    html = re.sub(' style="[^"]*"', "", html, flags=re.IGNORECASE)
    generic_style = 'style="word-break: normal !important; overflow-wrap: break-word !important; text-align: left !important;"'
    for tag in ["p", "span", "li", "div", "h1", "h2", "h3", "h4", "h5", "h6"]:
        html = re.sub(f"<{tag}>", f"<{tag} {generic_style}>", html, flags=re.IGNORECASE)
        html = re.sub(
            f'<{tag} (class="[^"]*")>',
            f"<{tag} \x01 {generic_style}>",
            html,
            flags=re.IGNORECASE,
        )
    img_style = 'style="max-width: 100% !important; height: auto !important;"'
    html = re.sub("<img ", f"<img {img_style} ", html, flags=re.IGNORECASE)
    html = (
        html.replace("&nbsp;", " ")
        .replace("&#160;", " ")
        .replace("\xa0", " ")
        .replace("\u200b", "")
        .replace("\u200c", "")
        .replace("\u200d", "")
        .replace("\ufeff", "")
    )
    wrapper_start = '<div class="cms-content-wrapper" style="width: 100%; max-width: 100%; overflow-wrap: break-word; word-break: normal;">'
    wrapper_end = "</div>"
    return f"{style_block}{wrapper_start}{html}{wrapper_end}"