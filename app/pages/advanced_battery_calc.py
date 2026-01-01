import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.components.tooltip import info_tooltip
from app.states.advanced_battery_state import AdvancedBatteryState
from app.components.email_confirmation_modal import email_confirmation_modal


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("activity", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                AdvancedBatteryState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                AdvancedBatteryState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                AdvancedBatteryState.intro_content["instructions"],
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
                    AdvancedBatteryState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        AdvancedBatteryState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        AdvancedBatteryState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=AdvancedBatteryState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            AdvancedBatteryState.show_technical_details,
            rx.el.div(
                rx.html(
                    AdvancedBatteryState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def advanced_battery_calc_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            advice_sidebar(),
            rx.el.div(
                intro_section(),
                rx.el.div(
                    rx.el.div(
                        rx.el.h3(
                            "1. Profiel Uploads",
                            class_name="text-lg font-bold text-gray-900 mb-4",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Verbruiksprofiel (CSV)",
                                    class_name="block text-sm font-medium text-gray-700 mb-2",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "upload",
                                        class_name="w-6 h-6 text-emerald-600 mb-2",
                                    ),
                                    rx.el.span(
                                        "Klik om te uploaden",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    class_name="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center hover:bg-gray-50 transition-colors cursor-pointer",
                                ),
                                class_name="mb-6",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Productieprofiel (CSV)",
                                    class_name="block text-sm font-medium text-gray-700 mb-2",
                                ),
                                rx.el.div(
                                    rx.icon(
                                        "upload",
                                        class_name="w-6 h-6 text-emerald-600 mb-2",
                                    ),
                                    rx.el.span(
                                        "Klik om te uploaden",
                                        class_name="text-sm text-gray-500",
                                    ),
                                    class_name="border-2 border-dashed border-gray-200 rounded-xl p-8 flex flex-col items-center justify-center hover:bg-gray-50 transition-colors cursor-pointer",
                                ),
                                class_name="mb-6",
                            ),
                        ),
                        rx.el.h3(
                            "2. Systeem Parameters",
                            class_name="text-lg font-bold text-gray-900 mb-4 mt-8",
                        ),
                        rx.el.div(
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "Batterij Capaciteit (kWh)",
                                        class_name="text-sm font-medium text-gray-700",
                                    ),
                                    info_tooltip(
                                        "De opslagcapaciteit van de batterij in kWh."
                                    ),
                                    class_name="flex items-center mb-1",
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value=AdvancedBatteryState.capacity.to_string(),
                                    on_change=AdvancedBatteryState.set_capacity,
                                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-emerald-500",
                                ),
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.label(
                                        "Omvormer Vermogen (kW)",
                                        class_name="text-sm font-medium text-gray-700",
                                    ),
                                    info_tooltip(
                                        "Het maximale laad- en ontlaadvermogen van de omvormer in kW."
                                    ),
                                    class_name="flex items-center mb-1",
                                ),
                                rx.el.input(
                                    type="number",
                                    default_value=AdvancedBatteryState.power.to_string(),
                                    on_change=AdvancedBatteryState.set_power,
                                    class_name="w-full px-4 py-2 border border-gray-300 rounded-lg outline-none focus:border-emerald-500",
                                ),
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8",
                        ),
                        rx.el.button(
                            rx.cond(
                                AdvancedBatteryState.is_processing,
                                "Verwerken...",
                                "Start Simulatie",
                            ),
                            on_click=AdvancedBatteryState.start_simulation,
                            disabled=AdvancedBatteryState.is_processing,
                            class_name="w-full py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-lg disabled:opacity-70",
                        ),
                        rx.cond(
                            AdvancedBatteryState.has_calculated,
                            rx.el.div(
                                rx.el.div(class_name="h-px bg-gray-100 my-6"),
                                rx.el.h3(
                                    "Resultaten (Demo)",
                                    class_name="text-lg font-bold text-gray-900 mb-4",
                                ),
                                rx.el.p(
                                    "De simulatie is voltooid. Bekijk het gedetailleerde rapport in uw e-mail.",
                                    class_name="text-gray-600 mb-6",
                                ),
                                rx.cond(
                                    AdvancedBatteryState.is_authenticated,
                                    rx.el.button(
                                        rx.cond(
                                            AdvancedBatteryState.is_sending_email,
                                            rx.spinner(
                                                class_name="w-5 h-5 mr-2 text-white"
                                            ),
                                            rx.icon("mail", class_name="w-5 h-5 mr-2"),
                                        ),
                                        rx.cond(
                                            AdvancedBatteryState.is_sending_email,
                                            "Verzenden...",
                                            "E-mail Rapport",
                                        ),
                                        on_click=AdvancedBatteryState.email_results,
                                        disabled=AdvancedBatteryState.is_sending_email,
                                        class_name="w-full flex items-center justify-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg disabled:opacity-70 disabled:cursor-not-allowed",
                                    ),
                                    rx.el.div(
                                        rx.el.p(
                                            "Log in om het volledige rapport te ontvangen.",
                                            class_name="text-sm text-gray-500 italic text-center",
                                        ),
                                        rx.el.a(
                                            "Inloggen",
                                            href="/login",
                                            class_name="block w-full text-center mt-2 text-emerald-600 font-bold hover:underline",
                                        ),
                                    ),
                                ),
                                class_name="animate-in fade-in slide-in-from-top-2 duration-500",
                            ),
                        ),
                        class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm",
                    ),
                    class_name="max-w-3xl",
                ),
                technical_details_section(),
                email_confirmation_modal(
                    AdvancedBatteryState.email_sent_modal_open,
                    AdvancedBatteryState.close_email_modal,
                ),
                class_name="flex-1 p-6 md:p-8",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=AdvancedBatteryState.load_page_content,
        )
    )