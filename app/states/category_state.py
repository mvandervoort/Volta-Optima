import reflex as rx
from app.services.cms_service import CMSService
import logging


class CategoryState(rx.State):
    categories: list[dict[str, object]] = []
    search_query: str = ""
    is_loading: bool = False
    show_modal: bool = False
    is_editing: bool = False
    current_category_id: str = ""
    form_name: str = ""
    form_slug: str = ""
    form_description: str = ""
    delete_confirm_open: bool = False
    item_to_delete: str = ""

    @rx.event
    def on_load(self):
        self.load_categories()

    @rx.event
    def load_categories(self):
        self.is_loading = True
        try:
            self.categories = CMSService.list_categories()
        except Exception as e:
            logging.exception(f"Error loading categories: {e}")
            rx.toast.error("Failed to load categories")
        self.is_loading = False

    @rx.event
    def set_search_query(self, query: str):
        self.search_query = query

    @rx.var
    def filtered_categories(self) -> list[dict[str, object]]:
        if not self.search_query:
            return self.categories
        query = self.search_query.lower()
        return [
            c
            for c in self.categories
            if query in str(c.get("name", "")).lower()
            or query in str(c.get("slug", "")).lower()
        ]

    @rx.event
    def set_form_name(self, value: str):
        self.form_name = value
        if not self.is_editing and (not self.form_slug):
            self.form_slug = value.lower().replace(" ", "-").replace(".", "")

    @rx.event
    def set_form_slug(self, value: str):
        self.form_slug = value

    @rx.event
    def set_form_description(self, value: str):
        self.form_description = value

    @rx.event
    def open_add_modal(self):
        self.is_editing = False
        self.current_category_id = ""
        self.form_name = ""
        self.form_slug = ""
        self.form_description = ""
        self.show_modal = True

    @rx.event
    def open_edit_modal(self, category: dict):
        self.is_editing = True
        self.current_category_id = category.get("id", "")
        self.form_name = category.get("name", "")
        self.form_slug = category.get("slug", "")
        self.form_description = category.get("description", "")
        self.show_modal = True

    @rx.event
    def close_modal(self):
        self.show_modal = False

    @rx.event
    def save_category(self):
        if not self.form_name or not self.form_slug:
            rx.toast.error("Name and Slug are required")
            return
        data = {
            "name": self.form_name,
            "slug": self.form_slug,
            "description": self.form_description,
        }
        try:
            if self.is_editing:
                CMSService.update_category(self.current_category_id, data)
                rx.toast.success("Category updated successfully")
            else:
                CMSService.create_category(data)
                rx.toast.success("Category created successfully")
            self.show_modal = False
            self.load_categories()
        except Exception as e:
            logging.exception(f"Error saving category: {e}")
            rx.toast.error(f"Failed to save category: {str(e)}")

    @rx.event
    def prompt_delete(self, category_id: str):
        self.item_to_delete = category_id
        self.delete_confirm_open = True

    @rx.event
    def cancel_delete(self):
        self.delete_confirm_open = False
        self.item_to_delete = ""

    @rx.event
    def confirm_delete(self):
        if self.item_to_delete:
            if CMSService.delete_category(self.item_to_delete):
                rx.toast.success("Category deleted")
                self.load_categories()
            else:
                rx.toast.error("Failed to delete category")
        self.delete_confirm_open = False
        self.item_to_delete = ""