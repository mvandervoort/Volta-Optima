import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar


def advice_theme_solar_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            advice_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "sun",
                        class_name="w-12 h-12 text-yellow-500 mb-4 animate-spin-slow",
                    ),
                    rx.el.h1(
                        "Zonne-energie Advies",
                        class_name="text-3xl font-bold text-gray-900 mb-4",
                    ),
                    rx.el.p(
                        "Optimaliseer uw zonne-energie installatie en rendement.",
                        class_name="text-xl text-gray-600 mb-8",
                    ),
                    class_name="mb-12",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.el.div(
                            rx.el.h3(
                                "Opbrengst Calculator",
                                class_name="text-xl font-bold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                "Bereken de verwachte opbrengst van uw zonnepanelen op basis van locatie en oriëntatie.",
                                class_name="text-gray-600 mb-4",
                            ),
                            rx.el.span(
                                "Start Calculator →",
                                class_name="text-emerald-600 font-bold",
                            ),
                            class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all h-full",
                        ),
                        href="/solar",
                    ),
                    rx.el.a(
                        rx.el.div(
                            rx.el.h3(
                                "Installatie Tips",
                                class_name="text-xl font-bold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                "Waar moet u op letten bij het installeren van zonnepanelen? Lees onze tips.",
                                class_name="text-gray-600 mb-4",
                            ),
                            rx.el.span(
                                "Lees Meer →", class_name="text-emerald-600 font-bold"
                            ),
                            class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all h-full",
                        ),
                        href="/kb",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-8",
                ),
                class_name="flex-1 p-6 md:p-8",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
        )
    )