import reflex as rx
from app.components.layout import base_layout
from app.states.kb_state import KnowledgeBaseState
from app.components.wiki_sidebar import wiki_sidebar


def article_card(article: dict) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.el.span(
                    article["category"],
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800 mb-3",
                ),
                class_name="flex",
            ),
            rx.el.h3(
                article["title"],
                class_name="text-lg font-bold text-gray-900 mb-2 line-clamp-2",
            ),
            rx.el.p(
                article["excerpt"],
                class_name="text-gray-600 text-sm mb-4 line-clamp-3 flex-1",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "Lees Artikel",
                        class_name="text-emerald-600 font-medium text-sm group-hover:underline",
                    ),
                    rx.icon("arrow-right", class_name="w-4 h-4 text-emerald-600 ml-1"),
                    class_name="flex items-center",
                ),
                rx.el.span(article["date"], class_name="text-xs text-gray-400"),
                class_name="flex items-center justify-between mt-auto pt-4 border-t border-gray-50",
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-all group h-full flex flex-col",
        ),
        href=f"/kb/{article['id']}",
    )


def featured_article() -> rx.Component:
    return rx.cond(
        KnowledgeBaseState.articles.length() > 0,
        rx.el.a(
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        "UITGELICHT",
                        class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-amber-100 text-amber-800 mb-4",
                    ),
                    rx.el.h2(
                        KnowledgeBaseState.articles[0]["title"],
                        class_name="text-2xl font-bold text-gray-900 mb-3",
                    ),
                    rx.el.p(
                        KnowledgeBaseState.articles[0]["excerpt"],
                        class_name="text-gray-600 mb-6 max-w-2xl",
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Lees Nu",
                            class_name="bg-gray-900 text-white px-5 py-2.5 rounded-lg text-sm font-medium hover:bg-gray-800 transition-colors",
                        ),
                        class_name="flex",
                    ),
                    class_name="flex-1",
                ),
                rx.el.div(
                    rx.icon(
                        "book-open", class_name="w-32 h-32 text-emerald-100 opacity-50"
                    ),
                    class_name="hidden md:block",
                ),
                class_name="bg-gradient-to-br from-emerald-50 to-white p-8 rounded-2xl border border-emerald-100 flex items-center justify-between gap-8 mb-10 shadow-sm",
            ),
            href=f"/kb/{KnowledgeBaseState.articles[0]['id']}",
        ),
    )


def kb_overview_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                wiki_sidebar(),
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Kennisbank",
                            class_name="text-3xl font-bold text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "Ontdek alles over de energietransitie, zonnepanelen en batterijen.",
                            class_name="text-gray-600 text-lg mb-8",
                        ),
                        featured_article(),
                        rx.el.div(
                            rx.el.h2(
                                rx.cond(
                                    KnowledgeBaseState.selected_category == "All",
                                    "Alle Artikelen",
                                    KnowledgeBaseState.selected_category,
                                ),
                                class_name="text-xl font-bold text-gray-900",
                            ),
                            rx.el.span(
                                f"{KnowledgeBaseState.filtered_articles.length()} resultaten",
                                class_name="text-sm text-gray-500",
                            ),
                            class_name="flex items-center justify-between mb-6",
                        ),
                        rx.cond(
                            KnowledgeBaseState.filtered_articles.length() > 0,
                            rx.el.div(
                                rx.foreach(
                                    KnowledgeBaseState.filtered_articles, article_card
                                ),
                                class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 gap-6",
                            ),
                            rx.el.div(
                                rx.icon(
                                    "search-x",
                                    class_name="w-12 h-12 text-gray-300 mb-3",
                                ),
                                rx.el.p(
                                    "Geen artikelen gevonden in deze categorie.",
                                    class_name="text-gray-500",
                                ),
                                class_name="flex flex-col items-center justify-center py-16 bg-gray-50 rounded-xl border border-dashed border-gray-200",
                            ),
                        ),
                    ),
                    class_name="flex-1 py-8 px-6 lg:px-10 min-w-0",
                ),
                class_name="flex w-full max-w-7xl mx-auto items-start",
            ),
            class_name="min-h-screen bg-gray-50/50",
        )
    )


def article_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                wiki_sidebar(),
                rx.el.div(
                    rx.cond(
                        KnowledgeBaseState.current_article,
                        rx.el.div(
                            rx.el.h1(
                                KnowledgeBaseState.current_article["title"],
                                class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-6 leading-tight",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.div(
                                        rx.icon(
                                            "calendar",
                                            class_name="w-4 h-4 text-gray-400 mr-2",
                                        ),
                                        rx.el.span(
                                            KnowledgeBaseState.current_article["date"],
                                            class_name="text-sm text-gray-600",
                                        ),
                                        class_name="flex items-center mr-6",
                                    ),
                                    rx.el.div(
                                        rx.icon(
                                            "folder",
                                            class_name="w-4 h-4 text-gray-400 mr-2",
                                        ),
                                        rx.el.span(
                                            KnowledgeBaseState.current_article[
                                                "category"
                                            ],
                                            class_name="text-sm text-gray-600",
                                        ),
                                        class_name="flex items-center mr-6",
                                    ),
                                    rx.el.div(
                                        rx.icon(
                                            "user",
                                            class_name="w-4 h-4 text-gray-400 mr-2",
                                        ),
                                        rx.el.span(
                                            KnowledgeBaseState.current_article[
                                                "author"
                                            ],
                                            class_name="text-sm text-gray-600",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    class_name="flex flex-wrap items-center mb-8 pb-8 border-b border-gray-100",
                                ),
                                rx.el.div(
                                    rx.el.style("""
                                        .kb-prose-fix .cms-content * {
                                            text-align: left !important;
                                            word-break: normal !important;
                                            overflow-wrap: break-word !important;
                                            white-space: normal !important;
                                            hyphens: none !important;
                                            -webkit-hyphens: none !important;
                                        }
                                        """),
                                    rx.html(
                                        KnowledgeBaseState.current_article[
                                            "content"
                                        ].to(str),
                                        class_name="prose prose-lg prose-emerald max-w-4xl kb-prose-fix prose-img:rounded-xl prose-headings:text-gray-900 prose-p:text-left prose-p:text-gray-700 prose-p:leading-relaxed prose-li:text-left prose-li:break-normal prose-a:text-emerald-600 hover:prose-a:text-emerald-700 cms-content",
                                    ),
                                ),
                                class_name="bg-white p-8 md:p-12 rounded-2xl border border-gray-200 shadow-sm",
                            ),
                        ),
                        rx.el.div(
                            rx.icon(
                                "file-x", class_name="w-16 h-16 text-gray-300 mb-4"
                            ),
                            rx.el.h2(
                                "Artikel niet gevonden",
                                class_name="text-xl font-bold text-gray-900 mb-2",
                            ),
                            rx.el.p(
                                "Het opgevraagde artikel bestaat niet of is verwijderd.",
                                class_name="text-gray-500",
                            ),
                            rx.el.a(
                                "Terug naar overzicht",
                                href="/kb",
                                class_name="mt-6 inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium",
                            ),
                            class_name="flex flex-col items-center justify-center py-20 text-center",
                        ),
                    ),
                    class_name="flex-1 py-8 px-6 lg:px-10 min-w-0",
                ),
                class_name="flex w-full max-w-7xl mx-auto items-start",
            ),
            class_name="min-h-screen bg-gray-50/50",
        )
    )