import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.states.battery_estimator_state import BatteryEstimatorState
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)
from app.components.email_confirmation_modal import email_confirmation_modal


def upload_zone(
    text: str,
    upload_id: str,
    handler: rx.EventHandler,
    status: rx.Var,
    profile_loaded: rx.Var,
    subtext: str = "CSV (365 dagen, kolom 'opbrengst_kwh')",
) -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud-upload", class_name="w-10 h-10 text-emerald-500 mb-3"),
                rx.el.div(
                    rx.el.span(
                        text, class_name="text-sm font-medium text-gray-700 text-center"
                    ),
                    info_tooltip(
                        "Upload een CSV-bestand met kolommen voor datum/tijd en opwekking/verbruik in kWh. Zorg voor data van een volledig jaar."
                    ),
                    class_name="flex items-center justify-center",
                ),
                rx.el.p(subtext, class_name="text-xs text-gray-500 mt-1"),
                class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-emerald-100 rounded-xl bg-emerald-50/50 hover:bg-emerald-50 transition-colors cursor-pointer w-full",
            ),
            id=upload_id,
            accept={"text/csv": [".csv"], "application/vnd.ms-excel": [".csv"]},
            max_files=1,
            class_name="w-full mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.cond(
                    profile_loaded.length() > 0,
                    rx.icon("check_check", class_name="w-4 h-4 text-emerald-600"),
                    rx.icon("badge_alert", class_name="w-4 h-4 text-gray-400"),
                ),
                rx.el.span(status, class_name="text-xs text-gray-600 font-medium"),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.el.button(
                "Verwerk Bestand",
                on_click=handler(rx.upload_files(upload_id=upload_id)),
                class_name="w-full py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 hover:text-emerald-600 transition-colors",
            ),
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
    )


def result_metric(label: str, value: str, subtext: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="text-sm text-gray-500 mb-1"),
        rx.el.h4(value, class_name="text-2xl font-bold text-gray-900"),
        rx.cond(
            subtext != "",
            rx.el.p(subtext, class_name="text-xs text-emerald-600 font-medium mt-1"),
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-100",
    )


def optimization_charts() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Optimalisatie Resultaten",
            class_name="text-sm font-bold text-gray-900 mb-4",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "Zelfvoorzieningsgraad vs Capaciteit",
                    class_name="text-xs text-gray-500 mb-2",
                ),
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.x_axis(
                        data_key="capacity", unit=" kWh", tick={"fontSize": 11}
                    ),
                    rx.recharts.y_axis(unit="%", tick={"fontSize": 11}),
                    rx.recharts.line(
                        data_key="zelfvoorziening",
                        stroke="#10B981",
                        stroke_width=2,
                        dot=True,
                        name="Zelfvoorziening",
                    ),
                    data=BatteryEstimatorState.comparison_chart_data,
                    width="100%",
                    height=200,
                ),
                class_name="mb-6",
            ),
            rx.el.div(
                rx.el.p(
                    "Grid Interactie vs Capaciteit",
                    class_name="text-xs text-gray-500 mb-2",
                ),
                rx.recharts.line_chart(
                    rx.recharts.cartesian_grid(stroke_dasharray="3 3", vertical=False),
                    rx.recharts.graphing_tooltip(),
                    rx.recharts.x_axis(
                        data_key="capacity", unit=" kWh", tick={"fontSize": 11}
                    ),
                    rx.recharts.y_axis(tick={"fontSize": 11}),
                    rx.recharts.line(
                        data_key="inkoop",
                        stroke="#EF4444",
                        stroke_width=2,
                        dot=False,
                        name="Inkoop (kWh)",
                    ),
                    rx.recharts.line(
                        data_key="teruglevering",
                        stroke="#3B82F6",
                        stroke_width=2,
                        dot=False,
                        name="Teruglevering (kWh)",
                    ),
                    data=BatteryEstimatorState.comparison_chart_data,
                    width="100%",
                    height=200,
                ),
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 mt-6",
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("battery-charging", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                BatteryEstimatorState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                BatteryEstimatorState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                BatteryEstimatorState.intro_content["instructions"],
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
                    BatteryEstimatorState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        BatteryEstimatorState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        BatteryEstimatorState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=BatteryEstimatorState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            BatteryEstimatorState.show_technical_details,
            rx.el.div(
                rx.html(
                    BatteryEstimatorState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def battery_estimator_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.title(
                "Thuisbatterij Capaciteit Berekenen | Uitgebreide Simulatie | Volta Optima"
            ),
            rx.el.meta(
                name="description",
                content="Bereken de optimale capaciteit voor uw thuisbatterij met onze geavanceerde simulatie op basis van uw jaarverbruik en zonnepaneel opbrengst.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Thuisbatterij Simulator",
                    description="Bereken de optimale capaciteit voor uw thuisbatterij op basis van uw verbruik en zonnepaneel opbrengst.",
                    url="/tools/batterij-estimator",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [
                        ("Home", "/"),
                        ("Tools", "/tools"),
                        ("Batterij Simulator", "/tools/batterij-estimator"),
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
                                "1. Verbruik & Productie",
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
                                            "Uw totale stroomverbruik per jaar in kWh, zoals vermeld op uw energierekening of jaaroverzicht."
                                        ),
                                        class_name="flex items-center mb-1",
                                    ),
                                    rx.el.input(
                                        type="number",
                                        default_value=BatteryEstimatorState.jaar_verbruik.to_string(),
                                        on_change=BatteryEstimatorState.set_jaar_verbruik,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none",
                                    ),
                                    class_name="mb-4",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.label(
                                            "Jaarlijkse Teruglevering (kWh)",
                                            class_name="text-sm font-medium text-gray-700",
                                        ),
                                        info_tooltip(
                                            "De totale hoeveelheid zonnestroom die u per jaar teruglevert aan het net (uw overschot na direct eigen verbruik)."
                                        ),
                                        class_name="flex items-center mb-1",
                                    ),
                                    rx.el.p(
                                        "Totaal jaarlijks teruggeleverd aan het net (zonder batterij).",
                                        class_name="text-xs text-gray-500 mb-2",
                                    ),
                                    rx.el.input(
                                        type="number",
                                        default_value=BatteryEstimatorState.jaar_teruglevering.to_string(),
                                        on_change=BatteryEstimatorState.set_jaar_teruglevering,
                                        class_name="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none",
                                    ),
                                    class_name="mb-6",
                                ),
                                rx.el.h4(
                                    "Zonne-opbrengst Profiel",
                                    class_name="text-sm font-bold text-gray-900 mb-3",
                                ),
                                rx.el.div(
                                    upload_zone(
                                        "Upload Zonne-CSV",
                                        "prod_upload",
                                        BatteryEstimatorState.handle_production_upload,
                                        BatteryEstimatorState.production_data_status,
                                        BatteryEstimatorState.production_profile,
                                        "CSV met kolom 'opbrengst_kwh'",
                                    ),
                                    class_name="mb-6",
                                ),
                                rx.el.button(
                                    rx.cond(
                                        BatteryEstimatorState.is_processing,
                                        rx.el.span(
                                            "Verwerken...",
                                            class_name="flex items-center gap-2",
                                        ),
                                        "Bereken Optimale Batterij",
                                    ),
                                    on_click=BatteryEstimatorState.calculate_results,
                                    disabled=BatteryEstimatorState.is_processing,
                                    class_name="w-full py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg hover:shadow-emerald-200/50 disabled:opacity-70",
                                ),
                                rx.el.p(
                                    BatteryEstimatorState.rate_limit_status,
                                    class_name="text-xs text-gray-500 text-center mt-2",
                                ),
                                rx.cond(
                                    BatteryEstimatorState.error_message != "",
                                    rx.el.p(
                                        BatteryEstimatorState.error_message,
                                        class_name="text-sm text-red-500 mt-2 text-center",
                                    ),
                                ),
                                class_name="bg-gray-50 p-6 rounded-2xl border border-gray-200",
                            ),
                            class_name="flex flex-col",
                        ),
                        rx.cond(
                            BatteryEstimatorState.has_calculated,
                            rx.el.div(
                                rx.el.h3(
                                    "2. Analyseresultaten",
                                    class_name="text-lg font-bold text-gray-900 mb-4",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.el.p(
                                            "Optimale Capaciteit",
                                            class_name="text-sm text-emerald-100 font-medium mb-1",
                                        ),
                                        rx.el.div(
                                            rx.el.span(
                                                BatteryEstimatorState.optimal_capacity.to_string(),
                                                class_name="text-5xl font-bold",
                                            ),
                                            rx.el.span(
                                                "kWh",
                                                class_name="text-xl opacity-80 ml-1",
                                            ),
                                            class_name="flex items-baseline",
                                        ),
                                        rx.el.p(
                                            "Voor maximale zelfvoorziening",
                                            class_name="text-xs text-emerald-200 mt-2 opacity-80",
                                        ),
                                        class_name="bg-emerald-600 text-white p-6 rounded-2xl shadow-lg mb-6",
                                    ),
                                    rx.el.div(
                                        result_metric(
                                            "Zelfvoorzieningsgraad",
                                            f"{BatteryEstimatorState.zelfvoorzieningsgraad}%",
                                        ),
                                        result_metric(
                                            "Grid Inkoop",
                                            f"{BatteryEstimatorState.grid_inkoop_totaal} kWh",
                                            "/ jaar",
                                        ),
                                        result_metric(
                                            "Grid Teruglevering",
                                            f"{BatteryEstimatorState.grid_teruglevering_totaal} kWh",
                                            "/ jaar",
                                        ),
                                        result_metric(
                                            "Batterij Cycli",
                                            f"{BatteryEstimatorState.battery_cycli}",
                                            f"Levensduur: {BatteryEstimatorState.levensduur_jaren} jr",
                                        ),
                                        class_name="grid grid-cols-2 gap-4 mb-6",
                                    ),
                                    optimization_charts(),
                                    rx.cond(
                                        BatteryEstimatorState.is_authenticated,
                                        rx.el.div(
                                            rx.el.button(
                                                rx.cond(
                                                    BatteryEstimatorState.is_sending_email,
                                                    rx.spinner(
                                                        class_name="w-5 h-5 mr-2 text-white"
                                                    ),
                                                    rx.icon(
                                                        "mail",
                                                        class_name="w-5 h-5 mr-2",
                                                    ),
                                                ),
                                                rx.cond(
                                                    BatteryEstimatorState.is_sending_email,
                                                    "Verzenden...",
                                                    "E-mail Resultaten",
                                                ),
                                                on_click=BatteryEstimatorState.email_results,
                                                disabled=BatteryEstimatorState.is_sending_email,
                                                class_name="w-full flex items-center justify-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg mt-6 disabled:opacity-70 disabled:cursor-not-allowed",
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
                                    "Voer gegevens in om resultaten te zien",
                                    class_name="text-gray-400 font-medium",
                                ),
                                class_name="h-full flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-200 rounded-2xl",
                            ),
                        ),
                        class_name="grid grid-cols-1 lg:grid-cols-2 gap-12",
                    ),
                ),
                technical_details_section(),
                email_confirmation_modal(
                    BatteryEstimatorState.email_sent_modal_open,
                    BatteryEstimatorState.close_email_modal,
                ),
                class_name="flex-1 p-6 md:p-8",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=BatteryEstimatorState.load_page_content,
        )
    )