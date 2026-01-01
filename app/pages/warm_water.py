import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar
from app.states.warmwater_state import WarmWaterState
from app.components.tooltip import info_tooltip
from app.components.structured_data import (
    json_ld_script,
    software_application_schema,
    breadcrumb_schema,
)
from app.components.email_confirmation_modal import email_confirmation_modal


def form_label(text: str, info: str = "") -> rx.Component:
    return rx.el.div(
        rx.el.label(text, class_name="block text-sm font-semibold text-gray-700"),
        rx.cond(info != "", info_tooltip(info)),
        class_name="flex items-center mb-1",
    )


def input_field(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    type_: str = "number",
    step: str = "1",
    suffix: str = "",
    placeholder: str = "",
    info: str = "",
    key: str | rx.Var = "",
) -> rx.Component:
    return rx.el.div(
        form_label(label, info),
        rx.el.div(
            rx.el.input(
                type=type_,
                step=step,
                default_value=value.to_string(),
                on_change=on_change,
                placeholder=placeholder,
                class_name="w-full px-4 py-2.5 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all bg-white text-gray-900 shadow-sm placeholder:text-gray-400",
            ),
            rx.cond(
                suffix != "",
                rx.el.span(
                    suffix,
                    class_name="absolute right-4 top-1/2 -translate-y-1/2 text-gray-500 text-sm pointer-events-none",
                ),
            ),
            class_name="relative",
        ),
        class_name="w-full mb-4",
    )


def slider_input(
    label: str,
    value: rx.Var,
    on_change: rx.EventHandler,
    min_val: float,
    max_val: float,
    step: float,
    suffix: str = "",
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            form_label(label),
            rx.el.div(
                rx.el.span(value, class_name="font-semibold text-gray-900"),
                rx.el.span(suffix, class_name="text-gray-500 text-sm ml-1"),
                class_name="flex items-baseline bg-gray-50 px-2 py-1 rounded text-sm border border-gray-200",
            ),
            class_name="flex justify-between items-center mb-1",
        ),
        rx.el.input(
            type="range",
            min=min_val,
            max=max_val,
            step=step,
            default_value=value,
            key=value.to_string(),
            on_change=on_change.throttle(100),
            class_name="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600",
        ),
        class_name="w-full mb-4",
    )


def accordion_section(
    title: str,
    icon: str,
    is_open: bool,
    on_toggle: rx.EventHandler,
    children: rx.Component,
    color_class: str = "bg-blue-50",
    icon_color: str = "text-blue-600",
) -> rx.Component:
    return rx.el.div(
        rx.el.button(
            rx.el.div(
                rx.icon(icon, class_name=f"w-5 h-5 {icon_color} mr-3"),
                rx.el.h3(title, class_name="text-base font-bold text-gray-900"),
                class_name="flex items-center",
            ),
            rx.icon(
                "chevron-down",
                class_name=rx.cond(
                    is_open,
                    "w-5 h-5 text-gray-500 transform rotate-180 transition-transform duration-200",
                    "w-5 h-5 text-gray-500 transition-transform duration-200",
                ),
            ),
            on_click=on_toggle,
            class_name=rx.cond(
                is_open,
                f"w-full flex justify-between items-center px-6 py-4 {color_class} rounded-t-xl transition-colors border-b border-gray-100",
                "w-full flex justify-between items-center px-6 py-4 bg-gray-50 hover:bg-gray-100 rounded-xl transition-all",
            ),
        ),
        rx.cond(
            is_open,
            rx.el.div(
                children,
                class_name="p-6 bg-white border-x border-b border-gray-100 rounded-b-xl shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="mb-4",
    )


def compact_result_card(
    title: str,
    icon: str,
    color_class: str,
    cost: rx.Var,
    is_cheapest: bool,
    is_wp: bool = False,
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name=f"w-6 h-6 {color_class} mr-3"),
            rx.el.h4(title, class_name="text-base font-bold text-gray-700"),
            class_name="flex items-center mb-3",
        ),
        rx.el.div(
            rx.el.span(
                "€", class_name="text-lg text-gray-500 font-medium mr-1 self-start mt-1"
            ),
            rx.el.span(cost, class_name="text-3xl font-bold text-gray-900"),
            rx.el.span("/jaar", class_name="text-sm text-gray-500 ml-1 self-end mb-1"),
            class_name="flex items-baseline",
        ),
        class_name=rx.cond(
            is_wp & is_cheapest,
            "bg-emerald-50 p-6 rounded-xl border-2 border-emerald-500 shadow-md relative overflow-hidden",
            "bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow",
        ),
    )


def comparison_bar_chart() -> rx.Component:
    return rx.el.div(
        rx.el.h4(
            "Visuele Vergelijking", class_name="text-sm font-bold text-gray-900 mb-4"
        ),
        rx.recharts.bar_chart(
            rx.recharts.cartesian_grid(
                stroke_dasharray="3 3", vertical=False, class_name="stroke-gray-200"
            ),
            rx.recharts.x_axis(data_key="name", hide=True),
            rx.recharts.y_axis(
                axis_line=False,
                tick_line=False,
                tick={"fontSize": 12, "fill": "#6b7280"},
                unit="€",
                domain=[0, "auto"],
            ),
            rx.recharts.tooltip(
                content_style={
                    "backgroundColor": "white",
                    "borderRadius": "8px",
                    "border": "1px solid #e5e7eb",
                    "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1)",
                },
                cursor=False,
            ),
            rx.recharts.bar(
                data_key="Huidig (Gas)", fill="#f97316", radius=[4, 4, 0, 0], name="Gas"
            ),
            rx.recharts.bar(
                data_key="Elektrische Boiler",
                fill="#3b82f6",
                radius=[4, 4, 0, 0],
                name="E-Boiler",
            ),
            rx.recharts.bar(
                data_key="Warmtepompboiler",
                fill="#10b981",
                radius=[4, 4, 0, 0],
                name="WP-Boiler",
            ),
            data=WarmWaterState.bar_chart_data,
            width="100%",
            height=300,
            margin={"top": 20, "right": 30, "left": 0, "bottom": 0},
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(class_name="w-3 h-3 rounded-full bg-orange-500 mr-2"),
                rx.el.span("Gas", class_name="text-xs text-gray-600"),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.div(class_name="w-3 h-3 rounded-full bg-blue-500 mr-2"),
                rx.el.span("E-Boiler", class_name="text-xs text-gray-600"),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.div(class_name="w-3 h-3 rounded-full bg-emerald-500 mr-2"),
                rx.el.span("WP-Boiler", class_name="text-xs text-gray-600"),
                class_name="flex items-center",
            ),
            class_name="flex justify-center gap-4 mt-4",
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-100",
    )


def table_row(
    label: str, val1: rx.Var, val2: rx.Var, val3: rx.Var, is_total: bool = False
) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            label,
            class_name=f"px-4 py-3 text-sm text-gray-600 {('font-bold' if is_total else '')} whitespace-nowrap",
        ),
        rx.el.td(
            val1,
            class_name=f"px-4 py-3 text-sm text-gray-900 text-right {('font-bold text-base' if is_total else '')} whitespace-nowrap",
        ),
        rx.el.td(
            val2,
            class_name=f"px-4 py-3 text-sm text-gray-900 text-right {('font-bold text-base' if is_total else '')} whitespace-nowrap",
        ),
        rx.el.td(
            val3,
            class_name=f"px-4 py-3 text-sm text-gray-900 text-right {('font-bold text-base' if is_total else '')} whitespace-nowrap",
        ),
        class_name="border-b border-gray-50 last:border-0 hover:bg-gray-50/50",
    )


def comparison_table() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.table(
                rx.el.thead(
                    rx.el.tr(
                        rx.el.th(
                            "KOSTENPOST",
                            class_name="px-4 py-3 text-left text-xs font-bold text-gray-400 uppercase tracking-wider whitespace-nowrap w-1/4",
                        ),
                        rx.el.th(
                            "HUIDIG (GAS)",
                            class_name="px-4 py-3 text-right text-xs font-bold text-orange-500 uppercase tracking-wider whitespace-nowrap w-1/4",
                        ),
                        rx.el.th(
                            "ELEK. BOILER",
                            class_name="px-4 py-3 text-right text-xs font-bold text-blue-500 uppercase tracking-wider whitespace-nowrap w-1/4",
                        ),
                        rx.el.th(
                            "WP-BOILER",
                            class_name="px-4 py-3 text-right text-xs font-bold text-emerald-500 uppercase tracking-wider whitespace-nowrap w-1/4",
                        ),
                        class_name="bg-gray-50 border-b border-gray-100",
                    )
                ),
                rx.el.tbody(
                    table_row(
                        "Energieverbruik (Bruto)",
                        rx.text("€", WarmWaterState.gas_energy_cost),
                        rx.text("€", WarmWaterState.boiler_energy_cost),
                        rx.text("€", WarmWaterState.wp_energy_cost),
                    ),
                    rx.el.tr(
                        rx.el.td(
                            rx.el.div(
                                rx.icon(
                                    "sun", class_name="w-4 h-4 text-emerald-500 mr-2"
                                ),
                                "Beschikbaar Surplus",
                                class_name="flex items-center text-emerald-600 font-medium whitespace-nowrap",
                            ),
                            class_name="px-4 py-3 text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            "-",
                            class_name="px-4 py-3 text-sm text-gray-400 text-right border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            rx.text(
                                WarmWaterState.annual_solar_surplus,
                                " kWh",
                                class_name="font-bold text-emerald-600",
                            ),
                            class_name="px-4 py-3 text-right text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            rx.text(
                                WarmWaterState.annual_solar_surplus,
                                " kWh",
                                class_name="font-bold text-emerald-600",
                            ),
                            class_name="px-4 py-3 text-right text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                    ),
                    rx.el.tr(
                        rx.el.td(
                            rx.el.div(
                                rx.icon(
                                    "circle_check",
                                    class_name="w-4 h-4 text-emerald-500 mr-2",
                                ),
                                "Benut Surplus",
                                class_name="flex items-center text-emerald-600 font-medium whitespace-nowrap",
                            ),
                            class_name="px-4 py-3 text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            "-",
                            class_name="px-4 py-3 text-sm text-gray-400 text-right border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            rx.text(
                                WarmWaterState.boiler_solar_kwh,
                                " kWh",
                                class_name="font-bold text-emerald-600",
                            ),
                            class_name="px-4 py-3 text-right text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                        rx.el.td(
                            rx.text(
                                WarmWaterState.wp_solar_kwh,
                                " kWh",
                                class_name="font-bold text-emerald-600",
                            ),
                            class_name="px-4 py-3 text-right text-sm border-b border-gray-50 bg-emerald-50/10",
                        ),
                    ),
                    rx.el.tr(
                        rx.el.td(
                            rx.el.div(
                                rx.icon(
                                    "triangle_alert",
                                    class_name="w-4 h-4 text-orange-500 mr-2",
                                ),
                                "Onbenut Surplus",
                                class_name="flex items-center text-orange-600 font-medium whitespace-nowrap",
                            ),
                            class_name="px-4 py-3 text-sm border-b border-gray-50",
                        ),
                        rx.el.td(
                            "-",
                            class_name="px-4 py-3 text-sm text-gray-400 text-right border-b border-gray-50",
                        ),
                        rx.el.td(
                            rx.text(WarmWaterState.boiler_unused_surplus, " kWh"),
                            class_name="px-4 py-3 text-sm text-orange-600 font-medium text-right border-b border-gray-50",
                        ),
                        rx.el.td(
                            rx.text(WarmWaterState.wp_unused_surplus, " kWh"),
                            class_name="px-4 py-3 text-sm text-orange-600 font-medium text-right border-b border-gray-50",
                        ),
                    ),
                    table_row(
                        "Gemiste Teruglevering",
                        "-",
                        rx.text("€", WarmWaterState.boiler_opportunity_cost),
                        rx.text("€", WarmWaterState.wp_opportunity_cost),
                    ),
                    table_row(
                        "Onderhoud",
                        rx.text("€", WarmWaterState.gas_maintenance_cost),
                        rx.text("€", WarmWaterState.boiler_maintenance_cost),
                        rx.text("€", WarmWaterState.wp_maintenance_cost),
                    ),
                    table_row(
                        "Afschrijving",
                        rx.text("€", WarmWaterState.gas_depreciation_cost),
                        rx.text("€", WarmWaterState.boiler_depreciation),
                        rx.text("€", WarmWaterState.wp_depreciation),
                    ),
                    table_row(
                        "Totaal per jaar",
                        rx.text("€", WarmWaterState.gas_total),
                        rx.text("€", WarmWaterState.boiler_total),
                        rx.text("€", WarmWaterState.wp_total),
                        is_total=True,
                    ),
                ),
                class_name="w-full",
            ),
            class_name="overflow-x-auto",
        ),
        class_name="bg-white rounded-xl border border-gray-100 shadow-sm overflow-hidden w-full",
    )


def waterbatterij_explanation() -> rx.Component:
    return rx.cond(
        WarmWaterState.waterbatterij_enabled
        | WarmWaterState.wpboiler_waterbatterij_enabled,
        rx.el.div(
            rx.el.div(
                rx.icon("sun", class_name="w-5 h-5 text-yellow-600 mr-2 mt-0.5"),
                rx.el.div(
                    rx.el.h4(
                        "Hoe de Waterbatterij werkt",
                        class_name="font-bold text-gray-900",
                    ),
                    rx.el.p(
                        "Door uw zonne-overschot te gebruiken om water te verwarmen, vermijdt u dure netstroom en 'slaat' u energie op in de vorm van warm water. De getoonde 'Effectieve stroomprijs' is een gemiddelde van gratis/goedkope zonnestroom en resterende netstroom.",
                        class_name="text-sm text-gray-600 mt-1",
                    ),
                    class_name="flex-1",
                ),
                class_name="flex items-start",
            ),
            class_name="bg-yellow-50 border border-yellow-100 p-4 rounded-xl mb-8",
        ),
    )


def intro_section() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("droplet", class_name="h-12 w-12 text-emerald-600 mb-4"),
            rx.el.h1(
                WarmWaterState.intro_content["title"],
                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
            ),
            rx.el.h2(
                WarmWaterState.intro_content["subtitle"],
                class_name="text-xl text-emerald-800 font-medium mb-6",
            ),
            rx.html(
                WarmWaterState.intro_content["instructions"],
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
                    WarmWaterState.technical_details_content["title"],
                    class_name="font-bold text-gray-900",
                ),
                class_name="flex items-center",
            ),
            rx.el.div(
                rx.el.span(
                    rx.cond(
                        WarmWaterState.show_technical_details,
                        "Verberg details",
                        "Toon details",
                    ),
                    class_name="text-sm text-gray-500 mr-2 hidden sm:block",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        WarmWaterState.show_technical_details,
                        "w-5 h-5 text-gray-400 transform rotate-180 transition-transform duration-200",
                        "w-5 h-5 text-gray-400 transition-transform duration-200",
                    ),
                ),
                class_name="flex items-center",
            ),
            on_click=WarmWaterState.toggle_technical_details,
            class_name="w-full flex items-center justify-between p-5 bg-white hover:bg-gray-50 transition-colors rounded-xl border border-gray-200 shadow-sm group",
        ),
        rx.cond(
            WarmWaterState.show_technical_details,
            rx.el.div(
                rx.html(
                    WarmWaterState.technical_details_content["content"],
                    class_name="prose prose-sm prose-emerald max-w-none text-gray-600",
                ),
                class_name="mt-2 p-6 bg-white rounded-xl border border-gray-200 shadow-sm animate-in slide-in-from-top-2 duration-200",
            ),
        ),
        class_name="w-full max-w-4xl mx-auto mt-12",
    )


def warm_water_content() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            intro_section(),
            accordion_section(
                "Warmwater Verbruik",
                "droplet",
                WarmWaterState.section_verbruik_open,
                lambda: WarmWaterState.toggle_section("verbruik"),
                rx.el.div(
                    rx.el.div(
                        input_field(
                            "Aantal Personen",
                            WarmWaterState.persons,
                            WarmWaterState.set_persons,
                            info="Het aantal bewoners in uw huishouden.",
                        ),
                        input_field(
                            "Liters per persoon/dag",
                            WarmWaterState.liters_per_person,
                            WarmWaterState.set_liters_per_person,
                            suffix="L",
                            info="Gemiddeld warmwaterverbruik per persoon per dag (douchen, kraan).",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.span(
                                "OF (EXPERT)",
                                class_name="px-3 py-1 bg-white text-gray-400 text-xs font-bold uppercase tracking-wider",
                            ),
                            class_name="relative flex justify-center border-t border-gray-100 my-6",
                        ),
                        class_name="relative",
                    ),
                    input_field(
                        "Direct kWh per jaar (Optioneel)",
                        WarmWaterState.direct_kwh_annual,
                        WarmWaterState.set_direct_kwh_annual,
                        suffix="kWh",
                        placeholder="Laat leeg om te berekenen o.b.v. personen",
                        info="Als u uw exacte jaarverbruik voor warm water weet, vul dat hier in.",
                    ),
                ),
                color_class="bg-blue-50",
                icon_color="text-blue-600",
            ),
            accordion_section(
                "Huidige Situatie (Gas CV)",
                "flame",
                WarmWaterState.section_gas_open,
                lambda: WarmWaterState.toggle_section("gas"),
                rx.el.div(
                    input_field(
                        "Gasprijs",
                        WarmWaterState.gas_price,
                        WarmWaterState.set_gas_price,
                        step="0.01",
                        suffix="€/m³",
                        info="Huidige gasprijs per m³ inclusief belastingen.",
                    ),
                    rx.el.div(
                        input_field(
                            "Rendement",
                            WarmWaterState.cv_efficiency,
                            WarmWaterState.set_cv_efficiency,
                            step="0.01",
                            info="Rendement van uw CV-ketel voor tapwater.",
                        ),
                        input_field(
                            "Onderhoud/jr",
                            WarmWaterState.gas_maintenance,
                            WarmWaterState.set_gas_maintenance,
                            suffix="€",
                            info="Jaarlijkse onderhoudskosten.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                ),
                color_class="bg-orange-50",
                icon_color="text-orange-500",
            ),
            accordion_section(
                "Elektrische Boiler (B-Label)",
                "zap",
                WarmWaterState.section_boiler_open,
                lambda: WarmWaterState.toggle_section("boiler"),
                rx.el.div(
                    input_field(
                        "Aanschafprijs",
                        WarmWaterState.boiler_purchase_price,
                        WarmWaterState.set_boiler_purchase_price,
                        suffix="€",
                        key="boiler_price_"
                        + WarmWaterState.waterbatterij_enabled.to_string(),
                        info="Aanschafprijs inclusief installatie.",
                    ),
                    rx.el.div(
                        input_field(
                            "Levensduur",
                            WarmWaterState.boiler_lifespan,
                            WarmWaterState.set_boiler_lifespan,
                            suffix="jaar",
                            info="Verwachte levensduur in jaren.",
                        ),
                        input_field(
                            "Onderhoud/jr",
                            WarmWaterState.boiler_maintenance,
                            WarmWaterState.set_boiler_maintenance,
                            suffix="€",
                            info="Jaarlijkse onderhoudskosten.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    slider_input(
                        "Stilstandsverlies",
                        WarmWaterState.boiler_standby_loss,
                        WarmWaterState.set_boiler_standby_loss,
                        0,
                        2.0,
                        0.1,
                        suffix="kWh/dag",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=WarmWaterState.waterbatterij_enabled,
                            on_change=WarmWaterState.toggle_waterbatterij,
                            class_name="mr-3 w-5 h-5 text-blue-600 rounded focus:ring-blue-500 border-gray-300",
                        ),
                        "Gebruik 'Waterbatterij' (Slim Verwarmen met Zonnestroom)",
                        class_name="flex items-center text-sm font-medium text-gray-700 mt-2 p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors cursor-pointer",
                    ),
                    rx.cond(
                        WarmWaterState.waterbatterij_enabled,
                        rx.el.div(
                            slider_input(
                                "Maximaal verwarmingsvermogen",
                                WarmWaterState.boiler_heating_power,
                                WarmWaterState.set_boiler_heating_power,
                                0.5,
                                5.0,
                                0.1,
                                suffix="kW",
                            ),
                            class_name="mt-4 pl-4 border-l-2 border-blue-200",
                        ),
                    ),
                ),
                color_class="bg-blue-50",
                icon_color="text-blue-600",
            ),
            accordion_section(
                "Warmtepompboiler (A-Label)",
                "wind",
                WarmWaterState.section_wp_open,
                lambda: WarmWaterState.toggle_section("wp"),
                rx.el.div(
                    rx.el.div(
                        input_field(
                            "Aanschafprijs",
                            WarmWaterState.wpboiler_purchase_price,
                            WarmWaterState.set_wpboiler_purchase_price,
                            suffix="€",
                            key="wpboiler_price_"
                            + WarmWaterState.wpboiler_waterbatterij_enabled.to_string(),
                            info="Aanschafprijs inclusief installatie.",
                        ),
                        input_field(
                            "COP (Rendement)",
                            WarmWaterState.cop,
                            WarmWaterState.set_cop,
                            step="0.1",
                            info="Coefficient of Performance: rendement van de warmtepomp.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    rx.el.div(
                        input_field(
                            "Levensduur",
                            WarmWaterState.wpboiler_lifespan,
                            WarmWaterState.set_wpboiler_lifespan,
                            suffix="jaar",
                            info="Verwachte levensduur in jaren.",
                        ),
                        input_field(
                            "Onderhoud/jr",
                            WarmWaterState.wpboiler_maintenance,
                            WarmWaterState.set_wpboiler_maintenance,
                            suffix="€",
                            info="Jaarlijkse onderhoudskosten.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    slider_input(
                        "Stilstandsverlies",
                        WarmWaterState.wpboiler_standby_loss,
                        WarmWaterState.set_wpboiler_standby_loss,
                        0,
                        1.5,
                        0.1,
                        suffix="kWh/dag",
                    ),
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=WarmWaterState.wpboiler_waterbatterij_enabled,
                            on_change=WarmWaterState.toggle_wp_waterbatterij,
                            class_name="mr-3 w-5 h-5 text-green-600 rounded focus:ring-green-500 border-gray-300",
                        ),
                        "Gebruik 'Waterbatterij' (Slim Verwarmen met Zonnestroom)",
                        class_name="flex items-center text-sm font-medium text-gray-700 mt-2 p-3 bg-gray-50 rounded-lg border border-gray-100 hover:bg-gray-100 transition-colors cursor-pointer",
                    ),
                    rx.cond(
                        WarmWaterState.wpboiler_waterbatterij_enabled,
                        rx.el.div(
                            slider_input(
                                "Maximaal verwarmingsvermogen",
                                WarmWaterState.wpboiler_heating_power,
                                WarmWaterState.set_wpboiler_heating_power,
                                0.5,
                                5.0,
                                0.1,
                                suffix="kW",
                            ),
                            class_name="mt-4 pl-4 border-l-2 border-green-200",
                        ),
                    ),
                ),
                color_class="bg-green-50",
                icon_color="text-green-600",
            ),
            accordion_section(
                "Elektriciteitsprijs",
                "plug",
                WarmWaterState.section_price_open,
                lambda: WarmWaterState.toggle_section("price"),
                rx.el.div(
                    rx.el.div(
                        input_field(
                            "Stroomprijs",
                            WarmWaterState.electricity_price,
                            WarmWaterState.set_electricity_price,
                            step="0.01",
                            suffix="€/kWh",
                            info="Huidige elektriciteitsprijs per kWh.",
                        ),
                        input_field(
                            "Terugleververgoeding",
                            WarmWaterState.feedin_tariff,
                            WarmWaterState.set_feedin_tariff,
                            step="0.01",
                            suffix="€/kWh",
                            info="Vergoeding die u krijgt voor teruggeleverde zonnestroom.",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 gap-6",
                    ),
                    input_field(
                        "Beschikbaar Zonne-overschot",
                        WarmWaterState.annual_solar_surplus,
                        WarmWaterState.set_annual_solar_surplus,
                        suffix="kWh/jr",
                        info="Hoeveelheid zonnestroom die u jaarlijks overhoudt (netto teruglevering).",
                    ),
                ),
                color_class="bg-indigo-50",
                icon_color="text-indigo-600",
            ),
            rx.el.button(
                rx.cond(
                    WarmWaterState.is_processing,
                    rx.el.div(
                        rx.spinner(size="2", class_name="text-white mr-2"),
                        "Berekenen...",
                        class_name="flex items-center justify-center gap-2",
                    ),
                    "Bereken Kostenvergelijking",
                ),
                on_click=WarmWaterState.calculate_results,
                disabled=WarmWaterState.is_processing,
                class_name="w-full py-4 mt-6 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-200 disabled:opacity-70 text-lg",
            ),
            rx.el.p(
                WarmWaterState.rate_limit_status,
                class_name="text-xs text-gray-500 text-center mt-2",
            ),
            rx.cond(
                WarmWaterState.has_calculated,
                rx.el.div(
                    rx.el.h2(
                        "Resultaten",
                        class_name="text-2xl font-bold text-gray-900 mb-6 mt-12 text-center",
                    ),
                    waterbatterij_explanation(),
                    rx.el.div(
                        compact_result_card(
                            "Huidig (Gas)",
                            "flame",
                            "text-orange-500",
                            WarmWaterState.gas_total.to_string(),
                            WarmWaterState.cheapest_option == "Gas CV",
                        ),
                        compact_result_card(
                            "Elektrische Boiler",
                            "zap",
                            "text-blue-500",
                            WarmWaterState.boiler_total.to_string(),
                            WarmWaterState.cheapest_option == "Elektrische Boiler",
                        ),
                        compact_result_card(
                            "Warmtepompboiler",
                            "wind",
                            "text-emerald-500",
                            WarmWaterState.wp_total.to_string(),
                            WarmWaterState.cheapest_option == "Warmtepompboiler",
                            is_wp=True,
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8",
                    ),
                    rx.el.div(
                        comparison_bar_chart(),
                        comparison_table(),
                        class_name="flex flex-col gap-8 mb-12",
                    ),
                    rx.cond(
                        WarmWaterState.is_authenticated,
                        rx.el.div(
                            rx.el.button(
                                rx.cond(
                                    WarmWaterState.is_sending_email,
                                    rx.el.div(
                                        rx.spinner(
                                            size="2", class_name="text-white mr-2"
                                        ),
                                        "Verzenden...",
                                        class_name="flex items-center",
                                    ),
                                    rx.el.div(
                                        rx.icon("mail", class_name="w-5 h-5 mr-2"),
                                        "E-mail Resultaten",
                                        class_name="flex items-center",
                                    ),
                                ),
                                on_click=WarmWaterState.email_results,
                                disabled=WarmWaterState.is_sending_email,
                                class_name="flex items-center justify-center px-6 py-3 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-colors shadow-md hover:shadow-lg disabled:opacity-70",
                            ),
                            class_name="flex justify-center",
                        ),
                    ),
                    class_name="animate-in fade-in slide-in-from-bottom-4 duration-700",
                ),
            ),
            technical_details_section(),
            email_confirmation_modal(
                WarmWaterState.email_sent_modal_open, WarmWaterState.close_email_modal
            ),
            class_name="max-w-3xl mx-auto",
        ),
        class_name="flex-1",
    )


def warm_water_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.title(
                "Warm Water Kosten Vergelijken | Gas vs Boiler vs Warmtepomp | Volta Optima"
            ),
            rx.el.meta(
                name="description",
                content="Vergelijk de kosten van gas, elektrische boilers en warmtepompboilers. Ontdek hoeveel u kunt besparen door slim gebruik te maken van uw zonnestroom.",
            ),
            json_ld_script(
                software_application_schema(
                    name="Warm Water Kosten Vergelijker",
                    description="Vergelijk energiekosten voor warm water bereiding: CV-ketel, elektrische boiler en warmtepompboiler.",
                    url="/tools/warm-water",
                )
            ),
            json_ld_script(
                breadcrumb_schema(
                    [
                        ("Home", "/"),
                        ("Tools", "/tools"),
                        ("Warm Water Scan", "/tools/warm-water"),
                    ]
                )
            ),
            advice_sidebar(),
            rx.el.div(warm_water_content(), class_name="flex-1 p-6 md:p-8"),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
            on_mount=WarmWaterState.load_page_content,
        )
    )