import reflex as rx
from app.states.base_state import State
from app.states.mobile_menu_state import MobileMenuState


def navbar_link(text: str, url: str, icon: str) -> rx.Component:
    is_active = State.router.page.path == url
    active_classes = (
        "flex items-center text-teal-600 font-bold border-b-2 border-teal-600 px-1 py-1"
    )
    inactive_classes = "flex items-center text-gray-600 hover:text-teal-600 font-medium transition-colors hover:scale-105 transform duration-200 px-1 py-1 border-b-2 border-transparent"
    active_icon_class = "h-4 w-4 mr-2 text-teal-600"
    inactive_icon_class = (
        "h-4 w-4 mr-2 text-gray-400 group-hover:text-teal-600 transition-colors"
    )
    return rx.el.a(
        rx.icon(
            icon, class_name=rx.cond(is_active, active_icon_class, inactive_icon_class)
        ),
        rx.el.span(text),
        href=url,
        class_name=rx.cond(is_active, active_classes, inactive_classes) + " group",
    )


def mobile_nav_link(text: str, url: str, icon: str) -> rx.Component:
    is_active = State.router.page.path == url
    return rx.el.a(
        rx.icon(
            icon,
            class_name=rx.cond(
                is_active, "w-5 h-5 text-teal-600 mr-3", "w-5 h-5 text-gray-400 mr-3"
            ),
        ),
        rx.el.span(
            text,
            class_name=rx.cond(
                is_active, "font-bold text-teal-600", "font-medium text-gray-700"
            ),
        ),
        href=url,
        on_click=MobileMenuState.close,
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-3 bg-teal-50 rounded-lg transition-colors mb-1 w-full",
            "flex items-center px-4 py-3 hover:bg-gray-50 rounded-lg transition-colors mb-1 w-full",
        ),
    )


def mobile_menu() -> rx.Component:
    return rx.drawer.root(
        rx.drawer.trigger(
            rx.el.button(
                rx.icon("menu", class_name="w-6 h-6 text-gray-700"),
                class_name="p-2 hover:bg-gray-100 rounded-lg transition-colors xl:hidden flex items-center",
            )
        ),
        rx.drawer.portal(
            rx.drawer.overlay(class_name="fixed inset-0 bg-black/60 z-50"),
            rx.drawer.content(
                rx.el.div(
                    rx.el.div(
                        rx.el.span(
                            "Menu", class_name="text-lg font-bold text-gray-900"
                        ),
                        rx.drawer.close(
                            rx.el.button(
                                rx.icon("x", class_name="w-6 h-6 text-gray-500"),
                                class_name="p-2 hover:bg-gray-100 rounded-full transition-colors",
                            )
                        ),
                        class_name="flex items-center justify-between p-5 border-b border-gray-100 shrink-0 bg-white",
                    ),
                    rx.el.div(
                        mobile_nav_link("Startpagina", "/", "home"),
                        mobile_nav_link("Aanleiding", "/aanleiding", "info"),
                        mobile_nav_link("Adviesmodules", "/advice-themes", "lightbulb"),
                        mobile_nav_link("Kennisbank", "/kb", "book-open"),
                        mobile_nav_link("Blog", "/blog", "newspaper"),
                        rx.cond(
                            State.is_authenticated,
                            mobile_nav_link("Mijn Resultaten", "/results", "bar-chart"),
                        ),
                        mobile_nav_link("Contact & Over ons", "/contact-about", "mail"),
                        class_name="flex flex-col p-4 gap-1 flex-1 overflow-y-auto bg-white min-h-0",
                    ),
                    rx.el.div(
                        rx.cond(
                            State.is_authenticated,
                            rx.el.button(
                                rx.icon("log-out", class_name="w-5 h-5 mr-3"),
                                "Uitloggen",
                                on_click=[State.logout, MobileMenuState.close],
                                class_name="flex items-center w-full px-4 py-3 text-red-600 hover:bg-red-50 rounded-lg transition-colors font-medium border border-red-100",
                            ),
                            rx.el.div(
                                rx.el.a(
                                    "Inloggen",
                                    href="/login",
                                    on_click=MobileMenuState.close,
                                    class_name="block w-full text-center py-3 px-4 border border-gray-200 rounded-lg text-gray-700 font-medium hover:bg-gray-50 mb-3 transition-colors bg-white",
                                ),
                                rx.el.a(
                                    "Registreren",
                                    href="/signup",
                                    on_click=MobileMenuState.close,
                                    class_name="block w-full text-center py-3 px-4 bg-teal-600 text-white rounded-lg font-bold hover:bg-teal-700 shadow-md transition-colors",
                                ),
                                class_name="flex flex-col w-full",
                            ),
                        ),
                        class_name="p-5 border-t border-gray-100 mt-auto bg-gray-50 shrink-0",
                    ),
                    class_name="flex flex-col h-full bg-white w-full",
                ),
                class_name="fixed top-0 right-0 z-50 h-full w-80 max-w-[85vw] bg-white shadow-2xl flex flex-col focus:outline-none",
            ),
        ),
        direction="right",
        key=MobileMenuState.menu_key.to_string(),
    )


def navbar() -> rx.Component:
    return rx.el.nav(
        rx.el.div(
            rx.el.a(
                rx.el.div(
                    rx.el.img(
                        src="/customcolor_icon_transparent_background.png",
                        alt="Energie Insight Logo",
                        class_name="h-10 w-10 object-contain p-1",
                    ),
                    class_name="h-10 w-10 bg-gray-100 rounded-lg flex items-center justify-center shadow-sm hover:shadow-md transition-all duration-300",
                ),
                rx.el.span(
                    "Energie Insight",
                    class_name="text-xl font-bold text-amber-600 ml-3 tracking-tight",
                ),
                href="/",
                class_name="flex items-center hover:opacity-90 transition-opacity group",
            ),
            rx.el.div(
                navbar_link("Startpagina", "/", "home"),
                navbar_link("Aanleiding", "/aanleiding", "info"),
                navbar_link("Adviesmodules", "/advice-themes", "lightbulb"),
                navbar_link("Kennisbank", "/kb", "book-open"),
                navbar_link("Blog", "/blog", "newspaper"),
                rx.cond(
                    State.is_authenticated,
                    navbar_link("Mijn Resultaten", "/results", "bar-chart"),
                ),
                navbar_link("Contact & Over ons", "/contact-about", "mail"),
                class_name="hidden xl:flex items-center gap-6",
            ),
            rx.el.div(
                rx.cond(
                    State.is_authenticated,
                    rx.el.div(
                        rx.cond(
                            State.is_admin,
                            rx.el.a(
                                "Admin",
                                href="/admin",
                                class_name="text-sm font-medium text-emerald-600 hover:text-emerald-700 transition-colors px-3 py-2 rounded-lg hover:bg-emerald-50 mr-2",
                            ),
                        ),
                        rx.el.button(
                            "Uitloggen",
                            on_click=State.logout,
                            class_name="text-sm font-medium text-gray-600 hover:text-red-600 transition-colors px-3 py-2 rounded-lg hover:bg-red-50",
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "Inloggen",
                            href="/login",
                            class_name="px-5 py-2.5 text-gray-700 hover:text-teal-600 font-medium text-sm transition-colors",
                        ),
                        rx.el.a(
                            "Registreren",
                            href="/signup",
                            class_name="px-5 py-2.5 bg-teal-500 text-white rounded-md hover:bg-teal-600 transition-all text-sm font-semibold shadow-sm hover:shadow-md ml-2",
                        ),
                        class_name="flex items-center",
                    ),
                ),
                class_name="hidden xl:flex items-center gap-2",
            ),
            rx.el.div(mobile_menu(), class_name="xl:hidden flex items-center"),
            class_name="container mx-auto px-4 h-20 flex items-center justify-between",
        ),
        class_name="border-b border-gray-100 bg-white/80 backdrop-blur-md sticky top-0 z-50",
    )