import reflex as rx


def email_confirmation_modal(
    open_var: rx.Var[bool], on_close: rx.EventHandler
) -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 animate-in fade-in duration-200"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "circle-check", class_name="w-16 h-16 text-emerald-500 mb-4"
                        ),
                        class_name="flex justify-center",
                    ),
                    rx.radix.primitives.dialog.title(
                        "E-mail Verzonden",
                        class_name="text-xl font-bold text-center text-gray-900 mb-2",
                    ),
                    rx.radix.primitives.dialog.description(
                        "Uw resultaten zijn succesvol verzonden naar uw e-mailadres.",
                        class_name="text-center text-gray-600 mb-8",
                    ),
                    rx.radix.primitives.dialog.close(
                        rx.el.button(
                            "Sluiten",
                            on_click=on_close,
                            class_name="w-full bg-emerald-600 text-white font-bold py-3 rounded-xl hover:bg-emerald-700 transition-colors shadow-lg hover:shadow-emerald-200/50 outline-none",
                        )
                    ),
                    class_name="flex flex-col w-full",
                ),
                class_name="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl p-8 shadow-2xl w-[90vw] max-w-sm z-[60] outline-none animate-in zoom-in-95 duration-200",
            ),
        ),
        open=open_var,
        on_open_change=lambda _: on_close(),
    )