import reflex as rx
from app.components.layout import base_layout
from app.components.admin_sidebar import admin_sidebar
from app.states.admin_state import AdminState
from app.states.base_state import State
from app.components.protected_guard import admin_guard


def dashboard_stat(title: str, value: str, icon: str, color: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.div(
                rx.icon(icon, class_name=f"w-6 h-6 text-{color}-600"),
                class_name=f"w-12 h-12 rounded-xl bg-{color}-100 flex items-center justify-center mb-4",
            ),
            rx.el.p(
                title,
                class_name="text-sm text-gray-500 font-semibold uppercase tracking-wider mb-1",
            ),
            rx.el.h3(value, class_name="text-2xl font-bold text-gray-900"),
            class_name="flex flex-col",
        ),
        class_name="bg-white p-6 rounded-2xl border border-gray-100 shadow-sm",
    )


def admin_guide_section() -> rx.Component:
    return rx.el.div(
        rx.el.h3("Admin Guide: User Roles", class_name="text-xl font-bold mb-4"),
        rx.el.div(
            rx.el.div(
                rx.el.p(
                    "To assign the 'admin' role to a user, you must use the SQL Editor in your Supabase Dashboard. This is required because role management is restricted for security.",
                    class_name="text-sm text-gray-600 mb-4 leading-relaxed",
                ),
                rx.el.div(
                    rx.el.p(
                        "Run this SQL query:",
                        class_name="text-xs font-bold text-gray-500 uppercase mb-2",
                    ),
                    rx.el.pre(
                        """UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'user@example.com';""",
                        class_name="bg-gray-900 text-emerald-400 p-4 rounded-lg text-xs overflow-x-auto font-mono",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.icon("info", class_name="w-5 h-5 text-blue-500 mr-2 shrink-0"),
                    rx.el.p(
                        "Users must log out and log back in for role changes to take effect.",
                        class_name="text-xs text-blue-700",
                    ),
                    class_name="flex items-start bg-blue-50 p-3 rounded-lg border border-blue-100",
                ),
            ),
            class_name="bg-white p-6 rounded-xl border border-gray-200",
        ),
        class_name="mt-8",
    )


def recent_activity_item(act: dict) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.p(act["action"], class_name="font-medium text-gray-900"),
            rx.el.p(act["time"], class_name="text-xs text-gray-500"),
            class_name="flex justify-between items-center mb-1",
        ),
        rx.el.div(
            rx.el.span(act["title"], class_name="text-sm text-gray-600 truncate block"),
            rx.el.span(
                act["status"],
                class_name="text-xs px-2 py-0.5 rounded-full bg-gray-100 text-gray-600 ml-2 shrink-0",
            ),
            class_name="flex justify-between items-center",
        ),
        class_name="py-4 border-b border-gray-100 last:border-0",
    )


def admin_dashboard_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "Admin Dashboard",
                            class_name="text-3xl font-bold text-gray-900",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Logged in as:",
                                class_name="text-xs text-gray-500 text-right",
                            ),
                            rx.el.p(
                                State.user["email"],
                                class_name="text-sm font-bold text-emerald-600 text-right",
                            ),
                            class_name="flex flex-col",
                        ),
                        class_name="flex justify-between items-center mb-8",
                    ),
                    rx.el.div(
                        dashboard_stat(
                            "Total Posts",
                            AdminState.total_posts.to_string(),
                            "file-text",
                            "blue",
                        ),
                        dashboard_stat(
                            "Published",
                            AdminState.published_posts.to_string(),
                            "circle_check",
                            "emerald",
                        ),
                        dashboard_stat(
                            "Drafts",
                            AdminState.draft_posts.to_string(),
                            "location_edit",
                            "orange",
                        ),
                        dashboard_stat(
                            "Categories",
                            AdminState.total_categories.to_string(),
                            "folder",
                            "purple",
                        ),
                        class_name="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8",
                    ),
                    rx.el.div(
                        rx.el.div(
                            rx.el.h3(
                                "Recent CMS Updates",
                                class_name="text-xl font-bold mb-4",
                            ),
                            rx.el.div(
                                rx.cond(
                                    AdminState.recent_activity.length() > 0,
                                    rx.foreach(
                                        AdminState.recent_activity, recent_activity_item
                                    ),
                                    rx.el.p(
                                        "No recent activity found.",
                                        class_name="text-sm text-gray-500 italic p-4",
                                    ),
                                ),
                                class_name="bg-white p-6 rounded-xl border border-gray-200",
                            ),
                            class_name="col-span-1 lg:col-span-2",
                        ),
                        rx.el.div(
                            rx.el.h3(
                                "Quick Actions", class_name="text-xl font-bold mb-4"
                            ),
                            rx.el.div(
                                rx.el.a(
                                    rx.icon("plus", class_name="w-5 h-5 mr-3"),
                                    "New Article",
                                    href="/admin/cms/editor/new",
                                    class_name="w-full flex items-center p-4 bg-white border border-gray-200 rounded-xl hover:border-emerald-500 hover:text-emerald-600 transition-colors mb-4 font-medium",
                                ),
                                rx.el.a(
                                    rx.icon("folder-plus", class_name="w-5 h-5 mr-3"),
                                    "Manage Categories",
                                    href="/admin/categories",
                                    class_name="w-full flex items-center p-4 bg-white border border-gray-200 rounded-xl hover:border-emerald-500 hover:text-emerald-600 transition-colors mb-4 font-medium",
                                ),
                                rx.el.a(
                                    rx.icon("list", class_name="w-5 h-5 mr-3"),
                                    "All Posts",
                                    href="/admin/cms",
                                    class_name="w-full flex items-center p-4 bg-white border border-gray-200 rounded-xl hover:border-emerald-500 hover:text-emerald-600 transition-colors font-medium",
                                ),
                            ),
                            admin_guide_section(),
                            class_name="col-span-1",
                        ),
                        class_name="grid grid-cols-1 lg:grid-cols-3 gap-8",
                    ),
                    class_name="p-8",
                ),
                class_name="flex-1 overflow-auto bg-gray-50",
                on_mount=AdminState.load_stats,
            ),
            class_name="flex min-h-screen",
        )
    )