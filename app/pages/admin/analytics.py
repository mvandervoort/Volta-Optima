import reflex as rx
from app.components.admin_sidebar import admin_sidebar
from app.states.admin_analytics_state import AdminAnalyticsState
from app.components.protected_guard import admin_guard


def stat_card(
    title: str, value: str, subtext: str = "", icon: str = "bar-chart"
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name="w-5 h-5 text-emerald-600"),
                class_name="w-10 h-10 rounded-lg bg-emerald-50 flex items-center justify-center mb-3",
            ),
            rx.el.h3(value, class_name="text-2xl font-bold text-gray-900"),
            rx.el.p(title, class_name="text-sm text-gray-500 font-medium"),
            rx.cond(
                subtext != "",
                rx.el.p(
                    subtext, class_name="text-xs text-emerald-600 mt-1 font-medium"
                ),
            ),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
    )


def recent_calc_row(calc: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.span(
                calc["created_at"].to(str).split("T")[0],
                class_name="text-sm font-medium text-gray-900",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                calc["calculator_type"],
                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.cond(
                calc["user_id"],
                rx.cond(
                    calc["user_email"],
                    rx.el.div(
                        rx.el.span(
                            calc["user_email"],
                            class_name="text-sm text-emerald-600 font-medium block truncate max-w-[150px]",
                            title=calc["user_email"],
                        ),
                        rx.el.span(
                            "Logged User", class_name="text-xs text-gray-400 block"
                        ),
                    ),
                    rx.el.span(
                        "Logged User", class_name="text-sm text-emerald-600 font-medium"
                    ),
                ),
                rx.el.div(
                    rx.el.span("Anonymous", class_name="text-sm text-gray-500 block"),
                    rx.el.span(
                        calc["ip_address"], class_name="text-xs text-gray-400 block"
                    ),
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.pre(
                    calc["input_data"].to_string(),
                    class_name="text-xs text-gray-500 overflow-hidden text-ellipsis max-w-xs",
                )
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.pre(
                    calc["output_data"].to_string(),
                    class_name="text-xs text-gray-500 overflow-hidden text-ellipsis max-w-xs",
                )
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("eye", class_name="w-5 h-5"),
                on_click=lambda: AdminAnalyticsState.open_detail_modal(calc),
                class_name="text-gray-400 hover:text-emerald-600 transition-colors p-2 hover:bg-gray-100 rounded-full",
                title="Bekijk Details",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
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
        AdminAnalyticsState.detail_modal_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "calculator", class_name="w-6 h-6 text-emerald-600 mr-2"
                            ),
                            rx.el.h3(
                                AdminAnalyticsState.selected_stat["calculator_type"]
                                .to(str)
                                .replace("_", " ")
                                .title(),
                                class_name="text-lg font-bold text-gray-900",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.el.button(
                            rx.icon(
                                "x",
                                class_name="w-5 h-5 text-gray-400 hover:text-gray-500",
                            ),
                            on_click=AdminAnalyticsState.close_detail_modal,
                            class_name="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none",
                        ),
                        class_name="flex justify-between items-center mb-6 pb-4 border-b border-gray-100",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h4(
                                "Input Parameters",
                                class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    AdminAnalyticsState.formatted_input_data, data_row
                                ),
                                class_name="bg-gray-50 rounded-xl p-4 mb-6",
                            ),
                        ),
                        rx.el.div(
                            rx.el.h4(
                                "Resultaten",
                                class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                            ),
                            rx.el.div(
                                rx.foreach(
                                    AdminAnalyticsState.formatted_output_data, data_row
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
                                AdminAnalyticsState.selected_stat["created_at"]
                                .to(str)
                                .replace("T", " ")[:16],
                                class_name="text-xs font-medium text-gray-600",
                            ),
                            class_name="flex items-center",
                        ),
                        rx.cond(
                            AdminAnalyticsState.selected_stat["user_email"],
                            rx.el.div(
                                rx.el.span(
                                    "User:", class_name="text-xs text-gray-400 mr-2"
                                ),
                                rx.el.span(
                                    AdminAnalyticsState.selected_stat["user_email"],
                                    class_name="text-xs font-medium text-emerald-600",
                                ),
                                class_name="flex items-center",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "IP:", class_name="text-xs text-gray-400 mr-2"
                                ),
                                rx.el.span(
                                    AdminAnalyticsState.selected_stat["ip_address"],
                                    class_name="text-xs font-medium text-gray-600",
                                ),
                                class_name="flex items-center",
                            ),
                        ),
                        class_name="flex justify-between items-center mt-6 pt-4 border-t border-gray-100",
                    ),
                    class_name="bg-white rounded-2xl px-4 pt-5 pb-4 overflow-hidden shadow-xl transform transition-all sm:max-w-lg sm:w-full sm:p-6",
                ),
                class_name="flex min-h-full items-center justify-center p-4 text-center sm:p-0",
            ),
            class_name="fixed inset-0 z-50 overflow-y-auto bg-gray-500 bg-opacity-75 backdrop-blur-sm transition-opacity",
        ),
    )


def analytics_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            detail_modal(),
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Berekeningsstatistieken",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.div(
                            rx.el.select(
                                rx.el.option("Laatste 7 dagen", value="7"),
                                rx.el.option("Laatste 30 dagen", value="30"),
                                rx.el.option("Laatste 90 dagen", value="90"),
                                value=AdminAnalyticsState.selected_date_range,
                                on_change=AdminAnalyticsState.set_date_range,
                                class_name="bg-white border border-gray-300 text-gray-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 mr-2 appearance-none",
                            ),
                            rx.el.select(
                                rx.el.option("Alle Types", value="all"),
                                rx.el.option("Solar Yield", value="solar_yield"),
                                rx.el.option("Warm Water", value="warm_water"),
                                rx.el.option(
                                    "Batterij Estimator", value="battery_estimator"
                                ),
                                rx.el.option("Simple Battery", value="simple_battery"),
                                rx.el.option(
                                    "Advanced Battery", value="advanced_battery"
                                ),
                                value=AdminAnalyticsState.selected_calc_type,
                                on_change=AdminAnalyticsState.set_calc_type,
                                class_name="bg-white border border-gray-300 text-gray-700 text-sm rounded-lg focus:ring-emerald-500 focus:border-emerald-500 block p-2.5 appearance-none",
                            ),
                            class_name="flex items-center",
                        ),
                        class_name="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4",
                    ),
                    rx.cond(
                        AdminAnalyticsState.is_loading,
                        rx.el.div(
                            rx.spinner(class_name="w-8 h-8 text-emerald-600"),
                            class_name="flex justify-center py-12",
                        ),
                        rx.el.div(
                            rx.el.div(
                                stat_card(
                                    "Totaal Berekeningen",
                                    AdminAnalyticsState.total_calculations.to_string(),
                                    "All time",
                                    "calculator",
                                ),
                                stat_card(
                                    "Deze Periode",
                                    AdminAnalyticsState.calculations_this_week_count.to_string(),
                                    "Selectie",
                                    "calendar",
                                ),
                                stat_card(
                                    "Gebruikersratio",
                                    f"{AdminAnalyticsState.logged_in_count} / {AdminAnalyticsState.anon_count}",
                                    "Logged In / Anon",
                                    "users",
                                ),
                                stat_card(
                                    "Populairste Tool",
                                    AdminAnalyticsState.most_popular_calculator,
                                    "Top categorie",
                                    "trophy",
                                ),
                                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.h3(
                                        "Trend over Tijd",
                                        class_name="text-lg font-bold text-gray-900 mb-4",
                                    ),
                                    rx.recharts.line_chart(
                                        rx.recharts.cartesian_grid(
                                            stroke_dasharray="3 3", vertical=False
                                        ),
                                        rx.recharts.graphing_tooltip(),
                                        rx.recharts.x_axis(
                                            data_key="date", tick={"fontSize": 12}
                                        ),
                                        rx.recharts.y_axis(tick={"fontSize": 12}),
                                        rx.recharts.line(
                                            data_key="count",
                                            stroke="#059669",
                                            stroke_width=2,
                                            dot=True,
                                            name="Berekeningen",
                                        ),
                                        data=AdminAnalyticsState.calculations_over_time,
                                        width="100%",
                                        height=300,
                                    ),
                                    class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
                                ),
                                rx.el.div(
                                    rx.el.h3(
                                        "Verdeling per Type",
                                        class_name="text-lg font-bold text-gray-900 mb-4",
                                    ),
                                    rx.recharts.bar_chart(
                                        rx.recharts.cartesian_grid(
                                            stroke_dasharray="3 3", vertical=False
                                        ),
                                        rx.recharts.graphing_tooltip(),
                                        rx.recharts.x_axis(data_key="type", hide=True),
                                        rx.recharts.y_axis(tick={"fontSize": 12}),
                                        rx.recharts.bar(
                                            data_key="value",
                                            fill="#3b82f6",
                                            radius=[4, 4, 0, 0],
                                            name="Aantal",
                                        ),
                                        data=AdminAnalyticsState.calculations_by_type,
                                        width="100%",
                                        height=300,
                                    ),
                                    class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
                                ),
                                class_name="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8",
                            ),
                            rx.el.div(
                                rx.el.h3(
                                    "Recente Activiteit",
                                    class_name="text-lg font-bold text-gray-900 mb-4",
                                ),
                                rx.el.div(
                                    rx.el.table(
                                        rx.el.thead(
                                            rx.el.tr(
                                                rx.el.th(
                                                    "Datum",
                                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "Type",
                                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "Gebruiker",
                                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "Inputs",
                                                    class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                                ),
                                                rx.el.th(
                                                    "Resultaat",
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
                                                AdminAnalyticsState.recent_calculations,
                                                recent_calc_row,
                                            ),
                                            class_name="bg-white divide-y divide-gray-200",
                                        ),
                                        class_name="min-w-full divide-y divide-gray-200",
                                    ),
                                    class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg bg-white overflow-x-auto",
                                ),
                            ),
                        ),
                    ),
                ),
                class_name="flex-1 p-8 overflow-auto bg-gray-50",
                on_mount=AdminAnalyticsState.load_analytics,
            ),
            class_name="flex min-h-screen bg-gray-50",
        )
    )