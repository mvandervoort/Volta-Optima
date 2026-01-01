import reflex as rx
import os


def google_analytics_scripts() -> list[rx.Component]:
    """
    Returns a list of Google Analytics 4 (GA4) script components to be added to head_components.
    Only returns scripts if GOOGLE_ANALYTICS_ID environment variable is set.
    """
    ga_id = os.getenv("GOOGLE_ANALYTICS_ID")
    if not ga_id:
        return []
    return [
        rx.script(
            src=f"https://www.googletagmanager.com/gtag/js?id={ga_id}", async_=True
        ),
        rx.script(
            f"\n            window.dataLayer = window.dataLayer || [];\n            function gtag(){{dataLayer.push(arguments);}}\n            gtag('js', new Date());\n            gtag('config', '{ga_id}');\n            "
        ),
    ]