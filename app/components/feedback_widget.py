import reflex as rx
from app.states.feedback_state import FeedbackState


def feedback_button() -> rx.Component:
    return rx.el.button(
        rx.el.div(
            rx.icon("square-pen", class_name="w-5 h-5 text-amber-950 mb-2"),
            rx.el.span(
                "Feedback",
                class_name="text-xs font-bold text-amber-950 uppercase tracking-widest [writing-mode:vertical-rl] rotate-180",
            ),
            class_name="flex flex-col items-center",
        ),
        on_click=FeedbackState.toggle_modal,
        class_name="fixed right-0 top-1/2 -translate-y-1/2 z-[60] py-4 px-2.5 bg-gradient-to-b from-amber-300 to-amber-500 rounded-l-xl shadow-[-4px_0_15px_rgba(0,0,0,0.1)] hover:pr-4 transition-all duration-300 border-y border-l border-white/30",
        title="Feedback geven",
    )


def feedback_modal() -> rx.Component:
    return rx.fragment(
        rx.cond(
            FeedbackState.is_open & ~FeedbackState.is_hidden_for_screenshot,
            rx.el.div(
                on_click=FeedbackState.toggle_modal,
                class_name="fixed inset-0 bg-black/40 backdrop-blur-sm z-[70] animate-in fade-in duration-300",
            ),
        ),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.h2(
                            "Feedback", class_name="text-xl font-bold text-gray-900"
                        ),
                        rx.el.button(
                            rx.icon(
                                "x",
                                class_name="w-6 h-6 text-gray-400 hover:text-gray-600",
                            ),
                            on_click=FeedbackState.toggle_modal,
                            class_name="p-1 hover:bg-gray-100 rounded-full transition-colors",
                        ),
                        class_name="flex items-center justify-between p-6 border-b",
                    ),
                    rx.el.div(
                        rx.el.input(
                            class_name="hidden",
                            on_change=FeedbackState.set_website_url,
                            default_value=FeedbackState.website_url,
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Type Feedback",
                                class_name="block text-sm font-bold text-gray-700 mb-2",
                            ),
                            rx.el.select(
                                rx.el.option("Suggestie", value="Suggestion"),
                                rx.el.option("Bug Melding", value="Bug Report"),
                                rx.el.option("Vraag", value="Question"),
                                rx.el.option("Anders", value="Other"),
                                on_change=FeedbackState.set_feedback_type,
                                value=FeedbackState.feedback_type,
                                class_name="w-full p-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 outline-none bg-white appearance-none",
                            ),
                            class_name="mb-6",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Uw Bericht",
                                class_name="block text-sm font-bold text-gray-700 mb-2",
                            ),
                            rx.el.textarea(
                                placeholder="Wat kunnen we verbeteren?",
                                on_change=[
                                    FeedbackState.set_description,
                                    FeedbackState.mark_form_interaction,
                                ],
                                default_value=FeedbackState.description,
                                class_name="w-full h-32 p-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-emerald-500 outline-none resize-none bg-white",
                            ),
                            class_name="mb-6",
                        ),
                        rx.el.div(
                            rx.el.label(
                                "Screenshot (optioneel)",
                                class_name="block text-sm font-bold text-gray-700 mb-2",
                            ),
                            rx.cond(
                                FeedbackState.has_screenshot,
                                rx.el.div(
                                    rx.el.img(
                                        src=FeedbackState.screenshot_data,
                                        class_name="w-full h-auto rounded-lg border border-gray-200 shadow-sm",
                                    ),
                                    rx.el.button(
                                        rx.icon("trash-2", class_name="w-4 h-4 mr-2"),
                                        "Verwijder screenshot",
                                        on_click=FeedbackState.clear_screenshot,
                                        class_name="absolute top-2 right-2 bg-white/90 text-red-600 p-2 rounded-lg text-xs font-bold shadow-md hover:bg-red-50 transition-colors flex items-center",
                                    ),
                                    class_name="relative",
                                ),
                                rx.el.button(
                                    rx.cond(
                                        FeedbackState.is_capturing,
                                        rx.spinner(
                                            class_name="w-5 h-5 text-emerald-600 mr-2"
                                        ),
                                        rx.icon(
                                            "camera",
                                            class_name="w-5 h-5 text-emerald-600 mr-2",
                                        ),
                                    ),
                                    rx.cond(
                                        FeedbackState.is_capturing,
                                        "Vastleggen...",
                                        "Maak Screenshot van pagina",
                                    ),
                                    on_click=FeedbackState.capture_screenshot,
                                    disabled=FeedbackState.is_capturing,
                                    class_name="w-full flex items-center justify-center p-4 border-2 border-dashed border-emerald-200 rounded-xl text-emerald-700 font-medium hover:bg-emerald-50 transition-colors bg-white",
                                ),
                            ),
                            class_name="mb-10",
                        ),
                        rx.el.button(
                            rx.cond(
                                FeedbackState.is_submitting,
                                "Verzenden...",
                                "Feedback Verzenden",
                            ),
                            on_click=FeedbackState.submit_feedback,
                            disabled=FeedbackState.is_submitting,
                            class_name="w-full py-4 bg-emerald-600 text-white font-bold rounded-xl hover:bg-emerald-700 transition-all shadow-md hover:shadow-emerald-200/50 disabled:opacity-70",
                        ),
                        class_name="flex-1 overflow-y-auto p-6",
                    ),
                    class_name="flex flex-col h-full feedback-widget-container",
                ),
                class_name="bg-white h-full shadow-2xl",
            ),
            class_name=rx.cond(
                FeedbackState.is_open & ~FeedbackState.is_hidden_for_screenshot,
                "fixed top-0 right-0 h-full w-full sm:w-[400px] z-[80] transition-transform duration-300 transform translate-x-0",
                "fixed top-0 right-0 h-full w-full sm:w-[400px] z-[80] transition-transform duration-300 transform translate-x-full",
            ),
        ),
    )


def feedback_widget() -> rx.Component:
    current_path = rx.State.router.page.path
    is_advice_page = (
        (current_path == "/advice-themes")
        | (current_path == "/solar")
        | (current_path == "/battery")
        | (current_path == "/dakscan")
        | (current_path == "/warm-water")
        | (current_path == "/advice/simple/battery")
        | (current_path == "/advice/advanced/battery")
        | (current_path == "/advice/solar-theme")
    )
    return rx.cond(is_advice_page, rx.fragment(feedback_button(), feedback_modal()))