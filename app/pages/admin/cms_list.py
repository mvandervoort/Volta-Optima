import reflex as rx
from app.components.admin_sidebar import admin_sidebar
from app.states.cms_list_state import CMSListState
from app.components.protected_guard import admin_guard


def filter_bar() -> rx.Component:
    return rx.el.div(
        rx.el.input(
            placeholder="Zoek berichten...",
            on_change=CMSListState.set_search_query,
            class_name="w-full md:w-64 px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none",
        ),
        rx.el.div(
            rx.el.select(
                rx.el.option("Alle Statussen", value=""),
                rx.el.option("Gepubliceerd", value="published"),
                rx.el.option("Concept", value="draft"),
                on_change=CMSListState.set_filter_status,
                value=CMSListState.filter_status,
                class_name="px-3 py-2 border rounded-lg text-sm bg-white appearance-none",
            ),
            rx.el.select(
                rx.el.option("Alle Talen", value=""),
                rx.el.option("Engels", value="en"),
                rx.el.option("Nederlands", value="nl"),
                on_change=CMSListState.set_filter_language,
                value=CMSListState.filter_language,
                class_name="px-3 py-2 border rounded-lg text-sm bg-white appearance-none",
            ),
            rx.el.select(
                rx.el.option("Alle Categorieën", value=""),
                rx.foreach(
                    CMSListState.categories,
                    lambda cat: rx.el.option(cat["name"], value=cat["id"]),
                ),
                on_change=CMSListState.set_filter_category,
                value=CMSListState.filter_category,
                class_name="px-3 py-2 border rounded-lg text-sm bg-white appearance-none",
            ),
            class_name="flex gap-2",
        ),
        class_name="flex flex-col md:flex-row justify-between gap-4 mb-6 bg-white p-4 rounded-xl shadow-sm border border-gray-100",
    )


def post_row(post: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.input(
                type="checkbox",
                on_change=lambda _: CMSListState.toggle_selection(post["id"].to(str)),
                checked=CMSListState.selected_ids.contains(post["id"].to(str)),
                class_name="rounded text-emerald-600 focus:ring-emerald-500",
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.div(
                    post["title"], class_name="text-sm font-medium text-gray-900"
                ),
                rx.el.div(post["slug"], class_name="text-sm text-gray-500"),
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.cond(
                post["status"] == "published",
                rx.el.span(
                    "Gepubliceerd",
                    class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800",
                ),
                rx.el.span(
                    "Concept",
                    class_name="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                post["language"].to(str).upper(), class_name="text-sm text-gray-500"
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                post["updated_at_formatted"], class_name="text-sm text-gray-500"
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.a(
                    rx.icon("pencil", class_name="w-4 h-4"),
                    href="/admin/cms/editor/" + post["id"].to(str),
                    class_name="text-emerald-600 hover:text-emerald-900 mr-3 transition-colors",
                ),
                rx.el.button(
                    rx.icon("copy", class_name="w-4 h-4"),
                    on_click=lambda: CMSListState.duplicate_post(post["id"].to(str)),
                    class_name="text-blue-600 hover:text-blue-900 mr-3 transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: CMSListState.delete_post(post["id"].to(str)),
                    class_name="text-red-600 hover:text-red-900 transition-colors",
                ),
                class_name="flex items-center",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
    )


def cms_list_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Contentbeheer",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.a(
                            rx.icon("plus", class_name="w-5 h-5 mr-2"),
                            "Nieuw Bericht",
                            href="/admin/cms/editor/new",
                            class_name="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none",
                        ),
                        class_name="flex justify-between items-center mb-6",
                    ),
                    filter_bar(),
                    rx.cond(
                        CMSListState.selected_ids.length() > 0,
                        rx.el.div(
                            rx.el.span(
                                f"{CMSListState.selected_ids.length()} items geselecteerd",
                                class_name="text-sm text-gray-700 font-medium",
                            ),
                            rx.el.button(
                                "Verwijder Geselecteerde",
                                on_click=CMSListState.bulk_delete,
                                class_name="px-3 py-1 bg-red-100 text-red-700 rounded-md text-sm font-medium hover:bg-red-200 transition-colors",
                            ),
                            class_name="flex justify-between items-center bg-blue-50 px-4 py-3 rounded-lg mb-4 border border-blue-100",
                        ),
                    ),
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        rx.el.input(
                                            type="checkbox",
                                            on_change=CMSListState.toggle_all_selection,
                                            class_name="rounded text-emerald-600 focus:ring-emerald-500",
                                        ),
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Titel",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Status",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Taal",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Bijgewerkt",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Acties",
                                        class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                ),
                                class_name="bg-gray-50",
                            ),
                            rx.el.tbody(
                                rx.foreach(CMSListState.posts, post_row),
                                class_name="bg-white divide-y divide-gray-200",
                            ),
                            class_name="min-w-full divide-y divide-gray-200",
                        ),
                        class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg bg-white overflow-x-auto",
                    ),
                ),
                class_name="flex-1 p-8 overflow-auto",
            ),
            class_name="flex min-h-screen bg-gray-50",
        )
    )