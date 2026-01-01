import reflex as rx
from app.components.admin_sidebar import admin_sidebar
from app.states.category_state import CategoryState
from app.components.protected_guard import admin_guard


def category_row(category: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(category["name"], class_name="text-sm font-medium text-gray-900"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(category["slug"], class_name="text-sm text-gray-500"),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                category["description"],
                class_name="text-sm text-gray-500 truncate max-w-xs",
            ),
            class_name="px-6 py-4",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.button(
                    rx.icon("pencil", class_name="w-4 h-4"),
                    on_click=lambda: CategoryState.open_edit_modal(category),
                    class_name="text-emerald-600 hover:text-emerald-900 mr-3 transition-colors",
                ),
                rx.el.button(
                    rx.icon("trash-2", class_name="w-4 h-4"),
                    on_click=lambda: CategoryState.prompt_delete(
                        category["id"].to(str)
                    ),
                    class_name="text-red-600 hover:text-red-900 transition-colors",
                ),
                class_name="flex items-center justify-end",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right text-sm font-medium",
        ),
    )


def category_modal() -> rx.Component:
    return rx.cond(
        CategoryState.show_modal,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h3(
                        rx.cond(
                            CategoryState.is_editing, "Edit Category", "New Category"
                        ),
                        class_name="text-lg font-medium leading-6 text-gray-900",
                    ),
                    rx.el.button(
                        rx.icon(
                            "x", class_name="w-5 h-5 text-gray-400 hover:text-gray-500"
                        ),
                        on_click=CategoryState.close_modal,
                        class_name="bg-white rounded-md inline-flex text-gray-400 hover:text-gray-500 focus:outline-none",
                    ),
                    class_name="flex justify-between items-center mb-5",
                ),
                rx.el.div(
                    rx.el.div(
                        rx.el.label(
                            "Name",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            on_change=CategoryState.set_form_name,
                            placeholder="Category Name",
                            class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2",
                            default_value=CategoryState.form_name,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Slug",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            on_change=CategoryState.set_form_slug,
                            placeholder="category-slug",
                            class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 bg-gray-50",
                            default_value=CategoryState.form_slug,
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Description",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.textarea(
                            on_change=CategoryState.set_form_description,
                            placeholder="Short description of this category",
                            class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 h-24",
                            default_value=CategoryState.form_description,
                        ),
                        class_name="mb-4",
                    ),
                ),
                rx.el.div(
                    rx.el.button(
                        "Cancel",
                        on_click=CategoryState.close_modal,
                        class_name="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm",
                    ),
                    rx.el.button(
                        "Save",
                        on_click=CategoryState.save_category,
                        class_name="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-emerald-600 text-base font-medium text-white hover:bg-emerald-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm",
                    ),
                    class_name="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse",
                ),
                class_name="bg-white rounded-lg px-4 pt-5 pb-4 overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-gray-500 bg-opacity-75 transition-opacity",
        ),
    )


def delete_confirmation_dialog() -> rx.Component:
    return rx.cond(
        CategoryState.delete_confirm_open,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.icon("triangle_alert", class_name="h-6 w-6 text-red-600"),
                        class_name="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100 sm:mx-0 sm:h-10 sm:w-10",
                    ),
                    rx.el.div(
                        rx.el.h3(
                            "Delete Category",
                            class_name="text-lg leading-6 font-medium text-gray-900",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Are you sure you want to delete this category? This action cannot be undone.",
                                class_name="text-sm text-gray-500",
                            ),
                            class_name="mt-2",
                        ),
                        class_name="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left",
                    ),
                    class_name="sm:flex sm:items-start",
                ),
                rx.el.div(
                    rx.el.button(
                        "Delete",
                        on_click=CategoryState.confirm_delete,
                        class_name="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-red-600 text-base font-medium text-white hover:bg-red-700 focus:outline-none sm:ml-3 sm:w-auto sm:text-sm",
                    ),
                    rx.el.button(
                        "Cancel",
                        on_click=CategoryState.cancel_delete,
                        class_name="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm",
                    ),
                    class_name="mt-5 sm:mt-4 sm:flex sm:flex-row-reverse",
                ),
                class_name="bg-white rounded-lg px-4 pt-5 pb-4 overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full sm:p-6",
            ),
            class_name="fixed inset-0 z-50 flex items-center justify-center bg-gray-500 bg-opacity-75 transition-opacity",
        ),
    )


def categories_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Categories", class_name="text-2xl font-bold text-gray-900"
                        ),
                        rx.el.button(
                            rx.icon("plus", class_name="w-5 h-5 mr-2"),
                            "New Category",
                            on_click=CategoryState.open_add_modal,
                            class_name="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-emerald-600 hover:bg-emerald-700 focus:outline-none",
                        ),
                        class_name="flex justify-between items-center mb-6",
                    ),
                    rx.el.div(
                        rx.el.input(
                            placeholder="Search categories...",
                            on_change=CategoryState.set_search_query,
                            class_name="w-full md:w-64 px-4 py-2 border rounded-lg text-sm focus:ring-2 focus:ring-emerald-500 outline-none mb-6",
                        )
                    ),
                    rx.el.div(
                        rx.el.table(
                            rx.el.thead(
                                rx.el.tr(
                                    rx.el.th(
                                        "Name",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Slug",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Description",
                                        class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                    rx.el.th(
                                        "Actions",
                                        class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                    ),
                                ),
                                class_name="bg-gray-50",
                            ),
                            rx.el.tbody(
                                rx.cond(
                                    CategoryState.filtered_categories.length() > 0,
                                    rx.foreach(
                                        CategoryState.filtered_categories, category_row
                                    ),
                                    rx.el.tr(
                                        rx.el.td(
                                            "No categories found.",
                                            col_span=4,
                                            class_name="px-6 py-4 text-center text-sm text-gray-500",
                                        )
                                    ),
                                ),
                                class_name="bg-white divide-y divide-gray-200",
                            ),
                            class_name="min-w-full divide-y divide-gray-200",
                        ),
                        class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg bg-white overflow-x-auto",
                    ),
                ),
                class_name="flex-1 p-8 overflow-auto",
            ),
            category_modal(),
            delete_confirmation_dialog(),
            class_name="flex min-h-screen bg-gray-50",
        )
    )