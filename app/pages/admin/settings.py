import reflex as rx
from app.components.admin_sidebar import admin_sidebar
from app.states.admin_settings_state import AdminSettingsState
from app.components.protected_guard import admin_guard


def status_indicator(label: str, connected: bool) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.span(label, class_name="text-sm font-medium text-gray-700"),
            rx.cond(
                connected,
                rx.el.span(
                    "Connected",
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800",
                ),
                rx.el.span(
                    "Not Configured",
                    class_name="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800",
                ),
            ),
            class_name="flex justify-between items-center mb-2",
        ),
        rx.el.div(
            class_name=rx.cond(
                connected,
                "h-2 bg-green-500 rounded-full",
                "h-2 bg-red-500 rounded-full",
            ),
            style={"width": "100%"},
        ),
        class_name="bg-white p-4 rounded-lg border border-gray-200 shadow-sm",
    )


def settings_section(title: str, content: rx.Component) -> rx.Component:
    return rx.el.div(
        rx.el.h3(title, class_name="text-lg font-bold text-gray-900 mb-4"),
        rx.el.div(
            content,
            class_name="bg-white p-6 rounded-xl border border-gray-200 shadow-sm",
        ),
        class_name="mb-8",
    )


def admin_settings_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            admin_sidebar(),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h1(
                            "System Settings",
                            class_name="text-2xl font-bold text-gray-900",
                        ),
                        rx.el.p(
                            "Manage global application configurations and view system status.",
                            class_name="text-sm text-gray-500 mt-1",
                        ),
                        class_name="mb-8",
                    ),
                    settings_section(
                        "Site Configuration",
                        rx.el.div(
                            rx.el.div(
                                rx.el.label(
                                    "Site Name",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.input(
                                    default_value="Energie Insight",
                                    placeholder="Enter site name",
                                    class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2",
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.div(
                                rx.el.label(
                                    "Site Description",
                                    class_name="block text-sm font-medium text-gray-700 mb-1",
                                ),
                                rx.el.textarea(
                                    default_value="Empowering your journey to a sustainable energy future with data-driven insights.",
                                    placeholder="Enter site description",
                                    class_name="w-full rounded-md border-gray-300 shadow-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 h-24",
                                ),
                                class_name="mb-4",
                            ),
                            rx.el.button(
                                "Save Changes",
                                class_name="px-4 py-2 bg-emerald-600 text-white text-sm font-medium rounded-md hover:bg-emerald-700 transition-colors",
                            ),
                        ),
                    ),
                    settings_section(
                        "Integration Status",
                        rx.el.div(
                            status_indicator(
                                "Supabase (Database & Auth)",
                                AdminSettingsState.supabase_connected,
                            ),
                            status_indicator(
                                "QuestDB (Time Series Data)",
                                AdminSettingsState.questdb_connected,
                            ),
                            status_indicator(
                                "Resend (Email Service)",
                                AdminSettingsState.resend_configured,
                            ),
                            class_name="grid grid-cols-1 md:grid-cols-3 gap-6",
                        ),
                    ),
                    settings_section(
                        "System Information",
                        rx.el.div(
                            rx.el.div(
                                rx.el.span(
                                    "App Version", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    AdminSettingsState.app_version,
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                class_name="flex justify-between py-2 border-b border-gray-100",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "Python Version", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    AdminSettingsState.python_version,
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                class_name="flex justify-between py-2 border-b border-gray-100",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    "Platform", class_name="text-sm text-gray-500"
                                ),
                                rx.el.span(
                                    AdminSettingsState.platform_info,
                                    class_name="text-sm font-medium text-gray-900",
                                ),
                                class_name="flex justify-between py-2",
                            ),
                        ),
                    ),
                ),
                class_name="flex-1 p-8 overflow-auto bg-gray-50",
                on_mount=AdminSettingsState.on_load,
            ),
            class_name="flex min-h-screen bg-gray-50",
        )
    )