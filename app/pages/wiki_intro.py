import reflex as rx


def wiki_intro_page() -> rx.Component:
    return rx.el.div("Redirecting...", on_mount=rx.redirect("/kb"))