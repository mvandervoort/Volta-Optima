import reflex as rx
from app.states.base_state import State
from app.states.auth_state import AuthState


def protected_guard(
    children: rx.Component,
    requires_auth: rx.Var[bool] | bool = False,
    required_role: rx.Var[str] | str = "any",
) -> rx.Component:
    """
    Wraps content to protect it based on authentication and role requirements.
    """
    return rx.cond(
        requires_auth,
        rx.cond(
            State.is_authenticated,
            rx.cond(
                (required_role == "admin") & ~State.is_admin,
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "shield-alert", class_name="w-16 h-16 text-red-500 mb-4"
                        ),
                        rx.el.h1(
                            "Access Denied",
                            class_name="text-2xl font-bold text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "You do not have permission to view this page.",
                            class_name="text-gray-600 mb-6",
                        ),
                        rx.el.a(
                            "Return Home",
                            href="/",
                            class_name="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors",
                        ),
                        class_name="flex flex-col items-center text-center p-8 bg-white rounded-2xl shadow-sm border border-gray-100 max-w-md mx-auto mt-20",
                    ),
                    class_name="min-h-[60vh] flex items-center justify-center",
                ),
                children,
            ),
            rx.radix.primitives.dialog.root(
                rx.radix.primitives.dialog.portal(
                    rx.radix.primitives.dialog.overlay(
                        class_name="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 animate-in fade-in duration-200"
                    ),
                    rx.radix.primitives.dialog.content(
                        rx.el.div(
                            rx.el.div(
                                rx.icon(
                                    "lock", class_name="w-12 h-12 text-emerald-600 mb-4"
                                ),
                                class_name="flex justify-center w-full",
                            ),
                            rx.radix.primitives.dialog.title(
                                "Inloggen Vereist",
                                class_name="text-xl font-bold text-center text-gray-900 mb-2",
                            ),
                            rx.radix.primitives.dialog.description(
                                "Voor deze module is inloggen verplicht. Registreer eerst als je dat nog niet hebt gedaan.",
                                class_name="text-center text-gray-600 mb-8 text-sm",
                            ),
                            rx.el.div(
                                rx.el.button(
                                    "Inloggen",
                                    on_click=[
                                        AuthState.set_redirect_url(
                                            State.router.page.path
                                        ),
                                        rx.redirect("/login"),
                                    ],
                                    class_name="w-full bg-emerald-600 text-white font-bold py-3 rounded-xl hover:bg-emerald-700 transition-colors shadow-lg hover:shadow-emerald-200/50 outline-none mb-3",
                                ),
                                rx.el.a(
                                    "Terug naar Home",
                                    href="/",
                                    class_name="block w-full text-center text-sm text-gray-500 hover:text-gray-900 font-medium py-2 hover:bg-gray-50 rounded-lg transition-colors",
                                ),
                                class_name="flex flex-col w-full",
                            ),
                            class_name="flex flex-col w-full items-center",
                        ),
                        class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl p-8 shadow-2xl w-[90vw] max-w-sm z-[60] outline-none animate-in zoom-in-95 duration-200 border border-gray-100",
                    ),
                ),
                open=True,
            ),
        ),
        children,
    )


def admin_guard(children: rx.Component) -> rx.Component:
    """
    Convenience wrapper for admin-only pages.
    """
    return protected_guard(children, requires_auth=True, required_role="admin")