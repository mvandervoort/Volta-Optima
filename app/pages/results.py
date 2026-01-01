import reflex as rx
from app.components.layout import base_layout
from app.components.results_sidebar import results_sidebar
from app.states.results_state import ResultsState
from app.components.protected_guard import protected_guard


def get_calculator_label(type_key: str) -> str:
    labels = {
        "warm_water": "Warm Water Calculator",
        "battery_estimator": "Thuisbatterij Calculator",
        "simple_battery": "Eenvoudige Batterij Scan",
        "solar_yield": "Zonnepanelen Calculator",
        "dakscan": "Dakscan",
        "advanced_battery": "Geavanceerde Batterij Simulatie",
    }
    return labels.get(type_key, type_key.replace("_", " ").title())


def get_calculator_icon(type_key: str) -> str:
    icons = {
        "warm_water": "droplet",
        "battery_estimator": "battery-charging",
        "simple_battery": "zap",
        "solar_yield": "sun",
        "dakscan": "layout-grid",
        "advanced_battery": "activity",
    }
    return icons.get(type_key, "calculator")


def overview_card(title: str, count: int, icon: str, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 text-{color}-600"),
            class_name=f"w-12 h-12 rounded-xl bg-{color}-100 flex items-center justify-center mb-4",
        ),
        rx.el.h3(count, class_name="text-2xl font-bold text-gray-900 mb-1"),
        rx.el.p(title, class_name="text-sm text-gray-500 font-medium"),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-all",
    )


def filter_button(type_key: str, label: str) -> rx.Component:
    is_active = ResultsState.selected_type_filter == type_key
    count = ResultsState.type_counts[type_key]
    return rx.el.button(
        rx.el.span(label, class_name="mr-2"),
        rx.el.span(
            count,
            class_name=rx.cond(
                is_active,
                "bg-emerald-200 text-emerald-800 py-0.5 px-2 rounded-full text-xs",
                "bg-gray-200 text-gray-600 py-0.5 px-2 rounded-full text-xs group-hover:bg-gray-300",
            ),
        ),
        on_click=lambda: ResultsState.set_type_filter(type_key),
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-2 rounded-full text-sm font-medium bg-emerald-100 text-emerald-800 transition-colors",
            "flex items-center px-4 py-2 rounded-full text-sm font-medium bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors group",
        ),
    )


def data_row(item: dict) -> rx.Component:
    return rx.el.div(
        rx.el.span(
            item["label"], class_name="text-sm font-medium text-gray-500 min-w-[150px]"
        ),
        rx.el.span(
            item["value"],
            class_name="text-sm font-semibold text-gray-900 break-all text-right ml-4",
        ),
        class_name="flex justify-between items-center py-2 border-b border-gray-50 last:border-0",
    )


def detail_modal() -> rx.Component:
    return rx.cond(
        ResultsState.detail_modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "calculator", class_name="w-6 h-6 text-emerald-600 mr-2"
                            ),
                            rx.el.h3(
                                get_calculator_label(
                                    ResultsState.selected_calculation[
                                        "calculator_type"
                                    ].to(str)
                                ),
                                class_name="text-lg font-bold text-gray-900",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.el.button(
                            rx.icon(
                                "x",
                                class_name="w-5 h-5 text-gray-400 hover:text-gray-500",
                            ),
                            on_click=ResultsState.close_detail_modal,
                            class_name="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none",
                        ),
                        class_name="flex justify-between items-center mb-6 pb-4 border-b border-gray-100",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h4(
                                "Ingevoerde Gegevens",
                                class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(ResultsState.formatted_input_data, data_row),
                                class_name="bg-gray-50 rounded-xl p-4 mb-6",
                            ),
                        ),
                        rx.el.div(
                            rx.el.h4(
                                "Berekeningsresultaten",
                                class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    ResultsState.formatted_output_data, data_row
                                ),
                                class_name="bg-emerald-50/50 rounded-xl p-4 border border-emerald-100",
                            ),
                        ),
                        class_name="flex flex-col gap-2 overflow-y-auto max-h-[60vh] pr-2",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "Datum:", class_name="text-xs text-gray-400 mr-2"
                            ),
                            rx.el.span(
                                ResultsState.selected_calculation["created_at"]
                                .to(str)
                                .replace("T", " ")[:16],
                                class_name="text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center",
                        ),
                        class_name="flex justify-between items-center mt-6 pt-4 border-t border-gray-100",
                    ),
                    class_name="bg-white rounded-2xl px-4 pt-5 pb-4 overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full sm:p-6",
                ),
                class_name="flex min-h-full items-center justify-center p-4 text-center sm:p-0",
            ),
            class_name="fixed inset-0 z-50 overflow-y-auto bg-gray-500/75 backdrop-blur-sm transition-opacity",
        ),
    )


def result_row(calc: dict) -> rx.Component:
    calc_id = calc["id"].to(str)
    calc_type = calc["calculator_type"]
    date_str = calc["created_at"].to(str).split("T")[0]
    output_data = calc["output_data"].to(dict)
    main_metric = rx.match(
        calc_type,
        ("solar_yield", f"{output_data['ac_annual']} kWh/jr"),
        (
            "warm_water",
            f"€{output_data['gas_total']} (Gas) vs €{output_data['wp_total']} (WP)",
        ),
        ("dakscan", f"{output_data['yield_kwh']} kWh/jr"),
        f"Capaciteit: {output_data.get('optimal_capacity', '-')} kWh",
    )
    return rx.el.tr(
        rx.el.td(
            rx.el.input(
                type="checkbox",
                checked=ResultsState.selected_ids.contains(calc_id),
                on_change=lambda _: ResultsState.toggle_selection(calc_id),
                class_name="w-4 h-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 cursor-pointer",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(date_str, class_name="text-sm text-gray-500"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.icon(
                    get_calculator_icon(calc_type.to(str)),
                    class_name="w-4 h-4 text-emerald-600 mr-2",
                ),
                rx.el.span(
                    get_calculator_label(calc_type.to(str)),
                    class_name="text-sm font-medium text-gray-900",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(main_metric, class_name="text-sm text-gray-600"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("eye", class_name="w-5 h-5"),
                on_click=lambda: ResultsState.open_detail_modal(calc),
                class_name="text-gray-400 hover:text-emerald-600 transition-colors p-2 hover:bg-gray-100 rounded-full",
                title="Bekijk Details",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
        class_name="hover:bg-gray-50 transition-colors",
    )


def confirmation_dialog() -> rx.Component:
    return rx.cond(
        ResultsState.show_confirm_dialog,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "triangle_alert", class_name="w-12 h-12 text-amber-500 mb-4"
                        ),
                        class_name="flex justify-center",
                    ),
                    rx.el.h3(
                        "Resultaten Anonimiseren",
                        class_name="text-xl font-bold text-center text-gray-900 mb-2",
                    ),
                    rx.el.p(
                        "Weet u zeker dat u de geselecteerde resultaten wilt verwijderen? Uw koppeling met deze data wordt verbroken, maar de anonieme gegevens blijven beschikbaar voor onze algemene statistieken.",
                        class_name="text-center text-gray-600 mb-8 text-sm leading-relaxed",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Annuleren",
                            on_click=ResultsState.close_confirm_dialog,
                            class_name="flex-1 px-4 py-3 bg-gray-100 text-gray-700 font-bold rounded-xl hover:bg-gray-200 transition-colors",
                        ),
                        rx.el.button(
                            rx.cond(
                                ResultsState.is_anonymizing,
                                "Verwerken...",
                                "Bevestigen",
                            ),
                            on_click=ResultsState.anonymize_selected,
                            disabled=ResultsState.is_anonymizing,
                            class_name="flex-1 px-4 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg hover:shadow-emerald-200/50",
                        ),
                        class_name="flex gap-4",
                    ),
                    class_name="bg-white rounded-2xl p-8 shadow-2xl w-[90vw] max-w-sm",
                ),
                class_name="flex min-h-full items-center justify-center p-4",
            ),
            class_name="fixed inset-0 z-[100] overflow-y-auto bg-black/60 backdrop-blur-sm animate-in fade-in duration-200",
        ),
    )


def results_content() -> rx.Component:
    return rx.el.div(
        detail_modal(),
        confirmation_dialog(),
        rx.el.div(
            rx.el.h1(
                "Mijn Resultaten", class_name="text-3xl font-bold text-gray-900 mb-2"
            ),
            rx.el.p(
                "Overzicht van uw uitgevoerde berekeningen en adviezen.",
                class_name="text-gray-600 mb-8",
            ),
            rx.cond(
                ResultsState.is_loading,
                rx.el.div(
                    rx.spinner(class_name="w-8 h-8 text-emerald-600"),
                    class_name="flex justify-center py-12",
                ),
                rx.cond(
                    ~ResultsState.has_results,
                    rx.el.div(
                        rx.icon("inbox", class_name="w-12 h-12 text-gray-300 mb-4"),
                        rx.el.h3(
                            "Nog geen resultaten",
                            class_name="text-lg font-medium text-gray-900",
                        ),
                        rx.el.p(
                            "Voer een adviesmodule uit om hier resultaten te zien.",
                            class_name="text-gray-500 font-medium mb-6",
                        ),
                        rx.el.a(
                            "Bekijk Adviesmodules",
                            href="/advice-themes",
                            class_name="px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium",
                        ),
                        class_name="flex flex-col items-center justify-center p-12 bg-gray-50 rounded-2xl border-2 border-dashed border-gray-200",
                    ),
                    rx.el.div(
                        rx.el.div(
                            overview_card(
                                "Totaal Berekeningen",
                                ResultsState.type_counts["all"],
                                "calculator",
                                "blue",
                            ),
                            overview_card(
                                "Zonnepanelen",
                                ResultsState.type_counts.get("solar_yield", 0),
                                "sun",
                                "orange",
                            ),
                            overview_card(
                                "Thuisbatterij",
                                ResultsState.type_counts.get("battery_estimator", 0)
                                + ResultsState.type_counts.get("simple_battery", 0),
                                "battery-charging",
                                "emerald",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Filter op type:",
                                class_name="text-sm font-medium text-gray-700 mr-4",
                            ),
                            rx.el.div(
                                filter_button("all", "Alles"),
                                rx.cond(
                                    ResultsState.type_counts["solar_yield"] > 0,
                                    filter_button("solar_yield", "Zonnepanelen"),
                                ),
                                rx.cond(
                                    ResultsState.type_counts["battery_estimator"] > 0,
                                    filter_button("battery_estimator", "Thuisbatterij"),
                                ),
                                rx.cond(
                                    ResultsState.type_counts["simple_battery"] > 0,
                                    filter_button("simple_battery", "Batterij Scan"),
                                ),
                                rx.cond(
                                    ResultsState.type_counts["warm_water"] > 0,
                                    filter_button("warm_water", "Warm Water"),
                                ),
                                rx.cond(
                                    ResultsState.type_counts["dakscan"] > 0,
                                    filter_button("dakscan", "Dakscan"),
                                ),
                                class_name="flex flex-wrap gap-2",
                            ),
                            class_name="flex flex-col sm:flex-row items-start sm:items-center mb-6 gap-2",
                        ),
                        rx.el.div(
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th(
                                            rx.el.input(
                                                type="checkbox",
                                                checked=ResultsState.all_selected,
                                                on_change=ResultsState.toggle_select_all,
                                                class_name="w-4 h-4 rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 cursor-pointer",
                                            ),
                                            class_name="px-6 py-3 text-left whitespace-nowrap",
                                        ),
                                        rx.el.th(
                                            "Datum",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Type",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Belangrijkste Gegevens",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Details",
                                            class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                    ),
                                    class_name="bg-gray-50",
                                ),
                                rx.el.tbody(
                                    rx.foreach(
                                        ResultsState.filtered_calculations.to(
                                            list[dict]
                                        ),
                                        result_row,
                                    ),
                                    class_name="bg-white divide-y divide-gray-200",
                                ),
                                class_name="min-w-full divide-y divide-gray-200",
                            ),
                            class_name="shadow-sm overflow-hidden border border-gray-200 sm:rounded-lg bg-white overflow-x-auto",
                        ),
                    ),
                ),
            ),
            class_name="max-w-5xl",
        ),
        class_name="flex-1 p-6 md:p-8",
    )


def results_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            results_sidebar(),
            protected_guard(results_content(), requires_auth=True),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=ResultsState.load_user_results,
        )
    )