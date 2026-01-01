import reflex as rx
from app.states.base_state import State


def footer() -> rx.Component:
    return rx.el.footer(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.img(
                                src="/customcolor_icon_transparent_background.png",
                                alt="Energie Insight Logo",
                                class_name="h-6 w-6 object-contain mr-3",
                            ),
                            rx.el.h3(
                                "Energie Insight",
                                class_name="text-lg font-bold text-amber-600",
                            ),
                            class_name="flex items-center mb-4",
                        ),
                        rx.el.p(
                            "Wij ondersteunen uw reis naar een duurzame energietoekomst met datagestuurde inzichten en expertadvies op maat voor de Nederlandse markt.",
                            class_name="text-gray-500 text-sm max-w-sm leading-relaxed",
                        ),
                    ),
                    class_name="col-span-1 md:col-span-2",
                ),
                rx.el.div(
                    rx.el.h4(
                        "Hulpmiddelen", class_name="font-semibold text-gray-900 mb-4"
                    ),
                    rx.el.ul(
                        rx.el.li(
                            rx.el.a(
                                "Adviesmodules",
                                href="/advice-themes",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Zonnepanelen Calculator",
                                href="/solar",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Verbeterde Thuisbatterij Berekening",
                                href="/battery",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        class_name="space-y-3",
                    ),
                ),
                rx.el.div(
                    rx.el.h4("Bronnen", class_name="font-semibold text-gray-900 mb-4"),
                    rx.el.ul(
                        rx.el.li(
                            rx.el.a(
                                "Kennisbank",
                                href="/kb",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Blog",
                                href="/blog",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        rx.el.li(
                            rx.el.a(
                                "Aanleiding",
                                href="/aanleiding",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        class_name="space-y-3",
                    ),
                ),
                rx.el.div(
                    rx.el.h4("Bedrijf", class_name="font-semibold text-gray-900 mb-4"),
                    rx.el.ul(
                        rx.el.li(
                            rx.el.a(
                                "Contact & Over ons",
                                href="/contact-about",
                                class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                            )
                        ),
                        class_name="space-y-3",
                    ),
                ),
                rx.cond(
                    State.is_admin,
                    rx.el.div(
                        rx.el.h4(
                            "Beheer", class_name="font-semibold text-gray-900 mb-4"
                        ),
                        rx.el.ul(
                            rx.el.li(
                                rx.el.a(
                                    "Dashboard",
                                    href="/admin",
                                    class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                                )
                            ),
                            rx.el.li(
                                rx.el.a(
                                    "CMS Berichten",
                                    href="/admin/cms",
                                    class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                                )
                            ),
                            rx.el.li(
                                rx.el.a(
                                    "Categorieën",
                                    href="/admin/categories",
                                    class_name="text-gray-500 hover:text-teal-600 text-sm transition-colors",
                                )
                            ),
                            class_name="space-y-3",
                        ),
                    ),
                    rx.el.div(),
                ),
                class_name=rx.cond(
                    State.is_admin,
                    "grid grid-cols-1 md:grid-cols-6 gap-8 mb-12",
                    "grid grid-cols-1 md:grid-cols-5 gap-8 mb-12",
                ),
            ),
            rx.el.div(
                rx.el.p(
                    "© 2026 Energie Insight. Alle rechten voorbehouden.",
                    class_name="text-sm text-gray-400",
                ),
                rx.el.div(
                    rx.el.a(
                        "Privacybeleid",
                        href="/privacybeleid",
                        class_name="text-sm text-gray-400 hover:text-teal-600 transition-colors",
                    ),
                    rx.el.a(
                        "Algemene voorwaarden",
                        href="/algemene-voorwaarden",
                        class_name="text-sm text-gray-400 hover:text-teal-600 transition-colors",
                    ),
                    class_name="flex gap-6 mt-4 md:mt-0",
                ),
                class_name="flex flex-col md:flex-row justify-between items-center border-t border-gray-200 pt-8",
            ),
            class_name="container mx-auto px-4 py-12",
        ),
        class_name="bg-white border-t border-gray-100 mt-auto",
    )