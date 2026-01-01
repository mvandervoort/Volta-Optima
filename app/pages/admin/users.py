import reflex as rx
from app.components.admin_sidebar import admin_sidebar
from app.states.admin_users_state import AdminUsersState
from app.components.protected_guard import admin_guard


def user_detail_modal() -> rx.Component:
    user = AdminUsersState.selected_user
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-in fade-in duration-200"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "User Details", class_name="text-xl font-bold text-gray-900"
                        ),
                        rx.radix.primitives.dialog.close(
                            rx.el.button(
                                rx.icon("x", class_name="w-5 h-5 text-gray-500"),
                                class_name="p-1 hover:bg-gray-100 rounded-full transition-colors",
                            )
                        ),
                        class_name="flex justify-between items-center mb-6 border-b border-gray-100 pb-4",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.p(
                                "ID",
                                class_name="text-xs font-bold text-gray-500 uppercase",
                            ),
                            rx.el.p(
                                user["id"].to(str),
                                class_name="text-sm font-mono bg-gray-50 p-2 rounded border border-gray-200 break-all",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Email",
                                class_name="text-xs font-bold text-gray-500 uppercase",
                            ),
                            rx.el.p(
                                user["email"].to(str),
                                class_name="text-sm font-medium text-gray-900",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Role",
                                class_name="text-xs font-bold text-gray-500 uppercase",
                            ),
                            rx.el.span(
                                user["role"].to(str),
                                class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Timestamps",
                                class_name="text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.div(
                                rx.el.div(
                                    rx.el.span(
                                        "Created:", class_name="text-gray-500 mr-2"
                                    ),
                                    rx.el.span(user["created_at"].to(str)),
                                    class_name="text-xs",
                                ),
                                rx.el.div(
                                    rx.el.span(
                                        "Last Login:", class_name="text-gray-500 mr-2"
                                    ),
                                    rx.el.span(user["last_login"].to(str)),
                                    class_name="text-xs",
                                ),
                                class_name="bg-gray-50 p-3 rounded-lg border border-gray-100",
                            ),
                            class_name="mb-4",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "User Metadata",
                                class_name="text-xs font-bold text-gray-500 uppercase mb-1",
                            ),
                            rx.el.pre(
                                user["metadata"].to_string(),
                                class_name="text-xs bg-gray-900 text-green-400 p-3 rounded-lg overflow-x-auto font-mono",
                            ),
                            class_name="mb-4",
                        ),
                        class_name="space-y-4",
                    ),
                    class_name="bg-white rounded-2xl p-6 shadow-xl w-full max-w-lg mx-4 outline-none animate-in zoom-in-95 duration-200 max-h-[85vh] overflow-y-auto",
                ),
                class_name="fixed left-[50%] top-[50%] translate-x-[-50%] translate-y-[-50%] z-[60] focus:outline-none",
            ),
        ),
        open=AdminUsersState.is_detail_open,
        on_open_change=lambda _: AdminUsersState.close_detail(),
    )


def user_row(user: dict) -> rx.Component:
    return rx.el.tr(
        rx.el.td(
            rx.el.div(
                rx.el.div(user["email"], class_name="text-sm font-medium text-gray-900")
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                user["role"],
                class_name=rx.cond(
                    user["role"] == "admin",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-purple-100 text-purple-800",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.span(
                user["status"],
                class_name=rx.cond(
                    user["status"] == "Active",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800",
                    "px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800",
                ),
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.div(
                rx.el.span(
                    user["last_login"].to(str).split("T")[0],
                    class_name="text-sm text-gray-500",
                )
            ),
            class_name="px-6 py-4 whitespace-nowrap",
        ),
        rx.el.td(
            rx.el.button(
                rx.icon("eye", class_name="w-5 h-5"),
                on_click=lambda: AdminUsersState.open_detail(user),
                class_name="text-gray-400 hover:text-emerald-600 transition-colors p-2 hover:bg-gray-100 rounded-full",
                title="View Details",
            ),
            class_name="px-6 py-4 whitespace-nowrap text-right",
        ),
    )


def role_management_info() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Role Management Guide", class_name="text-lg font-bold mb-4"),
        rx.el.div(
            rx.el.p(
                "Due to security restrictions, user roles cannot be modified directly through this dashboard without a service_role key. To assign admin privileges, please execute the following SQL in your Supabase Dashboard:",
                class_name="text-sm text-gray-600 mb-4",
            ),
            rx.el.div(
                rx.el.pre(
                    """UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'user@example.com';""",
                    class_name="font-mono text-xs text-emerald-300 bg-gray-900 p-4 rounded-lg overflow-x-auto mb-2",
                ),
                rx.el.button(
                    rx.icon("copy", class_name="w-4 h-4 mr-2"),
                    "Copy SQL Query",
                    on_click=AdminUsersState.copy_sql,
                    class_name="flex items-center text-xs text-emerald-600 hover:text-emerald-700 font-medium",
                ),
                class_name="bg-gray-50 p-4 rounded-lg border border-gray-200",
            ),
        ),
        class_name="bg-white p-6 rounded-xl border border-gray-200 mt-8",
    )


def admin_users_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            user_detail_modal(),
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "User Management",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.p(
                            "View registered users.",
                            class_name="text-sm text-gray-500 mt-1",
                        ),
                        class_name="mb-6",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "info", class_name="w-5 h-5 text-blue-500 mr-3 shrink-0"
                            ),
                            rx.el.p(
                                "This is a read-only view. For security reasons, full user management (Create, Update, Delete) is restricted to the Supabase Dashboard.",
                                class_name="text-sm text-blue-700",
                            ),
                            class_name="flex items-start bg-blue-50 p-4 rounded-lg border border-blue-100 mb-6",
                        ),
                        rx.cond(
                            AdminUsersState.error != "",
                            rx.el.div(
                                rx.icon(
                                    "trending_down",
                                    class_name="w-5 h-5 text-red-500 mr-3 shrink-0",
                                ),
                                rx.el.p(
                                    AdminUsersState.error,
                                    class_name="text-sm text-red-700",
                                ),
                                class_name="flex items-start bg-red-50 p-4 rounded-lg border border-red-100 mb-6",
                            ),
                        ),
                        rx.cond(
                            AdminUsersState.is_loading,
                            rx.el.div(
                                rx.spinner(class_name="w-8 h-8 text-emerald-600"),
                                class_name="flex justify-center py-12",
                            ),
                            rx.el.table(
                                rx.el.thead(
                                    rx.el.tr(
                                        rx.el.th(
                                            "User",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Role",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Status",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Last Login",
                                            class_name="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                        rx.el.th(
                                            "Details",
                                            class_name="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider",
                                        ),
                                    ),
                                    class_name="bg-gray-50",
                                ),
                                rx.el.tbody(
                                    rx.foreach(AdminUsersState.users, user_row),
                                    class_name="bg-white divide-y divide-gray-200",
                                ),
                                class_name="min-w-full divide-y divide-gray-200",
                            ),
                        ),
                        class_name="shadow overflow-hidden border-b border-gray-200 sm:rounded-lg bg-white overflow-x-auto",
                    ),
                    role_management_info(),
                ),
                class_name="flex-1 p-8 overflow-auto bg-gray-50",
                on_mount=AdminUsersState.load_users,
            ),
            class_name="flex min-h-screen bg-gray-50",
        )
    )