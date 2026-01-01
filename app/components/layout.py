import reflex as rx
from app.components.navbar import navbar
from app.components.footer import footer
from app.components.cookie_consent import cookie_consent_banner
from app.components.feedback_widget import feedback_widget


def base_layout(content: rx.Component) -> rx.Component:
    return rx.el.div(
        navbar(),
        rx.el.main(
            content,
            class_name="flex-1 w-full bg-gray-50 flex flex-col min-w-0 overflow-x-hidden",
        ),
        feedback_widget(),
        footer(),
        cookie_consent_banner(),
        class_name="flex flex-col min-h-screen font-['Montserrat'] overflow-x-hidden w-full",
    )