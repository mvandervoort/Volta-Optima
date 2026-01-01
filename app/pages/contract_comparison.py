import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.states.contract_comparison_state import ContractComparisonState
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)


def coming_soon_badge() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("construction", class_name="w-6 h-6 text-purple-900/80 mb-0.5"),
            rx.el.span(
                "Status",
                class_name="text-[11px] font-bold uppercase tracking-wider text-purple-800 leading-none mb-0.5",
            ),
            rx.el.span(
                "BINNENKORT",
                class_name="text-sm font-black tracking-widest text-purple-950 leading-none",
            ),
            class_name="flex flex-col items-center",
        ),
        title="Deze module is momenteel in ontwikkeling",
        class_name="fixed bottom-6 right-6 z-50 bg-gradient-to-br from-violet-300 to-purple-400 w-[120px] h-[120px] rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[5px] border-white flex items-center justify-center transform -rotate-12 hover:rotate-0 hover:scale-110 transition-all duration-300 ease-out cursor-default select-none animate-in fade-in zoom-in duration-700",
    )


def development_banner() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("rocket", class_name="w-5 h-5 text-purple-600 mr-3"),
                rx.el.p(
                    "Deze module is in actieve ontwikkeling en wordt binnenkort gelanceerd.",
                    class_name="text-sm font-bold text-purple-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.a(
                "Bekijk andere tools →",
                href="/advice-themes",
                class_name="text-xs font-bold text-purple-700 hover:text-purple-900 underline transition-colors",
            ),
            class_name="max-w-3xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4",
        ),
        class_name="w-full bg-purple-100/80 border-y border-purple-200 px-6 py-3 mb-8 rounded-xl",
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        development_banner(),
        rx.el.div(
            rx.icon("scale", class_name="h-12 w-12 text-violet-600 mb-4"),
            rx.el.h1(
                ContractComparisonState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                ContractComparisonState.intro_content["subtitle"],
                class_name="text-xl text-violet-800 font-medium mb-6",
            ),
            rx.html(
                ContractComparisonState.intro_content["instructions"],
                class_name="prose prose-violet text-gray-600 max-w-none text-left w-full",
            ),
            class_name="max-w-3xl mx-auto text-center flex flex-col items-center",
        ),
        class_name="bg-gradient-to-br from-violet-50/80 to-purple-50/50 p-8 md:p-12 rounded-3xl border border-violet-100 shadow-sm mb-12",
    )


def upload_zone(
    text: str,
    upload_id: str,
    handler: rx.EventHandler,
    status: rx.Var,
    subtext: str = "CSV (1 jaar, resolutie 1 uur)",
) -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.el.div(
                rx.icon("cloud-upload", class_name="w-10 h-10 text-violet-500 mb-3"),
                rx.el.div(
                    rx.el.span(
                        text, class_name="text-sm font-medium text-gray-700 text-center"
                    ),
                    info_tooltip(
                        "Upload een CSV-bestand met kolommen voor datum/tijd en waarden. Zorg voor data van een volledig jaar (8760 regels)."
                    ),
                    class_name="flex items-center justify-center",
                ),
                rx.el.p(subtext, class_name="text-xs text-gray-500 mt-1"),
                class_name="flex flex-col items-center justify-center p-6 border-2 border-dashed border-violet-100 rounded-xl bg-violet-50/50 hover:bg-violet-50 transition-colors cursor-pointer w-full",
            ),
            id=upload_id,
            accept={"text/csv": [".csv"], "application/vnd.ms-excel": [".csv"]},
            max_files=1,
            class_name="w-full mb-3",
        ),
        rx.el.div(
            rx.el.div(
                rx.cond(
                    status.contains("✅"),
                    rx.icon("check_check", class_name="w-4 h-4 text-emerald-600"),
                    rx.icon("badge_alert", class_name="w-4 h-4 text-gray-400"),
                ),
                rx.el.span(status, class_name="text-xs text-gray-600 font-medium"),
                class_name="flex items-center gap-2 mb-3",
            ),
            rx.el.button(
                "Verwerk Bestand",
                on_click=handler(rx.upload_files(upload_id=upload_id)),
                class_name="w-full py-2 bg-white border border-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-50 hover:text-violet-600 transition-colors",
            ),
        ),
        class_name="bg-white p-4 rounded-xl border border-gray-200 shadow-sm",
    )


def price_input(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    default_val: float,
    tooltip_text: str = "",
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.label(label, class_name="text-sm font-medium text-gray-700"),
            rx.cond(tooltip_text != "", info_tooltip(tooltip_text)),
            class_name="flex items-center mb-1",
        ),
        rx.el.div(
            rx.el.span(
                "€",
                class_name="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm",
            ),
            rx.el.input(
                type="number",
                step="0.01",
                default_value=value.to_string(),
                on_change=on_change,
                class_name="w-full pl-7 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-violet-500 focus:border-violet-500 outline-none text-sm",
            ),
            class_name="relative",
        ),
        class_name="mb-0",
    )


def technical_details_section() -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.el.div(
                    rx.icon("info", class_name="w-5 h-5 text-violet-600"),
                    class_name="w-8 h-8 rounded-full bg-violet-50 flex items-center justify-center mr-3",
                ),
                rx.el.span(
                    ContractComparisonState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        ContractComparisonState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        ContractComparisonState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=ContractComparisonState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            ContractComparisonState.show_technical_details,
            rx.el.div(
                rx.html(
                    ContractComparisonState.technical_details_content["content"],
                    class_name="prose prose-sm prose-violet max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def comparison_card(
    title: str,
    results: dict,
    color_class: str,
    icon: str,
    bg_class: str,
    is_cheapest: rx.Var[bool] | bool = False,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"w-6 h-6 {color_class}"),
                class_name=f"w-12 h-12 rounded-xl {bg_class} flex items-center justify-center mb-4",
            ),
            rx.el.h3(title, class_name="text-lg font-bold text-gray-900 mb-1"),
            rx.el.div(
                rx.el.span(
                    "€",
                    class_name="text-lg text-gray-500 font-medium mr-1 self-start mt-1",
                ),
                rx.el.span(
                    results["total_cost"].to_string(),
                    class_name="text-3xl font-bold text-gray-900",
                ),
                rx.el.span(
                    "/jaar", class_name="text-sm text-gray-500 ml-1 self-end mb-1"
                ),
                class_name="flex items-baseline mb-4",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Maandelijks:", class_name="text-xs text-gray-500 font-medium"
                    ),
                    rx.el.span(
                        f"€{results['avg_monthly']}",
                        class_name="text-sm font-bold text-gray-700",
                    ),
                    class_name="flex justify-between items-center py-1 border-b border-gray-50",
                ),
                class_name="w-full space-y-1",
            ),
            class_name="flex flex-col items-start w-full",
        ),
        rx.cond(
            is_cheapest,
            rx.el.div(
                "Goedkoopste Optie",
                class_name="absolute top-4 right-4 bg-emerald-100 text-emerald-800 text-xs font-bold px-2 py-1 rounded-full uppercase tracking-wider",
            ),
        ),
        class_name=rx.cond(
            is_cheapest,
            "bg-white p-6 rounded-2xl border-2 border-emerald-500 shadow-md relative overflow-hidden transition-all transform hover:-translate-y-1",
            "bg-white p-6 rounded-2xl border border-gray-100 shadow-sm relative overflow-hidden transition-all transform hover:-translate-y-1 hover:shadow-md",
        ),
    )


def chart_bar(label: str, value: rx.Var, pct: rx.Var, color_class: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                class_name=f"{color_class} h-full rounded-r-md transition-all duration-1000",
                style={"width": f"{pct}%"},
            ),
            class_name="flex-1 h-4 bg-gray-100 rounded-md overflow-hidden",
        ),
        rx.el.div(
            rx.el.span(
                label,
                class_name="text-[10px] text-gray-400 font-bold uppercase w-16 mr-2",
            ),
            rx.el.span(f"€{value}", class_name="text-xs font-bold text-gray-700 ml-2"),
            class_name="flex items-center mt-1",
        ),
        class_name="mb-3",
    )


def month_chart_row(month_data: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(
                month_data["name"], class_name="text-sm font-bold text-gray-900"
            ),
            class_name="mb-3 pb-1 border-b border-gray-50",
        ),
        chart_bar("Vast", month_data["Vast"], month_data["Vast_pct"], "bg-blue-600"),
        chart_bar(
            "Variabel",
            month_data["Variabel"],
            month_data["Variabel_pct"],
            "bg-orange-500",
        ),
        chart_bar(
            "Dynamisch",
            month_data["Dynamisch"],
            month_data["Dynamisch_pct"],
            "bg-violet-500",
        ),
        class_name="bg-gray-50/30 p-4 rounded-xl border border-gray-100/50",
    )


def results_section() -> rx.Component:
    return rx.cond(
        ContractComparisonState.has_results,
        rx.el.div(
            rx.el.h3(
                "Vergelijkingsresultaten",
                class_name="text-xl font-bold text-gray-900 mb-6",
            ),
            rx.el.div(
                comparison_card(
                    "Vast Contract",
                    ContractComparisonState.fixed_results,
                    "text-blue-600",
                    "lock",
                    "bg-blue-50",
                    is_cheapest=ContractComparisonState.is_fixed_cheapest,
                ),
                comparison_card(
                    "Variabel Contract",
                    ContractComparisonState.variable_results,
                    "text-orange-600",
                    "sliders-horizontal",
                    "bg-orange-50",
                    is_cheapest=ContractComparisonState.is_variable_cheapest,
                ),
                comparison_card(
                    "Dynamisch Contract",
                    ContractComparisonState.dynamic_results,
                    "text-violet-600",
                    "zap",
                    "bg-violet-50",
                    is_cheapest=ContractComparisonState.is_dynamic_cheapest,
                ),
                class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
            ),
            rx.el.div(
                rx.el.h4(
                    "Maandelijkse Kosten Verloop",
                    class_name="text-lg font-bold text-gray-900 mb-6",
                ),
                rx.el.div(
                    rx.foreach(
                        ContractComparisonState.comparison_chart_data, month_chart_row
                    ),
                    class_name="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.div(class_name="w-3 h-3 rounded-full bg-blue-600 mr-2"),
                        rx.el.span(
                            "Vast", class_name="text-xs text-gray-600 font-medium"
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.div(class_name="w-3 h-3 rounded-full bg-orange-500 mr-2"),
                        rx.el.span(
                            "Variabel", class_name="text-xs text-gray-600 font-medium"
                        ),
                        class_name="flex items-center",
                    ),
                    rx.el.div(
                        rx.el.div(class_name="w-3 h-3 rounded-full bg-violet-500 mr-2"),
                        rx.el.span(
                            "Dynamisch", class_name="text-xs text-gray-600 font-medium"
                        ),
                        class_name="flex items-center",
                    ),
                    class_name="flex justify-center gap-6 mt-8 pt-6 border-t border-gray-100",
                ),
                class_name="bg-white p-6 md:p-8 rounded-2xl border border-gray-100 shadow-sm",
            ),
            class_name="animate-in fade-in slide-in-from-bottom-4 duration-700 w-full",
        ),
    )


def contract_comparison_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            coming_soon_badge(),
            rx.el.title(
                "Contractvergelijker | Vast vs Variabel vs Dynamisch | Energie Insight"
            ),
            rx.el.meta(
                name="description",
                content="Vergelijk energiekosten van vaste, variabele en dynamische contracten op basis van uw eigen verbruiksdata.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Energiecontract Vergelijker",
                    description="Tool voor het vergelijken van energiekosten tussen verschillende contractvormen.",
                    url="/tools/contract-vergelijking",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [
                        ("Home", "/"),
                        ("Tools", "/tools"),
                        ("Contract Vergelijker", "/tools/contract-vergelijking"),
                    ]
                )
            ),
            advice_sidebar(),
            rx.el.div(
                intro_section(),
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "1. Profielen Uploaden",
                            class_name="text-lg font-bold text-gray-400 mb-4",
                        ),
                        rx.el.div(
                            upload_zone(
                                "Upload Huisverbruik",
                                "consumption_upload",
                                ContractComparisonState.handle_consumption_upload,
                                ContractComparisonState.consumption_status,
                                "CSV met 'Sum [kWh]' kolom (1 jaar)",
                            ),
                            upload_zone(
                                "Upload Zonne-opwek",
                                "production_upload",
                                ContractComparisonState.handle_production_upload,
                                ContractComparisonState.production_status,
                                "CSV met 'Yield' kolom (1 jaar)",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 opacity-60 grayscale-[0.5]",
                        ),
                        rx.el.h3(
                            "2. Contract Tarieven",
                            class_name="text-lg font-bold text-gray-400 mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.h4(
                                    "Vast Contract",
                                    class_name="text-sm font-bold text-blue-700/50 uppercase tracking-wider mb-3",
                                ),
                                price_input(
                                    "Inkoopprijs",
                                    ContractComparisonState.fixed_purchase_price,
                                    ContractComparisonState.set_fixed_purchase_price,
                                    0.4,
                                    "Totale prijs per kWh incl. belastingen voor afname",
                                ),
                                price_input(
                                    "Terugleververgoeding",
                                    ContractComparisonState.fixed_feedin_price,
                                    ContractComparisonState.set_fixed_feedin_price,
                                    0.08,
                                    "Vergoeding per kWh voor netto teruglevering",
                                ),
                                class_name="bg-blue-50/30 p-5 rounded-xl border border-blue-100",
                            ),
                            rx.el.div(
                                rx.el.h4(
                                    "Variabel Contract",
                                    class_name="text-sm font-bold text-orange-700/50 uppercase tracking-wider mb-3",
                                ),
                                price_input(
                                    "Inkoopprijs",
                                    ContractComparisonState.variable_purchase_price,
                                    ContractComparisonState.set_variable_purchase_price,
                                    0.35,
                                    "Totale prijs per kWh incl. belastingen voor afname",
                                ),
                                price_input(
                                    "Terugleververgoeding",
                                    ContractComparisonState.variable_feedin_price,
                                    ContractComparisonState.set_variable_feedin_price,
                                    0.07,
                                    "Vergoeding per kWh voor netto teruglevering",
                                ),
                                class_name="bg-orange-50/30 p-5 rounded-xl border border-orange-100",
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8 opacity-60",
                        ),
                        rx.cond(
                            ContractComparisonState.error_message != "",
                            rx.el.div(
                                rx.icon(
                                    "circle_alert",
                                    class_name="w-5 h-5 text-red-600 mr-2",
                                ),
                                ContractComparisonState.error_message,
                                class_name="mb-6 p-4 bg-red-50 text-red-700 rounded-xl flex items-center border border-red-100",
                            ),
                        ),
                        rx.el.button(
                            "Vergelijk Contracten (Binnenkort)",
                            disabled=True,
                            class_name="w-full py-4 bg-gray-300 text-gray-500 font-bold rounded-xl cursor-not-allowed mb-12 text-lg shadow-inner",
                        ),
                        results_section(),
                    ),
                    class_name="max-w-4xl mx-auto",
                ),
                technical_details_section(),
                class_name="flex-1 p-6 md:p-8",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=ContractComparisonState.load_page_content,
        )
    )