import reflex as rx
from app.states.cms_edit_state import CMSEditState
from app.components.admin_sidebar import admin_sidebar
from app.components.quill import quill
from app.components.protected_guard import admin_guard


def preview_modal() -> rx.Component:
    return rx.cond(
        CMSEditState.show_preview,
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    rx.el.h2("Voorbeeld", class_name="text-xl font-bold"),
                    rx.el.button(rx.icon("x"), on_click=CMSEditState.toggle_preview),
                    class_name="flex justify-between items-center p-4 border-b",
                ),
                rx.el.div(
                    rx.html(CMSEditState.content_html),
                    class_name="p-8 prose max-w-none overflow-y-auto h-[calc(90vh-70px)]",
                ),
                class_name="bg-white w-full max-w-4xl h-[90vh] rounded-xl shadow-2xl m-auto relative flex flex-col",
            ),
            class_name="fixed inset-0 bg-black/50 z-[100] flex items-center justify-center p-4",
        ),
    )


def focus_mode_overlay() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                "Focusmodus",
                class_name="text-sm font-bold uppercase tracking-wider text-gray-500",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("minimize-2", class_name="w-5 h-5"),
                    on_click=CMSEditState.toggle_focus_mode,
                    class_name="p-2 text-gray-500 hover:text-gray-900 transition-colors rounded-full hover:bg-gray-100",
                    title="Focusmodus verlaten",
                ),
                rx.el.button(
                    rx.cond(CMSEditState.saving, "Opslaan...", "Opslaan"),
                    on_click=CMSEditState.save_post,
                    class_name="ml-4 px-4 py-2 bg-emerald-600 text-white rounded-md hover:bg-emerald-700 text-sm font-medium",
                ),
                class_name="flex items-center",
            ),
            class_name="fixed top-0 left-0 right-0 h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 z-[60]",
        ),
        rx.el.div(
            rx.el.input(
                placeholder="Titel bericht",
                on_change=CMSEditState.set_title,
                class_name="text-4xl font-bold text-gray-900 placeholder:text-gray-300 outline-none w-full bg-transparent mb-8",
                default_value=CMSEditState.title,
            ),
            quill(
                value=CMSEditState.content_html,
                on_change=CMSEditState.set_content_html,
                theme="snow",
                placeholder="Begin met schrijven...",
            ),
            class_name="max-w-4xl mx-auto pt-24 px-8 pb-12 h-screen overflow-y-auto prose max-w-none [&_.ql-editor]:min-h-[calc(100vh-250px)] [&_.ql-container]:border-0 [&_.ql-toolbar]:border-0 [&_.ql-toolbar]:sticky [&_.ql-toolbar]:top-0 [&_.ql-toolbar]:bg-white [&_.ql-toolbar]:z-10",
        ),
        class_name="fixed inset-0 bg-white z-[55]",
    )


def editor_header() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                rx.cond(CMSEditState.content_id, "Bericht bewerken", "Nieuw bericht"),
                class_name="text-xl font-bold text-gray-900",
            ),
            rx.cond(
                CMSEditState.message != "",
                rx.el.span(
                    CMSEditState.message,
                    class_name="ml-4 text-sm text-emerald-600 font-medium animate-in fade-in",
                ),
            ),
            class_name="flex items-center",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("eye", class_name="w-4 h-4 mr-2"),
                "Voorbeeld",
                on_click=CMSEditState.toggle_preview,
                class_name="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors",
            ),
            rx.el.button(
                rx.icon("maximize-2", class_name="w-4 h-4 mr-2"),
                "Focus",
                on_click=CMSEditState.toggle_focus_mode,
                class_name="flex items-center px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-md transition-colors mr-2",
            ),
            rx.el.button(
                rx.icon("panel-right", class_name="w-4 h-4"),
                on_click=CMSEditState.toggle_settings_panel,
                class_name=rx.cond(
                    CMSEditState.show_settings_panel,
                    "p-2 text-emerald-600 bg-emerald-50 rounded-md transition-colors mr-4",
                    "p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-md transition-colors mr-4",
                ),
                title="Toggle Settings Panel",
            ),
            rx.el.div(class_name="h-6 w-px bg-gray-200 mr-4"),
            rx.el.button(
                "Annuleren",
                on_click=rx.redirect("/admin/cms"),
                class_name="px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors mr-2",
            ),
            rx.el.button(
                rx.cond(CMSEditState.saving, "Opslaan...", "Opslaan"),
                on_click=CMSEditState.save_post,
                disabled=CMSEditState.saving,
                class_name="px-6 py-2 bg-emerald-600 hover:bg-emerald-700 text-white text-sm font-bold rounded-lg shadow-sm transition-all disabled:opacity-70",
            ),
            class_name="flex items-center",
        ),
        class_name="h-16 border-b border-gray-200 bg-white flex items-center justify-between px-6 shrink-0 z-20",
    )


def main_writing_area() -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.input(
                placeholder="Titel bericht",
                on_change=CMSEditState.set_title,
                class_name="text-3xl font-bold text-gray-900 placeholder:text-gray-300 outline-none w-full bg-transparent mb-4",
                default_value=CMSEditState.title,
            ),
            rx.el.div(
                rx.el.span(
                    "slug:",
                    class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mr-2",
                ),
                rx.el.input(
                    placeholder="url-slug-hier",
                    on_change=CMSEditState.set_slug,
                    class_name="text-sm text-gray-600 font-mono bg-transparent outline-none w-full",
                    default_value=CMSEditState.slug,
                ),
                class_name="flex items-center mb-8 bg-gray-50 p-2 rounded-md border border-gray-100",
            ),
            class_name="max-w-4xl mx-auto w-full px-8 pt-8",
        ),
        rx.el.div(
            quill(
                value=CMSEditState.content_html,
                on_change=CMSEditState.set_content_html,
                theme="snow",
                placeholder="Schrijf iets geweldigs...",
            ),
            class_name="flex-1 max-w-4xl mx-auto w-full px-8 prose max-w-none [&_.ql-container]:border-0 [&_.ql-toolbar]:border-0 [&_.ql-toolbar]:sticky [&_.ql-toolbar]:top-0 [&_.ql-toolbar]:bg-gray-50 [&_.ql-toolbar]:z-10 [&_.ql-editor]:min-h-[400px]",
        ),
        rx.el.div(
            rx.el.label(
                "Uittreksel",
                class_name="block text-xs font-bold text-gray-500 uppercase mb-2",
            ),
            rx.el.textarea(
                placeholder="Korte samenvatting voor voorvertoningen...",
                on_change=CMSEditState.set_excerpt,
                class_name="w-full h-24 p-4 rounded-lg border border-gray-200 focus:border-emerald-500 focus:ring-1 focus:ring-emerald-500 outline-none resize-none text-sm",
                default_value=CMSEditState.excerpt,
            ),
            class_name="max-w-4xl mx-auto w-full px-8 py-8 border-t border-gray-100 mt-8",
        ),
        class_name="flex-1 overflow-y-auto bg-white flex flex-col",
    )


def settings_section(
    title: str, content: rx.Component, default_open: bool = True
) -> rx.Component:
    return rx.el.details(
        rx.el.summary(
            title,
            class_name="flex items-center justify-between cursor-pointer list-none text-sm font-bold text-gray-900 py-4 px-6 hover:bg-gray-50 transition-colors border-b border-gray-100",
        ),
        rx.el.div(content, class_name="p-6 border-b border-gray-100"),
        open=default_open,
        class_name="group",
    )


def settings_sidebar() -> rx.Component:
    return rx.el.div(
        settings_section(
            "Publicatie",
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Status",
                        class_name="block text-xs font-medium text-gray-500 mb-1.5",
                    ),
                    rx.el.select(
                        rx.el.option("Concept", value="draft"),
                        rx.el.option("Gepubliceerd", value="published"),
                        value=CMSEditState.status,
                        on_change=CMSEditState.set_status,
                        class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 appearance-none",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Taal",
                        class_name="block text-xs font-medium text-gray-500 mb-1.5",
                    ),
                    rx.el.select(
                        rx.el.option("Engels", value="en"),
                        rx.el.option("Nederlands", value="nl"),
                        value=CMSEditState.language,
                        on_change=CMSEditState.set_language,
                        class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 appearance-none",
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Categorie",
                        class_name="block text-xs font-medium text-gray-500 mb-1.5",
                    ),
                    rx.el.select(
                        rx.el.option("Selecteer Categorie", value=""),
                        rx.foreach(
                            CMSEditState.categories,
                            lambda cat: rx.el.option(cat["name"], value=cat["id"]),
                        ),
                        value=CMSEditState.category_id,
                        on_change=CMSEditState.set_category_id,
                        class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 appearance-none",
                    ),
                ),
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=CMSEditState.show_in_kb,
                            on_change=CMSEditState.set_show_in_kb,
                            class_name="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 mr-2",
                        ),
                        "Tonen in Kennisbank",
                        class_name="text-sm text-gray-700 flex items-center font-medium",
                    ),
                    rx.el.p(
                        "Indien uitgevinkt, is het artikel wel openbaar via de directe link, maar verschijnt het niet in de Kennisbank overzichten.",
                        class_name="text-xs text-gray-500 mt-1 ml-6",
                    ),
                    class_name="mb-4 mt-6 pt-4 border-t border-gray-100",
                ),
            ),
        ),
        settings_section(
            "Toegangsbeheer",
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        rx.el.input(
                            type="checkbox",
                            checked=CMSEditState.requires_auth,
                            on_change=CMSEditState.set_requires_auth,
                            class_name="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500 mr-2",
                        ),
                        "Authenticatie vereist",
                        class_name="text-sm text-gray-700 flex items-center font-medium",
                    ),
                    class_name="mb-4",
                ),
                rx.cond(
                    CMSEditState.requires_auth,
                    rx.el.div(
                        rx.el.label(
                            "Vereiste Rol",
                            class_name="block text-xs font-medium text-gray-500 mb-1.5",
                        ),
                        rx.el.select(
                            rx.el.option("Elke Gebruiker", value="any"),
                            rx.el.option("Alleen Beheerder", value="admin"),
                            value=CMSEditState.required_role,
                            on_change=CMSEditState.set_required_role,
                            class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 appearance-none",
                        ),
                        class_name="animate-in fade-in slide-in-from-top-2",
                    ),
                ),
            ),
        ),
        settings_section(
            "Mediabibliotheek",
            rx.el.div(
                rx.upload.root(
                    rx.el.div(
                        rx.icon("image", class_name="w-6 h-6 text-gray-400 mb-2"),
                        rx.el.p(
                            "Afbeeldingen uploaden",
                            class_name="text-xs font-medium text-gray-600",
                        ),
                        class_name="flex flex-col items-center justify-center p-4 border-2 border-dashed border-gray-200 rounded-lg hover:border-emerald-500 hover:bg-emerald-50/30 transition-all cursor-pointer bg-gray-50",
                    ),
                    id="cms_upload_sidebar",
                    accept={"image/png": [".png"], "image/jpeg": [".jpg", ".jpeg"]},
                    multiple=True,
                    class_name="w-full mb-3",
                ),
                rx.el.div(
                    rx.foreach(
                        rx.selected_files("cms_upload_sidebar"),
                        lambda f: rx.el.div(
                            f, class_name="text-xs text-gray-500 mb-1 truncate"
                        ),
                    ),
                    class_name="mb-2",
                ),
                rx.cond(
                    rx.selected_files("cms_upload_sidebar").length() > 0,
                    rx.el.button(
                        rx.cond(
                            CMSEditState.is_uploading, "Uploaden...", "Nu uploaden"
                        ),
                        on_click=CMSEditState.handle_image_upload(
                            rx.upload_files(upload_id="cms_upload_sidebar")
                        ),
                        disabled=CMSEditState.is_uploading,
                        class_name="w-full py-2 bg-emerald-600 text-white text-xs font-bold rounded-md hover:bg-emerald-700 transition-colors mb-4",
                    ),
                ),
                rx.el.h4(
                    "Recente Afbeeldingen",
                    class_name="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3",
                ),
                rx.el.div(
                    rx.foreach(
                        CMSEditState.uploaded_images,
                        lambda img: rx.el.div(
                            rx.el.img(
                                src=rx.get_upload_url(img),
                                class_name="w-full h-24 object-cover rounded-md border border-gray-200",
                            ),
                            rx.el.div(
                                rx.el.span(
                                    img,
                                    class_name="text-xs text-gray-500 truncate flex-1",
                                ),
                                rx.el.button(
                                    rx.icon("copy", class_name="w-3 h-3"),
                                    on_click=rx.set_clipboard(rx.get_upload_url(img)),
                                    class_name="text-gray-400 hover:text-emerald-600 p-1",
                                    title="URL kopiëren",
                                ),
                                class_name="flex items-center justify-between mt-1 px-1",
                            ),
                            class_name="mb-4",
                        ),
                    ),
                    class_name="max-h-60 overflow-y-auto pr-2",
                ),
            ),
        ),
        settings_section(
            "SEO Instellingen",
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Meta Titel",
                        class_name="block text-xs font-medium text-gray-500 mb-1.5",
                    ),
                    rx.el.input(
                        on_change=CMSEditState.set_meta_title,
                        class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2",
                        default_value=CMSEditState.meta_title,
                    ),
                    class_name="mb-4",
                ),
                rx.el.div(
                    rx.el.label(
                        "Meta Omschrijving",
                        class_name="block text-xs font-medium text-gray-500 mb-1.5",
                    ),
                    rx.el.textarea(
                        on_change=CMSEditState.set_meta_description,
                        class_name="w-full rounded-md border-gray-300 text-sm focus:border-emerald-500 focus:ring-emerald-500 border px-3 py-2 h-24 resize-none",
                        default_value=CMSEditState.meta_description,
                    ),
                ),
            ),
            default_open=False,
        ),
        class_name="w-80 border-l border-gray-200 bg-white flex flex-col overflow-y-auto shrink-0",
    )


def cms_editor_page() -> rx.Component:
    return admin_guard(
        rx.el.div(
            rx.cond(CMSEditState.focus_mode, focus_mode_overlay()),
            preview_modal(),
            rx.el.div(
                admin_sidebar(),
                rx.el.div(
                    editor_header(),
                    rx.el.div(
                        main_writing_area(),
                        rx.cond(CMSEditState.show_settings_panel, settings_sidebar()),
                        class_name="flex flex-1 overflow-hidden",
                    ),
                    class_name="flex-1 flex flex-col h-screen overflow-hidden bg-gray-50",
                ),
                class_name="flex h-screen overflow-hidden",
            ),
        )
    )