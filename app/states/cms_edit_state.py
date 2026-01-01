import reflex as rx
from app.services.cms_service import CMSService
import logging
import re


class CMSEditState(rx.State):
    content_id: str = ""
    title: str = ""
    slug: str = ""
    content_html: str = ""
    excerpt: str = ""
    status: str = "draft"
    language: str = "en"
    category_id: str = ""
    meta_title: str = ""
    meta_description: str = ""
    requires_auth: bool = False
    required_role: str = "any"
    show_in_kb: bool = False
    categories: list[dict[str, str]] = []
    saving: bool = False
    message: str = ""
    uploaded_images: list[str] = []
    is_uploading: bool = False
    show_preview: bool = False
    show_settings_panel: bool = True
    focus_mode: bool = False

    @rx.event
    def toggle_settings_panel(self):
        self.show_settings_panel = not self.show_settings_panel

    @rx.event
    def toggle_focus_mode(self):
        self.focus_mode = not self.focus_mode

    @rx.event
    def on_load(self):
        self.categories = CMSService.list_categories()
        params = self.router.page.params
        content_id = params.get("id", "")
        if content_id and content_id != "new":
            self.content_id = content_id
            self.load_content()
        else:
            self.reset_form()

    @rx.event
    def load_content(self):
        try:
            data = CMSService.get_content(self.content_id)
            if data:
                self.title = str(data.get("title") or "")
                self.slug = str(data.get("slug") or "")
                self.content_html = str(data.get("content_html") or "")
                self.excerpt = str(data.get("excerpt") or "")
                self.status = str(data.get("status") or "draft")
                self.language = str(data.get("language") or "en")
                cat_id = data.get("category_id")
                self.category_id = str(cat_id) if cat_id else ""
                self.meta_title = str(data.get("meta_title") or "")
                self.meta_description = str(data.get("meta_description") or "")
                req_auth = data.get("requires_auth")
                self.requires_auth = bool(req_auth) if req_auth is not None else False
                self.required_role = str(data.get("required_role") or "any")
                kb_vis = data.get("show_in_kb")
                self.show_in_kb = bool(kb_vis) if kb_vis is not None else False
            else:
                rx.toast.error(f"Could not load content with ID: {self.content_id}")
        except Exception as e:
            logging.exception(f"Error loading content: {e}")
            rx.toast.error("Error loading content")

    @rx.event
    def reset_form(self):
        self.content_id = ""
        self.title = ""
        self.slug = ""
        self.content_html = ""
        self.excerpt = ""
        self.status = "draft"
        self.language = "en"
        self.category_id = ""
        self.meta_title = ""
        self.meta_description = ""
        self.requires_auth = False
        self.required_role = "any"
        self.show_in_kb = False
        self.uploaded_images = []
        self.message = ""

    @rx.event
    def set_title(self, value: str):
        self.title = str(value) if value is not None else ""
        if not self.slug and self.title:
            s = self.title.lower()
            s = re.sub("[^a-z0-9\\s-]", "", s)
            s = re.sub("\\s+", "-", s)
            self.slug = s.strip("-")

    @rx.event
    def set_slug(self, value: str):
        self.slug = str(value) if value is not None else ""

    @rx.event
    def generate_slug_from_title(self):
        if not self.slug and self.title:
            s = self.title.lower()
            s = re.sub("[^a-z0-9\\s-]", "", s)
            s = re.sub("\\s+", "-", s)
            self.slug = s.strip("-")

    @rx.event
    def set_content_html(self, value: str):
        self.content_html = str(value) if value is not None else ""

    @rx.event
    def set_excerpt(self, value: str):
        self.excerpt = str(value) if value is not None else ""

    @rx.event
    def set_status(self, value: str):
        self.status = str(value) if value is not None else "draft"

    @rx.event
    def set_language(self, value: str):
        self.language = str(value) if value is not None else "en"

    @rx.event
    def set_category_id(self, value: str):
        self.category_id = str(value) if value is not None else ""

    @rx.event
    def set_meta_title(self, value: str):
        self.meta_title = str(value) if value is not None else ""

    @rx.event
    def set_meta_description(self, value: str):
        self.meta_description = str(value) if value is not None else ""

    @rx.event
    def set_requires_auth(self, value: bool | str):
        if isinstance(value, str):
            self.requires_auth = value.lower() == "true"
        else:
            self.requires_auth = bool(value)

    @rx.event
    def set_required_role(self, value: str):
        self.required_role = str(value) if value is not None else "any"

    @rx.event
    def set_show_in_kb(self, value: bool | str):
        if isinstance(value, str):
            self.show_in_kb = value.lower() == "true"
        else:
            self.show_in_kb = bool(value)

    @rx.event
    async def save_post(self):
        self.saving = True
        yield
        if not self.slug and self.title:
            s = self.title.lower()
            s = re.sub("[^a-z0-9\\s-]", "", s)
            s = re.sub("\\s+", "-", s)
            self.slug = s.strip("-")
        if not self.slug:
            yield rx.toast.error("Slug is required")
            self.saving = False
            return
        if not self.content_id:
            base_slug = self.slug
            counter = 1
            while True:
                existing = CMSService.get_content_by_slug(self.slug)
                if existing:
                    self.slug = f"{base_slug}-{counter}"
                    counter += 1
                    if counter > 100:
                        break
                else:
                    break
        data = {
            "title": self.title,
            "slug": self.slug,
            "content_html": self.content_html,
            "excerpt": self.excerpt,
            "status": self.status,
            "language": self.language,
            "category_id": self.category_id if self.category_id else None,
            "meta_title": self.meta_title,
            "meta_description": self.meta_description,
            "requires_auth": self.requires_auth,
            "required_role": self.required_role,
            "show_in_kb": self.show_in_kb,
        }
        try:
            if self.content_id:
                existing = CMSService.get_content_by_slug(self.slug)
                if existing and str(existing.get("id")) != self.content_id:
                    yield rx.toast.error(
                        "This slug is already in use by another post. Please choose a different one."
                    )
                    self.saving = False
                    return
            if self.content_id:
                CMSService.update_content(self.content_id, data)
                self.message = "Post updated successfully!"
                yield rx.toast.success(self.message)
            else:
                res = CMSService.create_content(data)
                if res:
                    self.content_id = res["id"]
                    self.message = "Post created successfully!"
                    yield rx.toast.success(self.message)
                    yield rx.redirect(f"/admin/cms/editor/{self.content_id}")
                else:
                    yield rx.toast.error("Failed to create post (no response)")
        except Exception as e:
            error_msg = str(e).lower()
            if (
                "23505" in error_msg
                or "duplicate key" in error_msg
                or "unique constraint" in error_msg
            ):
                yield rx.toast.error(
                    "A post with this slug already exists. Please choose a different slug."
                )
            else:
                logging.exception(f"Error saving post: {e}")
                yield rx.toast.error(f"Failed to save post: {str(e)}")
        self.saving = False

    @rx.event
    async def handle_image_upload(self, files: list[rx.UploadFile]):
        self.is_uploading = True
        try:
            for file in files:
                upload_data = await file.read()
                upload_dir = rx.get_upload_dir()
                upload_dir.mkdir(parents=True, exist_ok=True)
                filename = f"{file.name}"
                outfile = upload_dir / filename
                with outfile.open("wb") as f:
                    f.write(upload_data)
                self.uploaded_images.append(filename)
            rx.toast.success(f"Uploaded {len(files)} images")
        except Exception as e:
            logging.exception(f"Error uploading images: {e}")
            rx.toast.error("Failed to upload images")
        self.is_uploading = False

    @rx.event
    def toggle_preview(self):
        self.show_preview = not self.show_preview