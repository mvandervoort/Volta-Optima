import reflex as rx
from app.components.layout import base_layout
from app.states.blog_state import BlogState


def blog_post_card(post: dict) -> rx.Component:
    return rx.el.a(
        rx.el.div(
            rx.el.div(
                rx.cond(
                    post["category"],
                    rx.el.span(
                        post["category"],
                        class_name="absolute top-4 left-4 bg-white/90 backdrop-blur-sm px-3 py-1 rounded-full text-xs font-bold text-emerald-600 uppercase tracking-wider shadow-sm",
                    ),
                ),
                class_name="h-48 bg-gradient-to-br from-emerald-50 to-teal-100 rounded-t-xl overflow-hidden relative border-b border-gray-100",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        post["date"], class_name="text-xs text-gray-400 font-medium"
                    ),
                    class_name="mb-2",
                ),
                rx.el.h3(
                    post["title"],
                    class_name="text-xl font-bold text-gray-900 mb-3 line-clamp-2",
                ),
                rx.el.p(
                    post["excerpt"],
                    class_name="text-gray-600 text-sm mb-4 line-clamp-3 flex-1",
                ),
                rx.el.div(
                    rx.el.span(
                        "Lees Artikel",
                        class_name="text-emerald-600 font-medium text-sm group-hover:underline",
                    ),
                    rx.icon(
                        "arrow-right",
                        class_name="w-4 h-4 text-emerald-600 ml-1 transition-transform group-hover:translate-x-1",
                    ),
                    class_name="mt-auto flex items-center",
                ),
                class_name="p-6 flex flex-col flex-1",
            ),
            class_name="bg-white rounded-xl border border-gray-100 shadow-sm hover:shadow-md transition-all group h-full flex flex-col",
        ),
        href=f"/blog/{post['slug']}",
    )


def blog_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1(
                    "Laatste Inzichten",
                    class_name="text-3xl md:text-4xl font-bold text-gray-900 mb-4",
                ),
                rx.el.p(
                    "Nieuws, updates en diepgaande analyses over de energietransitie.",
                    class_name="text-xl text-gray-600 mb-12 max-w-2xl",
                ),
                rx.cond(
                    BlogState.is_loading,
                    rx.el.div(
                        rx.spinner(class_name="w-8 h-8 text-emerald-600"),
                        class_name="flex justify-center py-20",
                    ),
                    rx.cond(
                        BlogState.posts.length() > 0,
                        rx.el.div(
                            rx.foreach(BlogState.posts, blog_post_card),
                            class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8",
                        ),
                        rx.el.div(
                            rx.icon(
                                "file-text", class_name="w-12 h-12 text-gray-300 mb-4"
                            ),
                            rx.el.h3(
                                "Geen berichten gevonden",
                                class_name="text-lg font-medium text-gray-900",
                            ),
                            rx.el.p(
                                "Er zijn nog geen blogberichten gepubliceerd in deze categorie.",
                                class_name="text-gray-500 mt-1",
                            ),
                            class_name="flex flex-col items-center justify-center py-20 bg-gray-50 rounded-xl border border-dashed border-gray-200",
                        ),
                    ),
                ),
                class_name="container mx-auto px-4 py-12",
            )
        )
    )


def blog_post_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.cond(
                BlogState.is_loading,
                rx.el.div(
                    rx.spinner(class_name="w-10 h-10 text-emerald-600"),
                    class_name="min-h-[60vh] flex items-center justify-center",
                ),
                rx.cond(
                    BlogState.current_post,
                    rx.el.article(
                        rx.el.div(
                            rx.el.a(
                                "← Terug naar overzicht",
                                href="/blog",
                                class_name="text-sm font-medium text-gray-500 hover:text-emerald-600 mb-8 inline-block transition-colors",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    BlogState.current_post["category"],
                                    class_name="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 mb-6",
                                ),
                                rx.el.h1(
                                    BlogState.current_post["title"],
                                    class_name="text-3xl md:text-5xl font-bold text-gray-900 mb-6 leading-tight",
                                ),
                                rx.el.div(
                                    rx.el.div(
                                        rx.icon(
                                            "calendar",
                                            class_name="w-4 h-4 text-gray-400 mr-2",
                                        ),
                                        rx.el.span(
                                            BlogState.current_post["date"],
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
                                            BlogState.current_post["author"],
                                            class_name="text-sm text-gray-600",
                                        ),
                                        class_name="flex items-center",
                                    ),
                                    class_name="flex flex-wrap items-center mb-10 pb-10 border-b border-gray-100",
                                ),
                                rx.el.div(
                                    rx.html(
                                        BlogState.current_post["content_html"].to(str),
                                        class_name="prose prose-lg prose-emerald max-w-4xl blog-prose-fix prose-img:rounded-xl prose-headings:text-gray-900 prose-p:text-left prose-p:text-gray-700 prose-p:leading-relaxed prose-li:text-left prose-li:break-normal prose-a:text-emerald-600 hover:prose-a:text-emerald-700 cms-content",
                                    )
                                ),
                                class_name="max-w-4xl mx-auto",
                            ),
                        ),
                        class_name="container mx-auto px-4 py-12",
                    ),
                    rx.el.div(
                        rx.icon("file-x", class_name="w-16 h-16 text-gray-300 mb-4"),
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
                            href="/blog",
                            class_name="mt-6 inline-flex items-center px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors text-sm font-medium",
                        ),
                        class_name="min-h-[60vh] flex flex-col items-center justify-center text-center",
                    ),
                ),
            )
        )
    )