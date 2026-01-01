import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.states.simple_battery_state import SimpleBatteryState
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)
from app.components.email_confirmation_modal import email_confirmation_modal


def stat_card(label: str, value: str, subtext: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-sm text-gray-500 mb-1"),
        rx.el.h4(value, class_name="text-2xl font-bold text-gray-900"),
        rx.cond(
            subtext != "",
            rx.el.p(subtext, class_name="text-xs text-emerald-600 font-medium mt-1"),
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-100 shadow-sm",
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("zap", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                SimpleBatteryState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                SimpleBatteryState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                SimpleBatteryState.intro_content["instructions"],
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
                    SimpleBatteryState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        SimpleBatteryState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        SimpleBatteryState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=SimpleBatteryState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            SimpleBatteryState.show_technical_details,
            rx.el.div(
                rx.html(
                    SimpleBatteryState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def advanced_params_section() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "sliders-horizontal", class_name="w-5 h-5 text-amber-600 mr-2"
                    ),
                    rx.el.span(
                        "Geavanceerde Parameters",
                        class_name="font-semibold text-amber-900",
                    ),
                    class_name="flex items-center",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        SimpleBatteryState.show_advanced_params,
                        "w-5 h-5 text-amber-600 transform rotate-180 transition-transform",
                        "w-5 h-5 text-amber-600 transition-transform",
                    ),
                ),
                class_name="flex items-center justify-between w-full",
            ),
            on_click=SimpleBatteryState.toggle_advanced_params,
            class_name="w-full py-3 px-4 bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-200 rounded-lg hover:from-amber-100 hover:to-orange-100 hover:border-amber-300 transition-all shadow-sm mb-4",
        ),
        rx.cond(
            SimpleBatteryState.show_advanced_params,
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Round-trip Efficiëntie (eta)",
                                class_name="text-xs font-semibold text-gray-600",
                            ),
                            info_tooltip(
                                "Round-trip efficiëntie van de batterij (hoeveel energie er verloren gaat bij laden/ontladen). Standaard ca. 90-95%."
                            ),
                            class_name="flex items-center mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            step="0.01",
                            default_value=SimpleBatteryState.eta.to_string(),
                            on_change=SimpleBatteryState.set_eta,
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Ontladingsdiepte (DoD)",
                                class_name="text-xs font-semibold text-gray-600",
                            ),
                            info_tooltip(
                                "Maximale ontladingsdiepte. Hoeveel procent van de capaciteit daadwerkelijk bruikbaar is om de levensduur te verlengen."
                            ),
                            class_name="flex items-center mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            step="0.01",
                            default_value=SimpleBatteryState.dod.to_string(),
                            on_change=SimpleBatteryState.set_dod,
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Veiligheidsfactor",
                                class_name="text-xs font-semibold text-gray-600",
                            ),
                            info_tooltip(
                                "Veiligheidsmarge bovenop het gemiddelde verbruik om ook op piekdagen voldoende capaciteit te hebben."
                            ),
                            class_name="flex items-center mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            step="0.05",
                            default_value=SimpleBatteryState.safety_factor.to_string(),
                            on_change=SimpleBatteryState.set_safety_factor,
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                        ),
                    ),
                    class_name="grid grid-cols-3 gap-4 mb-4",
                ),
                rx.el.div(class_name="h-px bg-gray-200 my-4"),
                rx.el.h4(
                    "Financiële Aannames",
                    class_name="text-sm font-bold text-gray-900 mb-3",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Elektriciteitsprijs (€/kWh)",
                                class_name="text-xs font-semibold text-gray-600",
                            ),
                            info_tooltip(
                                "Gemiddelde stroomprijs die u betaalt per kWh (inclusief belastingen)."
                            ),
                            class_name="flex items-center mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            step="0.01",
                            default_value=SimpleBatteryState.electricity_price.to_string(),
                            on_change=SimpleBatteryState.set_electricity_price,
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                        ),
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.label(
                                "Batterijkosten (€/kWh)",
                                class_name="text-xs font-semibold text-gray-600",
                            ),
                            info_tooltip(
                                "Geschatte kosten per kWh opslagcapaciteit voor het batterijsysteem (incl. installatie)."
                            ),
                            class_name="flex items-center mb-1",
                        ),
                        rx.el.input(
                            type="number",
                            step="10",
                            default_value=SimpleBatteryState.battery_cost_per_kwh.to_string(),
                            on_change=SimpleBatteryState.set_battery_cost_per_kwh,
                            class_name="w-full px-3 py-2 border border-gray-300 rounded-md text-sm",
                        ),
                    ),
                    class_name="grid grid-cols-2 gap-4 mb-2",
                ),
                class_name="animate-in fade-in slide-in-from-top-2 duration-300",
            ),
        ),
        class_name="mb-6",
    )


def simple_battery_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.title(
                "Snel Batterij Advies | Eenvoudige Capaciteit Calculator | Volta Optima"
            ),
            rx.el.meta(
                name="description",
                content="Snel inzicht in de ideale thuisbatterij voor uw situatie? Gebruik onze eenvoudige calculator voor direct advies over capaciteit en terugverdientijd.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Snelle Batterij Calculator",
                    description="Bereken eenvoudig de potentiële besparing en optimale grootte van een thuisbatterij.",
                    url="/tools/batterij-snel",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [
                        ("Home", "/"),
                        ("Tools", "/tools"),
                        ("Snelle Batterij Check", "/tools/batterij-snel"),
                    ]
                )
            ),
            advice_sidebar(),
            rx.el.div(
                rx.el.div(
                    intro_section(),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "1. Systeem Invoer",
                                class_name="text-lg font-bold text-gray-900 mb-4",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.label(
                                            "Jaarlijks Verbruik (kWh)",
                                            class_name="text-sm font-medium text-gray-700",
                                        ),
                                        info_tooltip(
                                            "Totaal elektriciteitsverbruik van uw huishouden in een jaar (kWh)."
                                        ),
                                        class_name="flex items-center mb-1",
                                    ),
                                    rx.el.input(
                                        type="number",
                                        default_value=SimpleBatteryState.annual_consumption.to_string(),
                                        on_change=SimpleBatteryState.set_annual_consumption,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.label(
                                            "Jaarlijkse Netimport (kWh)",
                                            class_name="text-sm font-medium text-gray-700",
                                        ),
                                        info_tooltip(
                                            "De hoeveelheid stroom die u daadwerkelijk van het net afneemt (dus ná direct eigen verbruik)."
                                        ),
                                        class_name="flex items-center mb-1",
                                    ),
                                    rx.el.p(
                                        "De hoeveelheid stroom die van het net wordt gekocht.",
                                        class_name="text-xs text-gray-500 mb-2",
                                    ),
                                    rx.el.input(
                                        type="number",
                                        default_value=SimpleBatteryState.annual_grid_import.to_string(),
                                        on_change=SimpleBatteryState.set_annual_grid_import,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none",
                                    ),
                                    class_name="mb-6",
                                ),
                                advanced_params_section(),
                                rx.el.button(
                                    rx.cond(
                                        SimpleBatteryState.is_processing,
                                        rx.el.div(
                                            rx.spinner(
                                                class_name="w-4 h-4 text-white mr-2"
                                            ),
                                            "Berekenen...",
                                            class_name="flex items-center justify-center",
                                        ),
                                        "Bereken Optimale Batterij",
                                    ),
                                    on_click=SimpleBatteryState.calculate_optimal_battery,
                                    disabled=SimpleBatteryState.is_processing,
                                    class_name="w-full py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg hover:shadow-emerald-200/50 disabled:opacity-70",
                                ),
                                rx.el.p(
                                    SimpleBatteryState.rate_limit_status,
                                    class_name="text-xs text-gray-500 text-center mt-2",
                                ),
                                class_name="bg-gray-50 p-6 rounded-2xl border border-gray-200 h-fit",
                            ),
                        ),
                        rx.el.div(
                            rx.cond(
                                SimpleBatteryState.has_calculated,
                                rx.el.div(
                                    rx.el.h3(
                                        "2. Berekeningsresultaten",
                                        class_name="text-lg font-bold text-gray-900 mb-4",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            rx.el.p(
                                                "Aanbevolen Capaciteit",
                                                class_name="text-sm text-emerald-100 font-medium mb-1",
                                            ),
                                            rx.el.div(
                                                rx.el.span(
                                                    SimpleBatteryState.optimal_capacity.to_string(),
                                                    class_name="text-5xl font-bold",
                                                ),
                                                rx.el.span(
                                                    "kWh",
                                                    class_name="text-xl opacity-80 ml-1",
                                                ),
                                                class_name="flex items-baseline",
                                            ),
                                            rx.el.p(
                                                "Nominale Capaciteit",
                                                class_name="text-xs text-emerald-200 mt-2 opacity-80",
                                            ),
                                            class_name="bg-emerald-600 text-white p-6 rounded-2xl shadow-lg mb-6",
                                        ),
                                        rx.el.div(
                                            stat_card(
                                                "Bruikbare Capaciteit",
                                                f"{SimpleBatteryState.usable_capacity} kWh",
                                            ),
                                            stat_card(
                                                "Gem. Dagelijkse Export",
                                                f"{SimpleBatteryState.avg_daily_export} kWh",
                                            ),
                                            stat_card(
                                                "Extra Zelfconsumptie",
                                                f"{SimpleBatteryState.extra_self_consumption} kWh/jr",
                                                f"{SimpleBatteryState.percent_offset}% Gecompenseerd",
                                            ),
                                            stat_card(
                                                "Jaarlijkse Besparing",
                                                f"€{SimpleBatteryState.annual_savings}",
                                            ),
                                            stat_card(
                                                "Terugverdientijd",
                                                f"{SimpleBatteryState.payback_period} Jaar",
                                                f"ROI: {SimpleBatteryState.roi}%",
                                            ),
                                            class_name="grid grid-cols-1 md:grid-cols-2 gap-4",
                                        ),
                                        rx.cond(
                                            SimpleBatteryState.is_authenticated,
                                            rx.el.div(
                                                rx.el.button(
                                                    rx.cond(
                                                        SimpleBatteryState.is_sending_email,
                                                        rx.spinner(
                                                            class_name="w-5 h-5 mr-2 text-white"
                                                        ),
                                                        rx.icon(
                                                            "mail",
                                                            class_name="w-5 h-5 mr-2",
                                                        ),
                                                    ),
                                                    rx.cond(
                                                        SimpleBatteryState.is_sending_email,
                                                        "Verzenden...",
                                                        "E-mail Resultaten",
                                                    ),
                                                    on_click=SimpleBatteryState.email_results,
                                                    disabled=SimpleBatteryState.is_sending_email,
                                                    class_name="w-full flex justify-center items-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg mt-6 disabled:opacity-70 disabled:cursor-not-allowed",
                                                )
                                            ),
                                        ),
                                        class_name="animate-in fade-in slide-in-from-right-4 duration-700",
                                    ),
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "bar-chart-3",
                                        class_name="w-16 h-16 text-gray-200 mx-auto mb-4",
                                    ),
                                    rx.el.p(
                                        "Voer gegevens in om de optimale grootte te bekijken",
                                        class_name="text-gray-400 font-medium",
                                    ),
                                    class_name="h-full flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-200 rounded-2xl",
                                ),
                            ),
                            class_name="h-full",
                        ),
                        class_name="grid grid-cols-1 lg:grid-cols-2 gap-12",
                    ),
                ),
                technical_details_section(),
                email_confirmation_modal(
                    SimpleBatteryState.email_sent_modal_open,
                    SimpleBatteryState.close_email_modal,
                ),
                class_name="flex-1 p-6 md:p-8",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=SimpleBatteryState.load_page_content,
        )
    )