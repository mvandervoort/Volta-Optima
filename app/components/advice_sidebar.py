import reflex as rx


def advice_sidebar_item(text: str, url: str) -> rx.Component:
    is_active = rx.State.router.page.path == url
    return rx.el.a(
        rx.cond(
            is_active,
            rx.el.div(class_name="w-1 h-6 bg-teal-600 rounded-full mr-3"),
            rx.el.div(class_name="w-1 h-6 bg-transparent rounded-full mr-3"),
        ),
        text,
        href=url,
        class_name=rx.cond(
            is_active,
            "flex items-center px-3 py-2 text-sm font-medium text-teal-900 bg-teal-50 rounded-md mb-1",
            "flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md mb-1",
        ),
    )


def advice_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.h3(
                "ADVIESMODULES",
                class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
            ),
            rx.el.nav(
                advice_sidebar_item("Overzicht", "/advice-themes"),
                class_name="space-y-1 mb-8",
            ),
            rx.el.h3(
                "ZON & BATTERIJ",
                class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
            ),
            rx.el.nav(
                advice_sidebar_item("Dakscan - Zonnepotentieel", "/dakscan"),
                advice_sidebar_item("Zonnepanelen Calculator", "/solar"),
                advice_sidebar_item(
                    "Eenvoudige Batterij Berekening", "/advice/simple/battery"
                ),
                advice_sidebar_item("Verbeterde Thuisbatterij Berekening", "/battery"),
                advice_sidebar_item(
                    "Geavanceerde Batterij Simulatie", "/advice/advanced/battery"
                ),
                class_name="space-y-1",
            ),
            rx.el.h3(
                "WARM TAPWATER",
                class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 mt-8",
            ),
            rx.el.nav(
                advice_sidebar_item("Warmwater Calculator", "/warm-water"),
                class_name="space-y-1",
            ),
            rx.el.h3(
                "CONTRACTEN & TARIEVEN",
                class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4 mt-8",
            ),
            rx.el.nav(
                advice_sidebar_item(
                    "Vergelijk Contractsoorten", "/advice/contract-vergelijking"
                ),
                class_name="space-y-1",
            ),
            class_name="py-6 pr-6",
        ),
        class_name="hidden md:block w-64 shrink-0 border-r border-gray-200 min-h-[calc(100vh-5rem)]",
    )