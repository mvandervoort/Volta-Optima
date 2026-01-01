import reflex as rx
from app.states.reset_password_state import ResetPasswordState
from app.components.layout import base_layout


def reset_password_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.img(
                    src="/full_trimmed_transparent_customcolor.png",
                    alt="Energie Insight Logo",
                    class_name="mx-auto max-w-[300px] mb-8",
                ),
                rx.el.h1(
                    "Nieuw Wachtwoord",
                    class_name="text-2xl font-bold mb-6 text-center text-gray-900",
                ),
                rx.cond(
                    ResetPasswordState.success,
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "circle-check",
                                class_name="w-16 h-16 text-emerald-500 mb-4",
                            ),
                            class_name="flex justify-center",
                        ),
                        rx.el.h3(
                            "Wachtwoord Gewijzigd",
                            class_name="text-xl font-bold text-center text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "Uw wachtwoord is succesvol aangepast. U kunt nu inloggen met uw nieuwe wachtwoord.",
                            class_name="text-center text-gray-600 mb-8 leading-relaxed",
                        ),
                        rx.el.a(
                            "Ga naar Inloggen",
                            href="/login",
                            class_name="block w-full text-center bg-emerald-600 text-white py-3 rounded-xl hover:bg-emerald-700 transition-colors font-semibold shadow-md",
                        ),
                        class_name="animate-in fade-in slide-in-from-bottom-4 duration-500",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Stel een nieuw wachtwoord in voor uw account.",
                            class_name="text-gray-600 mb-6 text-center text-sm",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Nieuw Wachtwoord",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="password",
                                on_change=ResetPasswordState.set_new_password,
                                placeholder="Minimaal 8 tekens",
                                class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all mb-4 text-gray-900",
                            ),
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Bevestig Wachtwoord",
                                class_name="block text-sm font-medium text-gray-700 mb-1",
                            ),
                            rx.el.input(
                                type="password",
                                on_change=ResetPasswordState.set_confirm_password,
                                placeholder="Herhaal wachtwoord",
                                class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all mb-6 text-gray-900",
                            ),
                        ),
                        rx.cond(
                            ResetPasswordState.error_message != "",
                            rx.el.div(
                                rx.icon("circle-alert", class_name="w-4 h-4 mr-2"),
                                ResetPasswordState.error_message,
                                class_name="flex items-center text-red-600 text-sm mb-4 bg-red-50 p-3 rounded-lg border border-red-100 animate-in fade-in slide-in-from-top-1",
                            ),
                        ),
                        rx.el.button(
                            rx.cond(
                                ResetPasswordState.is_loading,
                                rx.el.div(
                                    rx.spinner(class_name="w-5 h-5 text-white mr-2"),
                                    "Bezig met opslaan...",
                                    class_name="flex items-center justify-center",
                                ),
                                "Wachtwoord Opslaan",
                            ),
                            on_click=ResetPasswordState.reset_password,
                            disabled=ResetPasswordState.is_loading,
                            class_name="w-full bg-emerald-600 text-white py-3 rounded-xl hover:bg-emerald-700 transition-all font-semibold shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-md",
                        ),
                        rx.el.div(
                            rx.el.a(
                                "Terug naar Inloggen",
                                href="/login",
                                class_name="text-sm text-gray-500 hover:text-emerald-600 transition-colors font-medium",
                            ),
                            class_name="text-center mt-6 pt-6 border-t border-gray-100",
                        ),
                    ),
                ),
                class_name="max-w-md mx-auto bg-white p-8 rounded-2xl shadow-xl border border-gray-100",
            ),
            class_name="container mx-auto px-4 py-20 min-h-[calc(100vh-200px)] flex items-center justify-center",
            on_mount=ResetPasswordState.on_load,
        )
    )