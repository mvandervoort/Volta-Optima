import reflex as rx


def info_tooltip(text: str) -> rx.Component:
    return rx.tooltip(
        rx.icon("info", class_name="w-4 h-4 text-gray-400 cursor-help ml-1"),
        content=text,
        content_props={
            "class_name": "bg-white text-gray-700 text-xs p-3 rounded-lg border border-emerald-200 shadow-xl max-w-xs z-50 leading-relaxed"
        },
        side="top",
        delay_duration=200,
    )