import reflex as rx
from app.components.layout import base_layout
from app.states.auth_state import AuthState


def signup_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.img(
                            src="/full_trimmed_transparent_customcolor.png",
                            alt="Energie Insight Logo",
                            style={
                                "maxWidth": "550px",
                                "width": "100%",
                                "height": "auto",
                                "display": "block",
                            },
                        ),
                        class_name="mx-auto mb-4",
                        style={"maxWidth": "550px"},
                    ),
                    class_name="flex justify-center w-full",
                ),
                rx.el.div(
                    rx.el.h1(
                        "Account Aanmaken",
                        class_name="text-2xl font-bold mb-8 text-center text-gray-900",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Volledige Naam",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            on_change=AuthState.set_full_name,
                            class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "E-mail",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            type="email",
                            on_change=AuthState.set_email,
                            class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all",
                        ),
                        class_name="mb-4",
                    ),
                    rx.el.div(
                        rx.el.label(
                            "Wachtwoord",
                            class_name="block text-sm font-medium text-gray-700 mb-1",
                        ),
                        rx.el.input(
                            type="password",
                            on_change=AuthState.set_password,
                            class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all",
                        ),
                        class_name="mb-6",
                    ),
                    rx.cond(
                        AuthState.error != "",
                        rx.el.p(
                            AuthState.error,
                            class_name="text-red-500 text-sm mb-4 bg-red-50 p-2 rounded-md border border-red-100",
                        ),
                    ),
                    rx.el.button(
                        rx.cond(
                            AuthState.is_loading, "Account aanmaken...", "Registreren"
                        ),
                        on_click=AuthState.signup,
                        disabled=AuthState.is_loading,
                        class_name="w-full bg-emerald-600 text-white py-3 rounded-xl hover:bg-emerald-700 transition-all font-semibold shadow-sm hover:shadow-md hover:-translate-y-0.5",
                    ),
                    rx.el.p(
                        "Heeft u al een account? ",
                        rx.el.a(
                            "Log in",
                            href="/login",
                            class_name="text-emerald-600 hover:underline",
                        ),
                        class_name="text-center text-sm text-gray-600 mt-6",
                    ),
                    class_name="max-w-md mx-auto bg-white p-8 rounded-2xl shadow-lg border border-gray-100",
                ),
                class_name="container mx-auto px-4 py-12",
            )
        )
    )