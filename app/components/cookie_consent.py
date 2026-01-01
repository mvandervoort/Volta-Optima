import reflex as rx
from app.states.cookie_consent_state import CookieConsentState


def cookie_consent_banner() -> rx.Component:
    return rx.cond(
        CookieConsentState.is_visible,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.p(
                        "Wij gebruiken cookies voor Google Analytics om onze website te verbeteren.",
                        class_name="text-sm text-gray-700",
                    ),
                    class_name="flex-1 mr-4",
                ),
                rx.el.div(
                    rx.el.button(
                        "Afwijzen",
                        on_click=CookieConsentState.reject_cookies,
                        class_name="whitespace-nowrap px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-medium rounded-lg transition-colors mr-2",
                    ),
                    rx.el.button(
                        "Accepteren",
                        on_click=CookieConsentState.accept_cookies,
                        class_name="whitespace-nowrap px-4 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-medium rounded-lg transition-colors shadow-sm",
                    ),
                    class_name="flex items-center",
                ),
                class_name="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between flex-row",
            ),
            class_name="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-[0_-4px_6px_-1px_rgba(0,0,0,0.05)] z-[100] animate-in slide-in-from-bottom-full duration-500",
        ),
    )