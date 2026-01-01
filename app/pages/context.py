import reflex as rx
from app.components.layout import base_layout
from app.states.context_page_state import ContextPageState
from app.states.context_cms_state import ContextCMSState


def faq_item(item: dict[str, str]) -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            item["question"],
            class_name="cursor-pointer font-medium text-gray-900 p-4 bg-gray-50 hover:bg-gray-100 rounded-lg mb-2 transition-colors list-none flex justify-between items-center select-none",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.style("""
                    .faq-fix .cms-content * {
                        text-align: left !important;
                        word-break: normal !important;
                        overflow-wrap: break-word !important;
                        white-space: normal !important;
                        hyphens: none !important;
                        -webkit-hyphens: none !important;
                    }
                    """),
                rx.html(item["answer"], class_name="cms-content"),
                class_name="prose prose-sm prose-emerald max-w-3xl faq-fix prose-p:text-left prose-p:mb-4 prose-li:text-left prose-li:mb-1",
            ),
            class_name="p-6 text-gray-600 bg-white border border-gray-100 rounded-lg mb-4 leading-relaxed text-left break-words",
        ),
        class_name="group",
    )


def sidebar_item(text: str, section_id: str) -> rx.Component:
    is_active = ContextPageState.active_section == section_id
    return rx.el.a(
        rx.el.div(
            class_name=rx.cond(
                is_active,
                "w-1 h-6 bg-teal-600 rounded-full mr-3",
                "w-1 h-6 bg-transparent rounded-full mr-3",
            )
        ),
        text,
        href=f"#{section_id}",
        on_click=lambda: ContextPageState.set_active_section(section_id),
        class_name=rx.cond(
            is_active,
            "flex items-center px-3 py-2 text-sm font-medium text-teal-900 bg-teal-50 rounded-md mb-1 cursor-pointer hover:bg-teal-100 transition-colors",
            "flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md cursor-pointer transition-colors",
        ),
    )


def context_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.h3(
                "AANLEIDING",
                class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
            ),
            rx.el.nav(
                sidebar_item("De Uitdaging", "the-challenge"),
                sidebar_item("Veelgestelde Vragen", "faq"),
                class_name="space-y-1",
            ),
            class_name="py-6 pr-6",
        ),
        class_name="hidden md:block w-64 shrink-0 border-r border-gray-200 min-h-[calc(100vh-5rem)] sticky top-20 self-start",
    )


def context_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            context_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.cond(
                        ContextCMSState.is_loading,
                        rx.el.div(
                            rx.spinner(class_name="w-8 h-8 text-teal-600"),
                            class_name="flex justify-center py-12",
                        ),
                        rx.el.div(
                            rx.el.h1(
                                ContextCMSState.challenge_title,
                                class_name="text-3xl md:text-4xl font-extrabold text-gray-900 mb-8 border-b border-gray-100 pb-4",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.html(
                                        ContextCMSState.challenge_content,
                                        class_name="prose prose-lg prose-emerald w-full max-w-none",
                                        style={
                                            "display": "block",
                                            "textAlign": "left",
                                            "wordBreak": "normal",
                                            "overflowWrap": "break-word",
                                            "whiteSpace": "normal",
                                        },
                                    ),
                                    class_name="cms-content-block block w-full max-w-3xl",
                                ),
                                class_name="text-left mb-10 w-full overflow-visible block",
                            ),
                        ),
                    ),
                    id="the-challenge",
                    class_name="mb-20 scroll-mt-24 w-full block overflow-visible",
                ),
                rx.el.div(
                    rx.el.h2(
                        "Veelgestelde Vragen",
                        class_name="text-3xl font-bold text-gray-900 mb-8",
                    ),
                    rx.cond(
                        ContextCMSState.is_loading,
                        rx.el.div(
                            rx.spinner(class_name="w-8 h-8 text-teal-600"),
                            class_name="flex justify-center py-12",
                        ),
                        rx.el.div(
                            rx.foreach(ContextCMSState.faq_items, faq_item),
                            class_name="mb-10 w-full block",
                        ),
                    ),
                    rx.el.div(
                        rx.el.h4(
                            "Heeft u nog vragen?",
                            class_name="text-lg font-bold text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "Kunt u het antwoord niet vinden? Ons team staat klaar om te helpen.",
                            class_name="text-gray-600 mb-4",
                        ),
                        rx.el.a(
                            "Contact Opnemen",
                            href="/contact-about",
                            class_name="inline-flex items-center justify-center px-6 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-emerald-600 hover:bg-emerald-700 transition-colors",
                        ),
                        class_name="bg-gray-50 p-8 rounded-xl border border-gray-100 w-full max-w-3xl text-center",
                    ),
                    id="faq",
                    class_name="scroll-mt-24 w-full block overflow-visible",
                ),
                class_name="block py-10 px-6 md:px-12 w-full max-w-4xl",
                style={"width": "100%"},
            ),
            class_name="flex flex-col md:flex-row w-full max-w-7xl mx-auto flex-1",
        )
    )