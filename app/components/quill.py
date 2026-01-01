import reflex as rx


class ReactQuill(rx.Component):
    library = "react-quill-new"
    tag = "ReactQuill"
    is_default = True
    lib_dependencies: list[str] = ["quill-resize-image"]
    theme: rx.Var[str] = "snow"
    value: rx.Var[str]
    on_change: rx.EventHandler[lambda v: [v]]
    modules: rx.Var[dict]
    formats: rx.Var[list]
    placeholder: rx.Var[str]
    read_only: rx.Var[bool]

    def _get_custom_code(self) -> str:
        return """
import 'react-quill-new/dist/quill.snow.css';
import { Quill } from 'react-quill-new';
import ResizeModule from 'quill-resize-image';

Quill.register('modules/resize', ResizeModule);
"""


toolbar_options = [
    [{"header": [1, 2, 3, 4, 5, 6, False]}],
    ["bold", "italic", "underline", "strike"],
    ["blockquote", "code-block"],
    [{"list": "ordered"}, {"list": "bullet"}],
    [{"script": "sub"}, {"script": "super"}],
    [{"indent": "-1"}, {"indent": "+1"}],
    [{"direction": "rtl"}],
    [{"size": ["small", False, "large", "huge"]}],
    [{"color": []}, {"background": []}],
    [{"font": []}],
    [{"align": []}],
    ["link", "image", "video"],
    ["clean"],
]
default_modules = {
    "toolbar": toolbar_options,
    "clipboard": {"matchVisual": False},
    "resize": {"locale": {}},
}
default_formats = [
    "header",
    "font",
    "size",
    "bold",
    "italic",
    "underline",
    "strike",
    "blockquote",
    "list",
    "bullet",
    "indent",
    "link",
    "image",
    "video",
    "align",
    "color",
    "background",
    "direction",
    "script",
    "code-block",
]


def quill(**props):
    if "modules" not in props:
        props["modules"] = default_modules
    if "formats" not in props:
        props["formats"] = default_formats
    return ReactQuill.create(**props)