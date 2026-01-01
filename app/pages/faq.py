import reflex as rx


def faq_page() -> rx.Component:
    return rx.el.div("Redirecting...", on_mount=rx.redirect("/aanleiding#faq"))