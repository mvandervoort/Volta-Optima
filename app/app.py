import reflex as rx
from app.pages.home import home_page
from app.pages.solar_yield import solar_yield_page
from app.pages.login import login_page
from app.pages.forgot_password import forgot_password_page
from app.pages.context import context_page
from app.pages.faq import faq_page
from app.pages.advice_themes import advice_themes_page
from app.pages.blog import blog_page
from app.pages.contact_about import contact_about_page
from app.pages.signup import signup_page
from app.pages.kb import kb_overview_page, article_page
from app.pages.wiki_intro import wiki_intro_page
from app.pages.battery_estimator import battery_estimator_page
from app.pages.advanced_battery_calc import advanced_battery_calc_page
from app.pages.dakscan import dakscan_page
from app.pages.admin.dashboard import admin_dashboard_page
from app.pages.results import results_page
from app.pages.advice_theme_solar import advice_theme_solar_page
from app.pages.warm_water import warm_water_page
from app.states.base_state import State
from app.states.cms_content_state import CMSContentState
from app.states.context_cms_state import ContextCMSState
from app.states.kb_state import KnowledgeBaseState
from app.pages.about import about_page
from app.utils.seo import generate_meta_tags
from app.constants import BASE_URL
from app.api.sitemap import sitemap_endpoint, robots_endpoint
from app.components.google_analytics import google_analytics_scripts


def api_routes(api):
    api.add_route("/sitemap.xml", sitemap_endpoint)
    api.add_route("/robots.txt", robots_endpoint)
    return api


app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(rel="preconnect", href="https://fonts.gstatic.com", cross_origin=""),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ]
    + google_analytics_scripts(),
    api_transformer=api_routes,
    stylesheets=["/styles/global.css"],
)
DEFAULT_IMAGE = "/og-image.png"
app.add_page(
    home_page,
    route="/",
    title="Energie Insight - Datagestuurd Energieadvies",
    description="Optimaliseer uw energieverbruik na de salderingsregeling. Bereken rendementen voor zonnepanelen, batterijen en warm water systemen.",
    meta=generate_meta_tags(
        "Energie Insight - Datagestuurd Energieadvies",
        "Optimaliseer uw energieverbruik na de salderingsregeling. Bereken rendementen voor zonnepanelen, batterijen en warm water systemen.",
        DEFAULT_IMAGE,
        "/",
    ),
)
app.add_page(
    context_page,
    route="/aanleiding",
    on_load=ContextCMSState.on_load,
    title="De Aanleiding - Energietransitie Uitdagingen | Energie Insight",
    description="Waarom nu handelen? De afbouw van de salderingsregeling en de impact op uw zonnepanelen rendement.",
    meta=generate_meta_tags(
        "De Aanleiding - Energietransitie Uitdagingen | Energie Insight",
        "Waarom nu handelen? De afbouw van de salderingsregeling en de impact op uw zonnepanelen rendement.",
        DEFAULT_IMAGE,
        "/aanleiding",
    ),
)
app.add_page(faq_page, route="/faq")
app.add_page(
    solar_yield_page,
    route="/solar",
    title="Zonnepanelen Opbrengst Calculator | Energie Insight",
    description="Bereken de werkelijke opbrengst en terugverdientijd van uw zonnepanelen met onze PVWatts-gebaseerde calculator.",
    meta=generate_meta_tags(
        "Zonnepanelen Opbrengst Calculator | Energie Insight",
        "Bereken de werkelijke opbrengst en terugverdientijd van uw zonnepanelen met onze PVWatts-gebaseerde calculator.",
        DEFAULT_IMAGE,
        "/solar",
    ),
)
app.add_page(
    advice_themes_page,
    route="/advice-themes",
    title="Adviesmodules & Rekentools | Energie Insight",
    description="Overzicht van al onze energie-adviesmodules: Zonne-energie, Batterijen en Warm Water.",
    meta=generate_meta_tags(
        "Adviesmodules & Rekentools | Energie Insight",
        "Overzicht van al onze energie-adviesmodules: Zonne-energie, Batterijen en Warm Water.",
        DEFAULT_IMAGE,
        "/advice-themes",
    ),
)
app.add_page(
    battery_estimator_page,
    route="/battery",
    title="Thuisbatterij Calculator | Energie Insight",
    description="Is een thuisbatterij rendabel? Bereken uw terugverdientijd en optimale capaciteit.",
    meta=generate_meta_tags(
        "Thuisbatterij Calculator | Energie Insight",
        "Is een thuisbatterij rendabel? Bereken uw terugverdientijd en optimale capaciteit.",
        DEFAULT_IMAGE,
        "/battery",
    ),
)
from app.pages.simple_battery import simple_battery_page
from app.pages.contract_comparison import contract_comparison_page

app.add_page(
    simple_battery_page,
    route="/advice/simple/battery",
    title="Eenvoudige Batterij Scan | Energie Insight",
    description="Snelle berekening voor batterijopslag potentieel op basis van jaarverbruik.",
    meta=generate_meta_tags(
        "Eenvoudige Batterij Scan | Energie Insight",
        "Snelle berekening voor batterijopslag potentieel op basis van jaarverbruik.",
        DEFAULT_IMAGE,
        "/advice/simple/battery",
    ),
)
app.add_page(
    lambda: protected_guard(advanced_battery_calc_page(), requires_auth=True),
    route="/advice/advanced/battery",
    title="Geavanceerde Batterij Simulatie | Energie Insight",
    description="Professionele simulatie met uurdata uploads voor nauwkeurig batterij-advies.",
    meta=generate_meta_tags(
        "Geavanceerde Batterij Simulatie | Energie Insight",
        "Professionele simulatie met uurdata uploads voor nauwkeurig batterij-advies.",
        DEFAULT_IMAGE,
        "/advice/advanced/battery",
    ),
)
app.add_page(
    lambda: protected_guard(dakscan_page(), requires_auth=True),
    route="/dakscan",
    title="Dakscan - Zonnepotentieel Analyse | Energie Insight",
    description="Analyseer het zonnepotentieel van uw dak met Google Solar AI.",
    meta=generate_meta_tags(
        "Dakscan - Zonnepotentieel Analyse | Energie Insight",
        "Analyseer het zonnepotentieel van uw dak met Google Solar AI.",
        DEFAULT_IMAGE,
        "/dakscan",
    ),
)
app.add_page(
    advice_theme_solar_page,
    route="/advice/solar-theme",
    title="Zonne-energie Advies | Energie Insight",
    description="Alles over zonne-energie: van installatie tot optimalisatie van uw opbrengst.",
    meta=generate_meta_tags(
        "Zonne-energie Advies | Energie Insight",
        "Alles over zonne-energie: van installatie tot optimalisatie van uw opbrengst.",
        DEFAULT_IMAGE,
        "/advice/solar-theme",
    ),
)
app.add_page(
    warm_water_page,
    route="/warm-water",
    title="Warmwater Warmtepomp Calculator | Energie Insight",
    description="Vergelijk kosten van Gas, Elektrische Boiler en Warmtepompboiler met onze calculator.",
    meta=generate_meta_tags(
        "Warmwater Warmtepomp Calculator | Energie Insight",
        "Vergelijk kosten van Gas, Elektrische Boiler en Warmtepompboiler met onze calculator.",
        DEFAULT_IMAGE,
        "/warm-water",
    ),
)
from app.components.protected_guard import protected_guard
from app.states.results_state import ResultsState

app.add_page(
    lambda: protected_guard(results_page(), requires_auth=True),
    route="/results",
    on_load=ResultsState.load_user_results,
    title="Mijn Resultaten | Energie Insight",
    description="Bekijk uw opgeslagen berekeningen en energie-adviezen.",
    meta=generate_meta_tags(
        "Mijn Resultaten | Energie Insight",
        "Bekijk uw opgeslagen berekeningen en energie-adviezen.",
        DEFAULT_IMAGE,
        "/results",
    ),
)
app.add_page(
    kb_overview_page,
    route="/kb",
    on_load=KnowledgeBaseState.load_articles,
    title="Kennisbank - Energie Transitie Wiki | Energie Insight",
    description="Uitgebreide kennisbank over zonnepanelen, batterijen, wetgeving en energietechniek.",
    meta=generate_meta_tags(
        "Kennisbank - Energie Transitie Wiki | Energie Insight",
        "Uitgebreide kennisbank over zonnepanelen, batterijen, wetgeving en energietechniek.",
        DEFAULT_IMAGE,
        "/kb",
    ),
)
app.add_page(
    article_page,
    route="/kb/[article_id]",
    on_load=KnowledgeBaseState.load_articles,
    title=KnowledgeBaseState.current_article["title"].to(str),
    meta=generate_meta_tags(
        KnowledgeBaseState.current_article["title"].to(str),
        KnowledgeBaseState.current_article["excerpt"].to(str),
        DEFAULT_IMAGE,
        "/kb/" + KnowledgeBaseState.current_article["id"].to(str),
    ),
)
app.add_page(wiki_intro_page, route="/wiki")
from app.pages.blog import blog_page, blog_post_page
from app.states.blog_state import BlogState

app.add_page(
    blog_page,
    route="/blog",
    on_load=BlogState.load_posts,
    title="Blog & Nieuws - Energie Insight",
    description="Laatste nieuws en inzichten over de energiemarkt en duurzame technologie.",
    meta=generate_meta_tags(
        "Blog & Nieuws - Energie Insight",
        "Laatste nieuws en inzichten over de energiemarkt en duurzame technologie.",
        DEFAULT_IMAGE,
        "/blog",
    ),
)
app.add_page(
    blog_post_page,
    route="/blog/[slug]",
    on_load=BlogState.load_current_post,
    title=BlogState.current_post["title"].to(str),
    meta=generate_meta_tags(
        BlogState.current_post["title"].to(str),
        BlogState.current_post["excerpt"].to(str),
        DEFAULT_IMAGE,
        "/blog/" + BlogState.current_post["slug"].to(str),
    ),
)
app.add_page(
    contact_about_page,
    route="/contact-about",
    title="Contact & Over Ons | Energie Insight",
    description="Neem contact op met Energie Insight of leer meer over onze missie.",
    meta=generate_meta_tags(
        "Contact & Over Ons | Energie Insight",
        "Neem contact op met Energie Insight of leer meer over onze missie.",
        DEFAULT_IMAGE,
        "/contact-about",
    ),
)
app.add_page(
    about_page,
    route="/about",
    on_load=lambda: CMSContentState.get_content("about-us"),
    title="Over Ons | Energie Insight",
    description="Leer meer over Energie Insight.",
    meta=generate_meta_tags(
        "Over Ons | Energie Insight",
        "Leer meer over Energie Insight.",
        DEFAULT_IMAGE,
        "/about",
    ),
)
from app.pages.terms import terms_page

app.add_page(
    terms_page,
    route="/algemene-voorwaarden",
    on_load=lambda: CMSContentState.get_content("algemene-voorwaarden"),
    title="Algemene Voorwaarden | Energie Insight",
    description="Onze algemene voorwaarden.",
    meta=generate_meta_tags(
        "Algemene Voorwaarden | Energie Insight",
        "Onze algemene voorwaarden.",
        DEFAULT_IMAGE,
        "/algemene-voorwaarden",
    ),
)
from app.pages.privacy import privacy_page

app.add_page(
    privacy_page,
    route="/privacybeleid",
    on_load=lambda: CMSContentState.get_content("privacybeleid"),
    title="Privacybeleid | Energie Insight",
    description="Ons privacybeleid.",
    meta=generate_meta_tags(
        "Privacybeleid | Energie Insight",
        "Ons privacybeleid.",
        DEFAULT_IMAGE,
        "/privacybeleid",
    ),
)
app.add_page(
    login_page,
    route="/login",
    title="Inloggen | Energie Insight",
    meta=generate_meta_tags(
        "Inloggen - Energie Insight",
        "Log in op uw Energie Insight account voor persoonlijk energieadvies.",
        DEFAULT_IMAGE,
        "/login",
    ),
)
app.add_page(
    forgot_password_page,
    route="/forgot-password",
    title="Wachtwoord Vergeten | Energie Insight",
    meta=generate_meta_tags(
        "Wachtwoord Vergeten - Energie Insight",
        "Herstel uw wachtwoord voor toegang tot Energie Insight.",
        DEFAULT_IMAGE,
        "/forgot-password",
    ),
)
from app.pages.reset_password import reset_password_page

app.add_page(
    reset_password_page,
    route="/reset-password",
    title="Reset Wachtwoord | Energie Insight",
    meta=generate_meta_tags(
        "Reset Wachtwoord - Energie Insight",
        "Stel een nieuw wachtwoord in voor uw Energie Insight account.",
        DEFAULT_IMAGE,
        "/reset-password",
    ),
)
app.add_page(
    signup_page,
    route="/signup",
    title="Registreren | Energie Insight",
    meta=generate_meta_tags(
        "Registreren - Energie Insight",
        "Maak een account aan voor persoonlijk energieadvies.",
        DEFAULT_IMAGE,
        "/signup",
    ),
)
app.add_page(
    admin_dashboard_page,
    route="/admin",
    title="Admin Dashboard | Energie Insight",
    meta=generate_meta_tags(
        "Admin Dashboard - Energie Insight",
        "Beheerdersdashboard voor content en instellingen.",
        DEFAULT_IMAGE,
        "/admin",
    ),
)
from app.pages.admin.cms_list import cms_list_page
from app.pages.admin.cms_editor import cms_editor_page
from app.states.cms_list_state import CMSListState
from app.states.cms_edit_state import CMSEditState
from app.pages.admin.categories import categories_page
from app.states.category_state import CategoryState
from app.pages.admin.users import admin_users_page
from app.pages.admin.settings import admin_settings_page
from app.states.admin_settings_state import AdminSettingsState
from app.pages.admin.analytics import analytics_page
from app.states.admin_analytics_state import AdminAnalyticsState

app.add_page(cms_list_page, route="/admin/cms", on_load=CMSListState.on_load)
app.add_page(
    cms_editor_page, route="/admin/cms/editor/[id]", on_load=CMSEditState.on_load
)
app.add_page(categories_page, route="/admin/categories", on_load=CategoryState.on_load)
app.add_page(admin_users_page, route="/admin/users")
app.add_page(
    admin_settings_page, route="/admin/settings", on_load=AdminSettingsState.on_load
)
app.add_page(
    analytics_page, route="/admin/analytics", on_load=AdminAnalyticsState.load_analytics
)
app.add_page(
    contract_comparison_page,
    route="/advice/contract-vergelijking",
    title="Vergelijk Energiecontracten | Energie Insight",
    description="Vergelijk vast, variabel en dynamische energiecontracten en ontdek welk type contract het beste past bij uw verbruik en zonnepanelen.",
    meta=generate_meta_tags(
        "Vergelijk Energiecontracten | Energie Insight",
        "Vergelijk vast, variabel en dynamische energiecontracten en ontdek welk type contract het beste past bij uw verbruik en zonnepanelen.",
        DEFAULT_IMAGE,
        "/advice/contract-vergelijking",
    ),
)