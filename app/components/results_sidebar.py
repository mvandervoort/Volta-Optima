import reflex as rx
from app.states.base_state import State


def results_sidebar_action(
    text: str,
    icon: str,
    disabled: rx.Var[bool] | bool = True,
    coming_soon: bool = False,
    on_click: rx.event.EventType = rx.noop,
) -> rx.Component:
    return rx.el.button(
        rx.icon(
            icon,
            class_name=rx.cond(disabled, "text-gray-400", "text-emerald-600")
            + " w-4 h-4 mr-3",
        ),
        rx.el.span(text, class_name="flex-1 text-left"),
        rx.cond(
            coming_soon,
            rx.el.span(
                "Zodra...",
                class_name="text-[10px] bg-gray-100 text-gray-400 px-1.5 py-0.5 rounded uppercase font-bold tracking-tighter",
            ),
            None,
        ),
        on_click=on_click,
        disabled=disabled,
        class_name=rx.cond(
            disabled,
            "flex items-center w-full px-3 py-2.5 text-sm font-medium text-gray-400 cursor-not-allowed rounded-xl mb-2 transition-colors border border-transparent opacity-60",
            "flex items-center w-full px-3 py-2.5 text-sm font-bold text-emerald-700 hover:text-emerald-800 rounded-xl mb-2 transition-all group shadow-sm bg-emerald-50 border border-emerald-200 hover:bg-emerald-100 hover:border-emerald-300 hover:-translate-y-0.5",
        ),
        title=rx.cond(coming_soon, "Binnenkort beschikbaar", text),
    )


from app.states.results_state import ResultsState


def results_sidebar() -> rx.Component:
    return rx.el.aside(
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.icon("circle_user_round", class_name="w-5 h-5 text-emerald-600"),
                    rx.el.h3(
                        "MIJN DATA",
                        class_name="text-xs font-bold text-gray-500 uppercase tracking-wider ml-3",
                    ),
                    class_name="flex items-center px-4 mb-6",
                ),
                rx.el.nav(
                    results_sidebar_action(
                        "Download Alle Data", "download", coming_soon=True
                    ),
                    results_sidebar_action(
                        "Exporteer naar PDF", "file-text", coming_soon=True
                    ),
                    results_sidebar_action(
                        "Verwijder Selectie",
                        "trash-2",
                        disabled=~ResultsState.has_selection,
                        coming_soon=False,
                        on_click=ResultsState.open_confirm_dialog,
                    ),
                    class_name="space-y-1 mb-10",
                ),
            ),
            rx.el.div(
                rx.el.h3(
                    "ANALYSE FILTERS",
                    class_name="px-4 text-xs font-bold text-gray-500 uppercase tracking-wider mb-4",
                ),
                rx.el.div(
                    rx.el.p(
                        "Geavanceerde filters worden momenteel ontwikkeld.",
                        class_name="px-4 text-xs text-gray-400 italic leading-relaxed",
                    ),
                    class_name="mb-10",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.icon("sparkles", class_name="w-4 h-4 text-emerald-500 mr-2"),
                    rx.el.span(
                        "Binnenkort", class_name="text-xs font-bold text-emerald-700"
                    ),
                    class_name="flex items-center px-4 mb-2",
                ),
                rx.el.p(
                    "Koppel uw resultaten direct aan nieuwe berekeningen voor nog nauwkeuriger advies.",
                    class_name="px-4 text-xs text-emerald-600/70 leading-relaxed",
                ),
                class_name="mt-auto p-4 bg-emerald-50/50 rounded-2xl mx-2 border border-emerald-100/50",
            ),
            class_name="py-6 pr-6 flex flex-col h-full",
        ),
        class_name="hidden md:block w-64 shrink-0 border-r border-gray-200 min-h-[calc(100vh-5rem)]",
    )