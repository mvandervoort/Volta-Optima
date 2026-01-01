import reflex as rx
from app.states.solar_state import SolarState
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)
from app.components.email_confirmation_modal import email_confirmation_modal


def form_label(text: str, tooltip: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.label(text, class_name="text-sm font-semibold text-gray-700"),
        rx.cond(tooltip != "", info_tooltip(tooltip)),
        class_name="flex items-center mb-1",
    )


def input_field(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    type_: str = "text",
    placeholder: str = "",
    tooltip: str = "",
) -> rx.Component:
    return rx.el.div(
        form_label(label, tooltip),
        rx.el.div(
            rx.el.input(
                on_change=on_change,
                type=type_,
                placeholder=placeholder,
                class_name="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all bg-gray-50 focus:bg-white text-gray-900 shadow-sm placeholder:text-gray-400",
                default_value=value,
            ),
            class_name="relative group",
        ),
        class_name="w-full",
    )


def select_field(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    options: list[tuple[str, str]],
    tooltip: str = "",
) -> rx.Component:
    return rx.el.div(
        form_label(label, tooltip),
        rx.el.div(
            rx.el.select(
                rx.foreach(options, lambda opt: rx.el.option(opt[0], value=opt[1])),
                value=value,
                on_change=on_change,
                class_name="w-full px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all bg-gray-50 focus:bg-white appearance-none text-gray-900 shadow-sm",
            ),
            rx.icon(
                "chevron-down",
                class_name="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none",
            ),
            class_name="relative",
        ),
        class_name="w-full",
    )


def slider_field(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    min_: int,
    max_: int,
    helper: str,
    tooltip: str = "",
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            form_label(label, tooltip),
            rx.el.span(
                value,
                class_name="text-sm font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-md",
            ),
            class_name="flex justify-between items-center mb-2",
        ),
        rx.el.input(
            type="range",
            min=min_,
            max=max_,
            default_value=value,
            key=value.to_string(),
            on_change=on_change.throttle(100),
            class_name="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-emerald-600",
        ),
        rx.el.p(helper, class_name="text-xs text-gray-500 mt-2"),
        class_name="w-full p-4 bg-gray-50 rounded-xl border border-gray-100",
    )


def result_card(
    title: str, value: str, unit: str, icon_name: str, color: str
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon_name, class_name=f"w-6 h-6 text-{color}-600"),
                class_name=f"w-12 h-12 rounded-xl bg-{color}-100 flex items-center justify-center mb-4",
            ),
            rx.el.p(
                title,
                class_name="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1",
            ),
            rx.el.div(
                rx.el.span(
                    value, class_name="text-2xl md:text-3xl font-bold text-gray-900"
                ),
                rx.el.span(unit, class_name="text-sm text-gray-400 ml-1 font-medium"),
                class_name="flex items-baseline",
            ),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all hover:-translate-y-1 duration-300",
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("sun", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                SolarState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                SolarState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                SolarState.intro_content["instructions"],
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
                    SolarState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        SolarState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        SolarState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=SolarState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            SolarState.show_technical_details,
            rx.el.div(
                rx.html(
                    SolarState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def solar_yield_content() -> rx.Component:
    return rx.el.div(
        intro_section(),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Systeemconfiguratie",
                    class_name="text-xl font-bold text-gray-800 mb-6 border-b pb-2",
                ),
                rx.el.div(
                    input_field(
                        "Locatie (Stad, Provincie of Adres)",
                        SolarState.address,
                        SolarState.set_address,
                        placeholder="bv. Amsterdam, NH",
                        tooltip="De plaats waar de zonnepanelen worden geïnstalleerd. Dit bepaalt de zonne-instraling.",
                    ),
                    class_name="mb-6",
                ),
                rx.el.div(
                    input_field(
                        "Systeemcapaciteit (kW)",
                        SolarState.system_capacity.to_string(),
                        SolarState.set_system_capacity,
                        type_="number",
                        tooltip="Het totale vermogen van uw zonnepanelensysteem in kilowattpiek (kWp).",
                    ),
                    input_field(
                        "Systeemverliezen (%)",
                        SolarState.losses.to_string(),
                        SolarState.set_losses,
                        type_="number",
                        tooltip="Verliezen door bekabeling, omvormer, schaduw, vuil, etc. Standaard is 14%.",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6",
                ),
                rx.el.div(
                    select_field(
                        "Type Paneel",
                        SolarState.module_type.to_string(),
                        SolarState.set_module_type_int,
                        [
                            ("Standaard (15% efficiëntie)", "0"),
                            ("Premium (19% efficiëntie)", "1"),
                            ("Dunne Film (10% efficiëntie)", "2"),
                        ],
                        tooltip="Het type zonneceltechnologie. Standaard panelen zijn het meest gebruikelijk.",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6",
                ),
                rx.el.div(
                    slider_field(
                        "Hellingshoek (graden)",
                        SolarState.tilt,
                        SolarState.set_tilt,
                        0,
                        90,
                        "Hoek van de panelen t.o.v. horizontaal (0 = plat).",
                        tooltip="De hoek van de panelen ten opzichte van de grond. 0° is plat, 90° is verticaal.",
                    ),
                    slider_field(
                        "Oriëntatie (graden) (Azimut)",
                        SolarState.azimuth,
                        SolarState.set_azimuth,
                        0,
                        360,
                        "Kompasrichting (180 = Zuiden).",
                        tooltip="De kompasrichting. 180° is Zuid, 90° is Oost, 270° is West.",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8",
                ),
                rx.cond(
                    SolarState.error_message != "",
                    rx.el.div(
                        rx.icon("badge_alert", class_name="w-5 h-5 mr-2"),
                        SolarState.error_message,
                        class_name="bg-red-50 text-red-600 p-4 rounded-lg flex items-center mb-6 border border-red-100",
                    ),
                ),
                rx.el.button(
                    rx.cond(
                        SolarState.is_loading,
                        rx.el.div(
                            rx.spinner(size="2", class_name="text-white mr-2"),
                            "Verwerken...",
                            class_name="flex items-center gap-2",
                        ),
                        rx.el.div(
                            rx.icon("calculator", class_name="w-5 h-5 mr-2"),
                            "Bereken Opbrengst",
                            class_name="flex items-center",
                        ),
                    ),
                    on_click=SolarState.calculate_yield,
                    disabled=SolarState.is_loading,
                    class_name="w-full md:w-auto px-8 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold rounded-xl shadow-lg hover:shadow-emerald-200 hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex justify-center mx-auto min-w-[200px]",
                ),
                class_name="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100",
            ),
            class_name="w-full max-w-5xl mx-auto animate-in fade-in duration-1000",
        ),
        rx.cond(
            SolarState.has_results,
            rx.el.div(
                rx.el.div(
                    rx.icon("map-pin", class_name="w-4 h-4 text-emerald-600 mr-2"),
                    rx.el.span(
                        "Gevonden Locatie: ",
                        class_name="text-sm text-gray-500 font-medium mr-1",
                    ),
                    rx.el.span(
                        f"{SolarState.lat}, {SolarState.lon}",
                        class_name="text-sm text-gray-900 font-semibold",
                    ),
                    class_name="flex items-center justify-center bg-gray-50 py-2 px-4 rounded-lg mx-auto w-fit mb-8 border border-gray-100",
                ),
                rx.el.h2(
                    "Jaarlijkse Resultaten",
                    class_name="text-2xl font-bold text-gray-800 mb-6 text-center mt-12",
                ),
                rx.el.div(
                    result_card(
                        "Energieopbrengst",
                        SolarState.ac_annual.to_string(),
                        "kWh/jr",
                        "zap",
                        "yellow",
                    ),
                    result_card(
                        "Geschatte Besparing",
                        f"€{SolarState.value_saved.to_string()}",
                        "/jr",
                        "dollar-sign",
                        "emerald",
                    ),
                    result_card(
                        "CO₂ Compensatie",
                        SolarState.co2_offset.to_string(),
                        "kg",
                        "leaf",
                        "green",
                    ),
                    result_card(
                        "Zonnestraling",
                        SolarState.solrad_annual.to_string(),
                        "kWh/m²/dag",
                        "sun",
                        "orange",
                    ),
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 w-full max-w-6xl mx-auto",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Reële Prijsanalyse 2024",
                                class_name="text-xl font-bold text-gray-900 mb-4",
                            ),
                            rx.el.p(
                                "Berekeningen gebaseerd op werkelijke 8.760 uurprijzen van Vattenfall (2024).",
                                class_name="text-sm text-gray-500 mb-6",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.p(
                                        "Gem. Prijs Gebruikt",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    rx.el.p(
                                        f"€{SolarState.avg_price}/kWh",
                                        class_name="text-lg font-bold text-gray-900",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Geschatte Systeemkosten",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    rx.el.p(
                                        f"€{SolarState.system_cost}",
                                        class_name="text-lg font-bold text-gray-900",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Terugverdientijd",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    rx.el.p(
                                        f"{SolarState.payback_period} Jaar",
                                        class_name="text-lg font-bold text-emerald-600",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.p(
                                        "Maandelijkse Besparing",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    rx.el.p(
                                        f"€{SolarState.monthly_savings}/mnd",
                                        class_name="text-lg font-bold text-emerald-600",
                                    ),
                                ),
                                class_name="grid grid-cols-2 gap-4",
                            ),
                            class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Besparingsoverzicht",
                                class_name="text-xl font-bold text-gray-900 mb-4",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.span(
                                            "Direct Verbruik (30%)",
                                            class_name="text-sm text-gray-600",
                                        ),
                                        rx.el.span(
                                            f"€{SolarState.savings_breakdown['self_consumption_euros']}",
                                            class_name="font-bold text-emerald-600",
                                        ),
                                        class_name="flex justify-between mb-2",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="bg-emerald-500 h-2 rounded-full",
                                            style={"width": "30%"},
                                        ),
                                        class_name="w-full bg-gray-100 rounded-full h-2 mb-4",
                                    ),
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.span(
                                            "Teruglevering (70%)",
                                            class_name="text-sm text-gray-600",
                                        ),
                                        rx.el.span(
                                            f"€{SolarState.savings_breakdown['export_euros']}",
                                            class_name="font-bold text-blue-600",
                                        ),
                                        class_name="flex justify-between mb-2",
                                    ),
                                    rx.el.div(
                                        rx.el.div(
                                            class_name="bg-blue-500 h-2 rounded-full",
                                            style={"width": "70%"},
                                        ),
                                        class_name="w-full bg-gray-100 rounded-full h-2 mb-4",
                                    ),
                                ),
                                rx.el.p(
                                    "Direct verbruik wordt gewaardeerd tegen de volledige dynamische prijs (€0,38/kWh), terwijl overtollige teruglevering een lager tarief oplevert (€0,08/kWh).",
                                    class_name="text-xs text-gray-500 mt-4 leading-relaxed",
                                ),
                            ),
                            class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Prijsopbouw (2024)",
                                class_name="text-xl font-bold text-gray-900 mb-4",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    SolarState.price_components,
                                    lambda item: rx.el.div(
                                        rx.el.span(
                                            item[0], class_name="text-sm text-gray-600"
                                        ),
                                        rx.el.span(
                                            f"€{item[1]}",
                                            class_name="text-sm font-medium text-gray-900",
                                        ),
                                        class_name="flex justify-between py-2 border-b border-gray-50 last:border-0",
                                    ),
                                ),
                                class_name="space-y-1",
                            ),
                            class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-6xl mx-auto mt-6",
                    )
                ),
                rx.el.div(
                    rx.el.button(
                        rx.icon("download", class_name="w-5 h-5 mr-2"),
                        "Download Jaarcijfers (CSV)",
                        on_click=SolarState.download_solar_data,
                        class_name="flex items-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg",
                    ),
                    rx.cond(
                        SolarState.is_authenticated,
                        rx.el.button(
                            rx.cond(
                                SolarState.is_sending_email,
                                rx.spinner(class_name="w-5 h-5 mr-2 text-emerald-700"),
                                rx.icon("mail", class_name="w-5 h-5 mr-2"),
                            ),
                            rx.cond(
                                SolarState.is_sending_email,
                                "Verzenden...",
                                "E-mail Resultaten",
                            ),
                            on_click=SolarState.email_results,
                            disabled=SolarState.is_sending_email,
                            class_name="flex items-center px-6 py-3 bg-white text-emerald-700 border border-emerald-200 font-bold rounded-xl hover:bg-emerald-50 transition-colors shadow-md hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed",
                        ),
                    ),
                    class_name="flex flex-col md:flex-row justify-center w-full gap-4 mt-8",
                ),
                class_name="animate-in fade-in slide-in-from-bottom-4 duration-700 w-full mb-12",
            ),
        ),
        technical_details_section(),
        class_name="w-full flex flex-col items-center",
    )


def solar_yield_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.title(
                "Zonnepanelen Opbrengst Calculator | PVWatts Analyse | Volta Optima"
            ),
            rx.el.meta(
                name="description",
                content="Bereken nauwkeurig de opbrengst van uw zonnepanelen met onze PVWatts integratie. Analyseer locatie, hellingshoek en oriëntatie voor optimaal rendement.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Zonnepanelen Opbrengst Calculator",
                    description="Bereken de energieopbrengst van zonnepanelen op basis van locatie en specificaties.",
                    url="/tools/solar-yield",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [
                        ("Home", "/"),
                        ("Tools", "/tools"),
                        ("Solar Opbrengst", "/tools/solar-yield"),
                    ]
                )
            ),
            advice_sidebar(),
            rx.el.div(
                solar_yield_content(),
                email_confirmation_modal(
                    SolarState.email_sent_modal_open, SolarState.close_email_modal
                ),
                class_name="flex-1 p-6 md:p-8",
                on_mount=SolarState.load_page_content,
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
        )
    )