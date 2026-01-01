import reflex as rx
from app.components.layout import base_layout
from app.states.cms_content_state import CMSContentState
from app.components.protected_guard import protected_guard


def about_page() -> rx.Component:
    slug = "about-us"
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.h1("Over Ons", class_name="text-3xl font-bold mb-6"),
                rx.cond(
                    CMSContentState.loading_slugs.contains(slug),
                    rx.el.div(
                        rx.spinner(class_name="text-teal-600 w-8 h-8"),
                        class_name="flex justify-center py-12",
                    ),
                    rx.cond(
                        CMSContentState.content_cache.contains(slug),
                        protected_guard(
                            rx.el.div(
                                rx.el.style("""
                                    .page-content-fix .cms-content * {
                                        text-align: left !important;
                                        word-break: normal !important;
                                        overflow-wrap: break-word !important;
                                        white-space: normal !important;
                                        hyphens: none !important;
                                        -webkit-hyphens: none !important;
                                    }
                                    """),
                                rx.html(
                                    CMSContentState.content_cache[slug][
                                        "content_html"
                                    ].to(str),
                                    class_name="prose prose-lg prose-emerald max-w-3xl page-content-fix prose-p:text-left prose-p:leading-relaxed prose-li:text-left prose-li:break-normal cms-content",
                                ),
                            ),
                            requires_auth=CMSContentState.content_cache[slug][
                                "requires_auth"
                            ],
                            required_role=CMSContentState.content_cache[slug][
                                "required_role"
                            ],
                        ),
                        rx.html("", class_name="prose max-w-none prose-emerald"),
                    ),
                ),
                class_name="max-w-3xl mx-auto bg-white p-8 rounded-xl shadow-sm border my-12",
            ),
            class_name="container mx-auto px-4",
        )
    )