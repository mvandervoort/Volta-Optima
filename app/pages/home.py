import reflex as rx
from app.components.layout import base_layout
from app.components.seo import json_ld
from app.utils.seo import organization_schema, webpage_schema


def info_card(title: str, description: str, icon: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-teal-600"),
            class_name="h-12 w-12 bg-teal-50 rounded-lg flex items-center justify-center mb-6",
        ),
        rx.el.h3(title, class_name="text-xl font-bold text-gray-900 mb-3"),
        rx.el.p(description, class_name="text-gray-600 text-sm leading-relaxed"),
        class_name="bg-white p-8 rounded-2xl border border-gray-100 shadow-sm h-full",
    )


def beta_badge() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon("flask-conical", class_name="w-6 h-6 text-amber-900/80 mb-0.5"),
            rx.el.span(
                "Nu nog",
                class_name="text-[11px] font-bold uppercase tracking-wider text-amber-800 leading-none mb-0.5",
            ),
            rx.el.span(
                "BETA",
                class_name="text-xl font-black tracking-widest text-amber-950 leading-none",
            ),
            class_name="flex flex-col items-center",
        ),
        title="Dit platform is in actieve ontwikkeling",
        class_name="fixed bottom-6 right-6 z-50 bg-gradient-to-br from-amber-300 to-amber-500 w-[120px] h-[120px] rounded-full shadow-[0_8px_30px_rgb(0,0,0,0.12)] border-[5px] border-white flex items-center justify-center transform rotate-12 hover:rotate-6 hover:scale-105 transition-all duration-300 ease-out cursor-default select-none animate-in fade-in zoom-in duration-700",
    )


def home_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            json_ld(organization_schema()),
            json_ld(
                webpage_schema(
                    "Volta Optima - Datagestuurd Energieadvies",
                    "Optimaliseer uw energieverbruik en rendement na de salderingsregeling met onze geavanceerde calculators.",
                    "/",
                )
            ),
            beta_badge(),
            rx.el.section(
                rx.el.div(
                    rx.el.img(
                        src="/full_trimmed_transparent_customcolor.png",
                        alt="Energie Insight - Advies Platform Energie Transitie",
                        class_name="mx-auto w-[480px] h-auto mb-6",
                    ),
                    rx.el.h1(
                        rx.el.span(
                            "De salderings\xadregeling voorbij,", class_name="block"
                        ),
                        rx.el.span(
                            "met ",
                            rx.el.span(
                                "(berekend)",
                                class_name="font-semibold italic text-gray-500",
                            ),
                            " ",
                            rx.el.span("Vertrouwen", class_name="text-teal-600"),
                            class_name="block mt-2 md:mt-4",
                        ),
                        class_name="hero-headline text-2xl sm:text-4xl md:text-5xl lg:text-6xl font-extrabold text-gray-900 mb-8 leading-tight tracking-tight px-4 sm:px-6 w-full mx-auto",
                    ),
                    rx.el.p(
                        "Het energielandschap verandert. De salderingsregeling wordt afgebouwd, maar uw besparingen hoeven dat niet te zijn. Energie Insight helpt u door de transitie met datagestuurd advies op maat voor Nederlandse huiseigenaren en klein MKB.",
                        class_name="text-xl text-gray-600 mb-10 max-w-2xl mx-auto leading-relaxed px-4",
                    ),
                    rx.el.div(
                        rx.el.a(
                            "Start Adviesmodule",
                            href="/advice-themes",
                            class_name="px-8 py-4 bg-teal-600 text-white rounded-full hover:bg-teal-700 transition-all font-semibold shadow-lg hover:shadow-teal-200/50 hover:-translate-y-0.5",
                        ),
                        rx.el.a(
                            "Meer Informatie",
                            href="/aanleiding",
                            class_name="px-8 py-4 bg-white text-gray-900 border border-gray-200 rounded-full hover:bg-gray-50 hover:border-gray-300 transition-all font-semibold shadow-sm hover:shadow-md hover:-translate-y-0.5",
                        ),
                        class_name="flex flex-col sm:flex-row gap-4 justify-center",
                    ),
                    class_name="container mx-auto px-4 py-10 md:py-16 text-center",
                ),
                class_name="bg-white border-b border-gray-100",
            ),
            rx.el.section(
                rx.el.div(
                    rx.el.h2(
                        "Waarom Nu?",
                        class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-6 text-left",
                    ),
                    rx.el.p(
                        "De aanstaande wijzigingen in de salderingsregeling betekenen dat het terugleveren van zonne-energie aan het net minder winstgevend wordt. Het is tijd om uw eigen verbruik te optimaliseren.",
                        class_name="text-lg text-gray-600 max-w-3xl mb-16 leading-relaxed text-center mx-auto",
                    ),
                    rx.el.div(
                        info_card(
                            "Dalende Terugleververgoeding",
                            "Terugleveren is minder rendabel dan voorheen. Ontdek hoeveel u mogelijk misloopt en wat u eraan kunt doen.",
                            "trending-down",
                        ),
                        info_card(
                            "Eigen Verbruik",
                            "Het doel is maximalisatie van eigen verbruik. Wij laten zien hoe u uw zonnestroom direct kunt benutten.",
                            "zap",
                        ),
                        info_card(
                            "Opslagoplossingen",
                            "Is een thuisbatterij rendabel voor u? Wij analyseren de terugverdientijd op basis van uw persoonlijke profiel.",
                            "battery-charging",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-3 gap-8",
                    ),
                    class_name="container mx-auto px-6 md:px-8 py-20",
                ),
                class_name="bg-gray-50 w-full",
            ),
        )
    )