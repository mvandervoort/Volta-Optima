import reflex as rx
from app.states.forgot_password_state import ForgotPasswordState
from app.components.layout import base_layout


def forgot_password_page() -> rx.Component:
    return base_layout(
        rx.el.div(
            rx.el.div(
                rx.el.img(
                    src="/full_trimmed_transparent_customcolor.png",
                    alt="Energie Insight Logo",
                    class_name="mx-auto max-w-[300px] mb-8",
                ),
                rx.el.h1(
                    "Wachtwoord Herstellen",
                    class_name="text-2xl font-bold mb-6 text-center text-gray-900",
                ),
                rx.cond(
                    ForgotPasswordState.has_sent,
                    rx.el.div(
                        rx.el.div(
                            rx.icon(
                                "circle-check",
                                class_name="w-16 h-16 text-emerald-500 mb-4",
                            ),
                            class_name="flex justify-center",
                        ),
                        rx.el.h3(
                            "Check uw e-mail",
                            class_name="text-xl font-bold text-center text-gray-900 mb-2",
                        ),
                        rx.el.p(
                            "We hebben een e-mail verzonden met instructies om uw wachtwoord te herstellen. Vergeet niet uw spam-folder te controleren.",
                            class_name="text-center text-gray-600 mb-8 leading-relaxed",
                        ),
                        rx.el.a(
                            "Terug naar Inloggen",
                            href="/login",
                            class_name="block w-full text-center bg-gray-100 text-gray-700 py-3 rounded-xl hover:bg-gray-200 transition-colors font-semibold",
                        ),
                        class_name="animate-in fade-in slide-in-from-bottom-4 duration-500",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "Vul uw e-mailadres in en wij sturen u een link om uw wachtwoord opnieuw in te stellen.",
                            class_name="text-gray-600 mb-8 text-center text-sm leading-relaxed",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "E-mailadres",
                                class_name="block text-sm font-bold text-gray-700 mb-2",
                            ),
                            rx.el.input(
                                on_change=ForgotPasswordState.set_email,
                                type="email",
                                placeholder="naam@voorbeeld.nl",
                                class_name="w-full rounded-xl border-gray-300 px-4 py-3 border focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 outline-none transition-all shadow-sm placeholder:text-gray-400 text-gray-900",
                                default_value=ForgotPasswordState.email,
                            ),
                            rx.cond(
                                ForgotPasswordState.error_message != "",
                                rx.el.div(
                                    rx.icon("circle-alert", class_name="w-4 h-4 mr-2"),
                                    ForgotPasswordState.error_message,
                                    class_name="flex items-center text-red-600 text-sm mt-2 animate-in fade-in slide-in-from-top-1",
                                ),
                            ),
                            class_name="mb-6",
                        ),
                        rx.el.button(
                            rx.cond(
                                ForgotPasswordState.is_loading,
                                rx.el.div(
                                    rx.spinner(class_name="w-5 h-5 text-white mr-2"),
                                    "Verzenden...",
                                    class_name="flex items-center justify-center",
                                ),
                                "Verstuur Reset Link",
                            ),
                            on_click=ForgotPasswordState.send_reset_email,
                            disabled=ForgotPasswordState.is_loading,
                            class_name="w-full bg-emerald-600 text-white py-3 rounded-xl hover:bg-emerald-700 transition-all font-bold shadow-md hover:shadow-lg hover:-translate-y-0.5 disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-md",
                        ),
                        rx.el.div(
                            rx.el.a(
                                "← Terug naar Inloggen",
                                href="/login",
                                class_name="text-sm text-gray-500 hover:text-emerald-600 font-medium transition-colors",
                            ),
                            class_name="text-center mt-8 pt-6 border-t border-gray-100",
                        ),
                        class_name="animate-in fade-in duration-500",
                    ),
                ),
                class_name="max-w-md mx-auto bg-white p-8 md:p-10 rounded-2xl shadow-xl border border-gray-100",
            ),
            class_name="container mx-auto px-4 py-20 min-h-[calc(100vh-200px)] flex items-center justify-center",
        )
    )