import reflex as rx
from app.states.kb_state import KnowledgeBaseState


def category_link(name: str, count: int) -> rx.Component:
    is_active = KnowledgeBaseState.selected_category == name
    return rx.el.button(
        rx.el.span(name, class_name="text-sm font-medium"),
        rx.el.span(
            count,
            class_name="text-xs bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full group-hover:bg-emerald-100 group-hover:text-emerald-700 transition-colors",
        ),
        on_click=lambda: KnowledgeBaseState.select_category(name),
        class_name=rx.cond(
            is_active,
            "flex items-center justify-between w-full px-3 py-2 text-emerald-700 bg-emerald-50 rounded-lg transition-colors mb-1 group",
            "flex items-center justify-between w-full px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-colors mb-1 group",
        ),
    )


def recent_article_link(article: dict) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.icon(
                "file-text", class_name="w-4 h-4 text-gray-400 mt-0.5 mr-3 shrink-0"
            ),
            rx.el.div(
                rx.el.p(
                    article["title"],
                    class_name="text-sm font-medium text-gray-700 hover:text-emerald-600 line-clamp-2 transition-colors",
                ),
                rx.el.p(article["date"], class_name="text-xs text-gray-400 mt-1"),
            ),
            class_name="flex items-start",
        ),
        href=f"/kb/{article['id']}",
        class_name="block mb-4 last:mb-0",
    )


def wiki_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon(
                        "search",
                        class_name="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400",
                    ),
                    rx.el.input(
                        placeholder="Zoeken...",
                        on_change=KnowledgeBaseState.set_search_query,
                        class_name="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent placeholder-gray-400",
                        default_value=KnowledgeBaseState.search_query,
                    ),
                    class_name="relative",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.h3(
                    "CATEGORIEËN",
                    class_name="px-1 text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                ),
                rx.el.div(
                    category_link("All", KnowledgeBaseState.articles.length()),
                    rx.foreach(
                        KnowledgeBaseState.category_counts,
                        lambda item: category_link(item[0], item[1]),
                    ),
                    class_name="space-y-0.5",
                ),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.h3(
                    "MEEST RECENT",
                    class_name="px-1 text-xs font-bold text-gray-400 uppercase tracking-wider mb-4",
                ),
                rx.foreach(KnowledgeBaseState.recent_articles, recent_article_link),
                class_name="mb-8",
            ),
            rx.el.div(
                rx.el.h3(
                    "SNEL NAAR",
                    class_name="px-1 text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                ),
                rx.el.a(
                    rx.icon("calculator", class_name="w-4 h-4 mr-2"),
                    "Zonnepanelen Calculator",
                    href="/solar",
                    class_name="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-emerald-600 hover:bg-gray-50 rounded-lg transition-colors",
                ),
                rx.el.a(
                    rx.icon("battery-charging", class_name="w-4 h-4 mr-2"),
                    "Batterij Schatter",
                    href="/battery",
                    class_name="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-emerald-600 hover:bg-gray-50 rounded-lg transition-colors",
                ),
                rx.el.a(
                    rx.icon("circle_help", class_name="w-4 h-4 mr-2"),
                    "Veelgestelde Vragen",
                    href="/aanleiding#faq",
                    class_name="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:text-emerald-600 hover:bg-gray-50 rounded-lg transition-colors",
                ),
            ),
            class_name="h-full overflow-y-auto pr-4",
        ),
        class_name="w-72 shrink-0 hidden lg:block border-r border-gray-200 py-8 sticky top-[80px] h-[calc(100vh-80px)] min-w-0",
    )