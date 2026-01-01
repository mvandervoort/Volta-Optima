import reflex as rx
import json


def json_ld(data: dict | rx.Var) -> rx.Component:
    """
    Injects JSON-LD structured data into the page.
    Accepts a dict or a Reflex Var containing the dict.
    """
    script_content = rx.cond(isinstance(data, rx.Var), data, json.dumps(data))
    return rx.el.script(script_content, type="application/ld+json")