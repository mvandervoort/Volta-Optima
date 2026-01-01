import reflex as rx


def admin_sidebar_item(text: str, url: str, icon: str) -> rx.Component:
    is_active = rx.State.router.page.path == url
    return rx.el.a(
        rx.icon(
            icon,
            class_name=f"w-5 h-5 mr-3 {rx.cond(is_active, 'text-emerald-600', 'text-gray-500')}",
        ),
        rx.el.span(text),
        href=url,
        class_name=rx.cond(
            is_active,
            "flex items-center px-4 py-3 bg-emerald-50 text-emerald-700 rounded-lg mb-1 font-medium",
            "flex items-center px-4 py-3 text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-lg mb-1 transition-colors",
        ),
    )


def admin_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.icon("shield-check", class_name="h-8 w-8 text-emerald-600 mb-2"),
                rx.el.span(
                    "Admin Portal", class_name="text-xl font-bold text-gray-900"
                ),
                class_name="flex flex-col items-center mb-8 pt-4",
            ),
            rx.el.nav(
                rx.el.p(
                    "CONTENT",
                    class_name="px-4 text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 mt-4",
                ),
                admin_sidebar_item("Dashboard", "/admin", "layout-dashboard"),
                admin_sidebar_item("CMS Posts (Legacy)", "/admin/cms", "file-text"),
                admin_sidebar_item("Categories", "/admin/categories", "folder"),
                rx.el.p(
                    "SYSTEM",
                    class_name="px-4 text-xs font-bold text-gray-400 uppercase tracking-wider mb-2 mt-6",
                ),
                admin_sidebar_item("Analytics", "/admin/analytics", "bar-chart-2"),
                admin_sidebar_item("Users", "/admin/users", "users"),
                admin_sidebar_item("Settings", "/admin/settings", "settings"),
                class_name="space-y-1",
            ),
            class_name="h-full px-4",
        ),
        class_name="w-64 bg-white border-r border-gray-200 min-h-screen shrink-0 hidden md:block",
    )