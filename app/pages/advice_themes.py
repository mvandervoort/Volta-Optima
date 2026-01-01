import reflex as rx
from app.components.layout import base_layout
from app.components.advice_sidebar import advice_sidebar

TOOLS = [
    {
        "title": "Dakscan - Zonnepotentieel",
        "description": "Analyseer het zonnepotentieel van uw dak met Google Solar AI.",
        "url": "/dakscan",
        "icon": "layout-grid",
        "requires_auth": True,
    },
    {
        "title": "Zonneopbrengst Calculator",
        "description": "Schat de jaarlijkse productie en financiële rendementen op basis van uw dakkenmerken.",
        "url": "/solar",
        "icon": "sun",
        "requires_auth": False,
    },
    {
        "title": "Eenvoudige Batterij Berekening",
        "description": "Snelle en eenvoudige berekening van de batterijgrootte voor uw huis.",
        "url": "/advice/simple/battery",
        "icon": "zap",
        "requires_auth": False,
    },
    {
        "title": "Verbeterde Thuisbatterij Berekening",
        "description": "Snelle check of een thuisbatterij financieel zinvol is voor u, gebruikmakend van prijsgegevens uit 2024.",
        "url": "/battery",
        "icon": "battery-charging",
        "requires_auth": False,
    },
    {
        "title": "Geavanceerde Batterijsimulatie",
        "description": "Upload uurgegevens voor een professionele simulatie met dynamische prijzen.",
        "url": "/advice/advanced/battery",
        "icon": "activity",
        "requires_auth": True,
    },
    {
        "title": "Warmwater Calculator",
        "description": "Vergelijk kosten van gasketel, elektrische boiler en warmtepompboiler, inclusief slimme zonne-integratie.",
        "url": "/warm-water",
        "icon": "droplet",
        "icon": "droplet",
        "requires_auth": False,
    },
    {
        "title": "Vergelijk Soort Contracten",
        "description": "Ontdek welke contractvorm (vast, variabel of dynamisch) op dit moment financieel het meest aantrekkelijk is voor uw profiel.",
        "url": "/advice/contract-vergelijking",
        "icon": "scale",
        "requires_auth": False,
        "coming_soon": True,
    },
]


def tool_card(tool: dict) -> rx.Component:
    """Renders a card for a specific tool."""
    return rx.el.a(
        rx.cond(
            tool["requires_auth"],
            rx.tooltip(
                rx.el.div(
                    rx.icon("lock", class_name="w-4 h-4 text-amber-600"),
                    class_name="absolute top-4 right-4 p-2 bg-amber-50 rounded-full border border-amber-100 shadow-sm z-10",
                ),
                content="Inloggen vereist voor deze tool",
            ),
        ),
        rx.el.div(
            rx.cond(
                tool.get("coming_soon"),
                rx.el.span(
                    "Binnenkort",
                    class_name="absolute top-4 right-4 bg-violet-100 text-violet-700 px-2 py-1 rounded text-[10px] font-bold uppercase tracking-wider",
                ),
            ),
            rx.el.div(
                rx.icon(
                    tool["icon"],
                    class_name=f"w-8 h-8 {rx.cond(tool.get('coming_soon'), 'text-violet-600', 'text-teal-600')}",
                ),
                class_name=f"w-14 h-14 rounded-xl {rx.cond(tool.get('coming_soon'), 'bg-violet-50', 'bg-teal-50')} flex items-center justify-center mb-6",
            ),
            rx.el.h3(tool["title"], class_name="text-xl font-bold text-gray-900 mb-3"),
            rx.el.p(
                tool["description"],
                class_name="text-gray-600 mb-6 flex-1 leading-relaxed",
            ),
            rx.el.div(
                rx.el.span(
                    "Start Hulpmiddel",
                    class_name="font-semibold text-teal-600 group-hover:text-teal-700",
                ),
                rx.icon(
                    "arrow-right",
                    class_name="w-4 h-4 text-teal-600 ml-2 group-hover:translate-x-1 transition-transform",
                ),
                class_name="flex items-center mt-auto",
            ),
            class_name="flex flex-col h-full",
        ),
        href=tool["url"],
        class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md hover:border-teal-100 transition-all group h-full block relative",
    )


def advice_themes_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            advice_sidebar(),
            rx.el.div(
                rx.el.h1(
                    "Energietransitie Hulpmiddelen",
                    class_name="text-3xl font-bold text-gray-900 mb-4",
                ),
                rx.el.p(
                    "Krijg toegang tot onze reeks rekentools die zijn ontworpen om u te helpen weloverwogen beslissingen te nemen over zonne-energie en batterijopslag.",
                    class_name="text-gray-600 mb-12 max-w-2xl",
                ),
                rx.el.div(
                    *[tool_card(tool) for tool in TOOLS],
                    class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6",
                ),
                class_name="flex-1 py-10 px-6 md:px-12",
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
        )
    )