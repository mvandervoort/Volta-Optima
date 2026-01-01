import reflex as rx
from app.states.dakscan_state import DakscanState
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)
from app.components.protected_guard import protected_guard
from app.components.email_confirmation_modal import email_confirmation_modal


def metric_card(
    label: str, value: str, subtext: str, icon: str, color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 text-{color}-600 mb-3"),
            rx.el.p(label, class_name="text-sm text-gray-500 font-medium"),
            rx.el.h3(value, class_name="text-2xl font-bold text-gray-900 mt-1"),
            rx.el.p(subtext, class_name=f"text-xs text-{color}-600 mt-1 font-medium"),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all",
    )


def segment_row(segment: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.span(segment["index"], class_name="font-medium text-gray-900"),
            class_name="px-4 py-3 text-center",
        ),
        rx.el.td(
            f"{segment['area']} m²", class_name="px-4 py-3 text-right text-gray-600"
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(f"{segment['azimuth']}°", class_name="mr-2"),
                rx.el.span(
                    segment["direction"],
                    class_name="px-2 py-0.5 bg-gray-100 rounded text-xs font-bold text-gray-600",
                ),
                class_name="flex items-center justify-end",
            ),
            class_name="px-4 py-3 text-right",
        ),
        rx.el.td(
            f"{segment['pitch']}°", class_name="px-4 py-3 text-right text-gray-600"
        ),
        class_name="border-b border-gray-50 last:border-0 hover:bg-gray-50/50 transition-colors",
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("layout-grid", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                DakscanState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                DakscanState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                DakscanState.intro_content["instructions"],
                class_name="prose prose-emerald text-gray-600 max-w-none text-left w-full",
            ),
            class_name="max-w-3xl mx-auto text-center flex flex-col items-center",
        ),
        class_name="bg-gradient-to-br from-emerald-50/80 to-teal-50/50 p-8 md:p-12 rounded-3xl border border-emerald-100 shadow-sm mb-12",
    )


def technical_details_section() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.el.div(
                    rx.icon("info", class_name="w-5 h-5 text-emerald-600"),
                    class_name="w-8 h-8 rounded-full bg-emerald-50 flex items-center justify-center mr-3",
                ),
                rx.el.span(
                    DakscanState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        DakscanState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        DakscanState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=DakscanState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            DakscanState.show_technical_details,
            rx.el.div(
                rx.html(
                    DakscanState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def roof_segments_section() -> rx.Component:
    return rx.cond(
        DakscanState.roof_segments.length() > 0,
        rx.el.div(
            rx.el.h3(
                "Gedetailleerde Daksegmenten",
                class_name="text-lg font-bold text-gray-900 mb-4",
            ),
            rx.el.div(
                rx.el.table(
                    rx.el.thead(
                        rx.el.tr(
                            rx.el.th(
                                "#",
                                class_name="px-4 py-3 text-center text-xs font-bold text-gray-500 uppercase tracking-wider w-12",
                            ),
                            rx.el.th(
                                "Oppervlakte",
                                class_name="px-4 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Oriëntatie",
                                class_name="px-4 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider",
                            ),
                            rx.el.th(
                                "Hellingshoek",
                                class_name="px-4 py-3 text-right text-xs font-bold text-gray-500 uppercase tracking-wider",
                            ),
                        ),
                        class_name="bg-gray-50 border-b border-gray-100",
                    ),
                    rx.el.tbody(rx.foreach(DakscanState.roof_segments, segment_row)),
                    class_name="w-full",
                ),
                class_name="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-6",
            ),
            rx.el.div(
                rx.icon("info", class_name="w-5 h-5 text-blue-500 mr-3 flex-shrink-0"),
                rx.el.div(
                    rx.el.p(
                        "Deze details tonen de verschillende vlakken van uw dak. U kunt de waarden voor oriëntatie (azimut) en hellingshoek gebruiken om de ",
                        rx.el.a(
                            "Zonnepanelen Calculator",
                            href="/solar",
                            class_name="text-blue-700 font-bold hover:underline",
                        ),
                        " nauwkeuriger in te vullen voor een specifiek dakdeel.",
                        class_name="text-sm text-blue-700",
                    )
                ),
                class_name="flex items-start bg-blue-50 p-4 rounded-lg border border-blue-100 mb-8",
            ),
        ),
    )


def dakscan_content() -> rx.Component:
    return rx.el.div(
        intro_section(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Uw Adres",
                        class_name="block text-sm font-medium text-gray-700 mb-2",
                    ),
                    rx.el.div(
                        rx.el.input(
                            placeholder="Straatnaam 123, Stad",
                            on_change=DakscanState.set_address,
                            class_name="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 outline-none w-full",
                            default_value=DakscanState.address,
                        ),
                        rx.el.button(
                            rx.cond(
                                DakscanState.is_loading,
                                rx.spinner(class_name="w-5 h-5 text-white"),
                                rx.el.div(
                                    rx.icon("search", class_name="w-5 h-5"),
                                    "Scan Dak",
                                    class_name="flex items-center gap-2",
                                ),
                            ),
                            on_click=DakscanState.analyze_roof,
                            disabled=DakscanState.is_loading,
                            class_name="px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors disabled:opacity-70 disabled:cursor-not-allowed min-w-[140px] flex justify-center items-center",
                        ),
                        class_name="flex flex-col md:flex-row gap-3",
                    ),
                    rx.cond(
                        DakscanState.error_message != "",
                        rx.el.div(
                            rx.icon(
                                "circle_alert", class_name="w-5 h-5 text-red-500 mr-2"
                            ),
                            DakscanState.error_message,
                            class_name="mt-4 p-4 bg-red-50 text-red-700 rounded-xl flex items-center",
                        ),
                    ),
                    class_name="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm mb-8",
                )
            ),
            rx.cond(
                DakscanState.has_results,
                rx.el.div(
                    rx.el.h2(
                        "Resultaten voor uw dak",
                        class_name="text-xl font-bold text-gray-900 mb-6",
                    ),
                    rx.el.div(
                        metric_card(
                            "Max. Aantal Panelen",
                            DakscanState.panels_count.to_string(),
                            f"Op {DakscanState.roof_area} m² dak",
                            "layout-grid",
                            "blue",
                        ),
                        metric_card(
                            "Geschatte Jaaropbrengst",
                            f"{DakscanState.annual_yield} kWh",
                            "Potentiële productie",
                            "zap",
                            "yellow",
                        ),
                        metric_card(
                            "Jaarlijkse Besparing",
                            f"€{DakscanState.annual_savings}",
                            "Bij huidig prijspeil",
                            "euro",
                            "emerald",
                        ),
                        metric_card(
                            "CO₂ Compensatie",
                            f"{DakscanState.co2_offset} kg",
                            "Per jaar",
                            "leaf",
                            "green",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8",
                    ),
                    roof_segments_section(),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Analyse Details",
                                class_name="font-bold text-gray-900 mb-4",
                            ),
                            rx.el.ul(
                                rx.el.li(
                                    rx.icon(
                                        "sun", class_name="w-4 h-4 text-orange-500 mr-2"
                                    ),
                                    rx.el.span(
                                        "Zonuren per jaar:",
                                        class_name="text-gray-600 mr-1",
                                    ),
                                    rx.el.span(
                                        f"{DakscanState.sunshine_hours}",
                                        class_name="font-medium",
                                    ),
                                    class_name="flex items-center py-2 border-b border-gray-100",
                                ),
                                rx.el.li(
                                    rx.icon(
                                        "layers",
                                        class_name="w-4 h-4 text-blue-500 mr-2",
                                    ),
                                    rx.el.span(
                                        "Daksegmenten:", class_name="text-gray-600 mr-1"
                                    ),
                                    rx.el.span(
                                        f"{DakscanState.max_arrays}",
                                        class_name="font-medium",
                                    ),
                                    class_name="flex items-center py-2 border-b border-gray-100",
                                ),
                                class_name="space-y-1",
                            ),
                            class_name="bg-gray-50 p-6 rounded-2xl",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Volgende Stappen",
                                class_name="font-bold text-gray-900 mb-4",
                            ),
                            rx.el.p(
                                "Wilt u een gedetailleerd installatieplan? Bekijk onze uitgebreide solar calculator.",
                                class_name="text-sm text-gray-600 mb-4",
                            ),
                            rx.el.a(
                                "Ga naar Solar Calculator",
                                href="/solar",
                                class_name="block text-center w-full py-2 px-4 bg-white border border-gray-300 text-gray-700 font-medium rounded-lg hover:bg-gray-50 transition-colors mb-3",
                            ),
                            rx.cond(
                                DakscanState.is_authenticated,
                                rx.el.button(
                                    rx.cond(
                                        DakscanState.is_sending_email,
                                        rx.spinner(
                                            class_name="w-5 h-5 mr-2 text-white"
                                        ),
                                        rx.icon("mail", class_name="w-5 h-5 mr-2"),
                                    ),
                                    rx.cond(
                                        DakscanState.is_sending_email,
                                        "Verzenden...",
                                        "E-mail Resultaten",
                                    ),
                                    on_click=DakscanState.email_results,
                                    disabled=DakscanState.is_sending_email,
                                    class_name="w-full flex justify-center items-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed",
                                ),
                            ),
                            class_name="bg-gray-50 p-6 rounded-2xl",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    class_name="animate-in fade-in slide-in-from-bottom-4 duration-500",
                ),
            ),
            class_name="max-w-4xl mx-auto",
        ),
        technical_details_section(),
        email_confirmation_modal(
            DakscanState.email_sent_modal_open, DakscanState.close_email_modal
        ),
        class_name="flex-1 p-6 md:p-8",
    )


def dakscan_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.title("Dakscan | Google Solar Analyse | Volta Optima"),
            rx.el.meta(
                name="description",
                content="Doe de gratis dakscan en ontdek direct het zonnepotentieel van uw woning met Google Solar technologie.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Dakscan Calculator",
                    description="Solar potentieel analyse tool gebruikmakend van Google Solar API.",
                    url="/dakscan",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [("Home", "/"), ("Tools", "/tools"), ("Dakscan", "/dakscan")]
                )
            ),
            advice_sidebar(),
            protected_guard(dakscan_content(), requires_auth=True),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=DakscanState.load_page_content,
        )
    )