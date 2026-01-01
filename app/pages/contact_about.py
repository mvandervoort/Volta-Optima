import reflex as rx
from app.components.layout import base_layout
from app.states.contact_state import ContactState
from app.components.email_confirmation_modal import email_confirmation_modal


def contact_form() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Neem Contact Op", class_name="text-2xl font-bold text-gray-900 mb-6"),
        rx.el.div(
            rx.el.label("Website", html_for="website_url_honey", class_name="hidden"),
            rx.el.input(
                id="website_url_honey",
                type="text",
                name="website_url",
                on_change=ContactState.set_website_url,
                default_value=ContactState.website_url,
                tab_index=-1,
                auto_complete="off",
                class_name="opacity-0 absolute left-[-9999px] top-0 h-0 w-0 z-[-1]",
            ),
            class_name="absolute opacity-0 h-0 w-0 overflow-hidden",
            aria_hidden="true",
        ),
        rx.el.div(
            rx.el.label(
                "Naam", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                on_change=[ContactState.set_name, ContactState.mark_form_loaded],
                on_focus=ContactState.ensure_form_loaded,
                class_name="w-full rounded-lg border-gray-300 border px-4 py-2 focus:ring-2 focus:ring-emerald-500 outline-none",
                default_value=ContactState.name,
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "E-mail", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.input(
                type="email",
                on_change=[ContactState.set_email, ContactState.mark_form_loaded],
                on_focus=ContactState.ensure_form_loaded,
                class_name="w-full rounded-lg border-gray-300 border px-4 py-2 focus:ring-2 focus:ring-emerald-500 outline-none",
                default_value=ContactState.email,
            ),
            class_name="mb-4",
        ),
        rx.el.div(
            rx.el.label(
                "Bericht", class_name="block text-sm font-medium text-gray-700 mb-1"
            ),
            rx.el.textarea(
                on_change=[ContactState.set_message, ContactState.mark_form_loaded],
                on_focus=ContactState.ensure_form_loaded,
                class_name="w-full rounded-lg border-gray-300 border px-4 py-2 h-32 resize-none focus:ring-2 focus:ring-emerald-500 outline-none",
                default_value=ContactState.message,
            ),
            class_name="mb-6",
        ),
        rx.el.button(
            rx.cond(ContactState.loading, "Verzenden...", "Verstuur Bericht"),
            on_click=ContactState.send_message,
            disabled=ContactState.loading,
            class_name="w-full bg-emerald-600 text-white py-3 rounded-lg hover:bg-emerald-700 transition-colors font-medium disabled:opacity-70",
        ),
        class_name="bg-white p-8 rounded-xl border border-gray-100 shadow-sm h-fit",
    )


def contact_item(icon: str, label: str, value: str, href: str = None) -> rx.Component:
    content = rx.el.div(
        rx.el.div(
            rx.icon(icon, class_name="w-5 h-5 text-emerald-600"),
            class_name="w-10 h-10 rounded-full bg-emerald-50 flex items-center justify-center mr-4 shrink-0",
        ),
        rx.el.div(
            rx.el.p(
                label,
                class_name="text-xs font-semibold text-gray-500 uppercase tracking-wider",
            ),
            rx.el.p(value, class_name="text-gray-900 font-medium"),
        ),
        class_name="flex items-center",
    )
    if href:
        return rx.el.a(
            content,
            href=href,
            class_name="block p-3 hover:bg-gray-50 rounded-xl transition-colors -mx-3",
        )
    return rx.el.div(content, class_name="p-3 -mx-3")


def team_member_card(
    name: str, title: str, email: str = "", linkedin: str = ""
) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon("user", class_name="w-8 h-8 text-emerald-600"),
                class_name="w-16 h-16 rounded-full bg-emerald-50 flex items-center justify-center shrink-0",
            ),
            rx.el.div(
                rx.el.h4(name, class_name="text-lg font-bold text-gray-900"),
                rx.el.p(title, class_name="text-sm text-emerald-600 font-medium"),
                rx.el.div(
                    rx.cond(
                        linkedin != "",
                        rx.el.a(
                            rx.icon("linkedin", class_name="w-4 h-4"),
                            href=linkedin,
                            target="_blank",
                            class_name="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-md transition-all",
                        ),
                    ),
                    rx.cond(
                        email != "",
                        rx.el.a(
                            rx.icon("mail", class_name="w-4 h-4"),
                            href=f"mailto:{email}",
                            class_name="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded-md transition-all",
                        ),
                    ),
                    class_name="flex gap-2 mt-2",
                ),
                class_name="flex-1",
            ),
            class_name="flex gap-4 items-center",
        ),
        class_name="bg-white p-5 rounded-2xl border border-gray-100 shadow-sm hover:shadow-md transition-shadow",
    )


def about_section() -> rx.Component:
    return rx.el.div(
        rx.el.h2("Over Ons", class_name="text-2xl font-bold text-gray-900 mb-6"),
        rx.el.img(
            src="/full_trimmed_transparent_customcolor.png",
            alt="Energie Insight Logo",
            class_name="w-full max-w-[300px] h-auto mb-8 mx-auto",
        ),
        rx.el.div(
            rx.el.p(
                "Energie Insight is toegewijd aan het versnellen van de energietransitie door huiseigenaren te voorzien van nauwkeurige, datagestuurde inzichten.",
                class_name="text-gray-600 mb-4 leading-relaxed",
            ),
            rx.el.p(
                "Onze missie is om complexe energiemarktdata toegankelijk en begrijpelijk te maken, zodat u de beste beslissingen kunt nemen voor uw duurzame toekomst.",
                class_name="text-gray-600 mb-10 leading-relaxed",
            ),
            rx.el.div(
                rx.el.h3("Ons Team", class_name="text-lg font-bold text-gray-900 mb-4"),
                rx.el.div(
                    team_member_card(
                        "Manfred van der Voort",
                        "initiatiefnemer",
                        email="m.vandervoort@energie-insight.nl",
                        linkedin="https://www.linkedin.com/in/manfredvandervoort/",
                    ),
                    team_member_card("Rob van Bokkem", "mede-initiatiefnemer"),
                    class_name="space-y-4 mb-10",
                ),
            ),
            rx.el.div(
                rx.el.h3(
                    "Contactgegevens", class_name="text-lg font-bold text-gray-900 mb-4"
                ),
                rx.el.div(
                    contact_item("building", "Adres", "Hoofdkwartier 86, 6711 WW Ede"),
                    contact_item(
                        "mail",
                        "E-mail",
                        "info@energie-insight.nl",
                        href="mailto:info@energie-insight.nl",
                    ),
                    contact_item(
                        "phone",
                        "Telefoon",
                        "+31 (0)6 23368673",
                        href="tel:+31623368673",
                    ),
                    contact_item("file-text", "KVK Nummer", "98811835"),
                    class_name="space-y-1 bg-white rounded-2xl border border-gray-100 p-6 shadow-sm",
                ),
            ),
        ),
    )


def contact_about_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Contact & Over Ons",
                    class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-12 text-center",
                ),
                rx.el.div(
                    contact_form(),
                    about_section(),
                    class_name="grid grid-cols-1 lg:grid-cols-2 gap-12 max-w-6xl mx-auto items-start",
                ),
            ),
            email_confirmation_modal(
                ContactState.email_sent_modal_open, ContactState.close_email_modal
            ),
            class_name="container mx-auto px-4 py-12",
        )
    )