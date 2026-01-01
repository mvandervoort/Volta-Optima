import reflex as rx
from app.services.supabase_client import supabase
import logging


class AdminUsersState(rx.State):
    users: list[dict[str, object]] = []
    is_loading: bool = False
    error: str = ""
    selected_user: dict[str, object] = {}
    is_detail_open: bool = False

    @rx.event
    def load_users(self):
        self.is_loading = True
        self.error = ""
        try:
            if not supabase:
                self.users = []
                self.error = "Supabase client not initialized"
                return
            try:
                response = supabase.auth.admin.list_users()
                raw_users = response
                user_list = (
                    raw_users
                    if isinstance(raw_users, list)
                    else getattr(raw_users, "users", [])
                )
                self.users = []
                for user in user_list:
                    app_meta = getattr(user, "app_metadata", {})
                    user_meta = getattr(user, "user_metadata", {})
                    self.users.append(
                        {
                            "id": getattr(user, "id", ""),
                            "email": getattr(user, "email", ""),
                            "role": app_meta.get("role", "user"),
                            "last_login": getattr(user, "last_sign_in_at", "Never"),
                            "created_at": getattr(user, "created_at", ""),
                            "status": "Active"
                            if getattr(user, "email_confirmed_at", None)
                            else "Unconfirmed",
                            "metadata": user_meta,
                            "app_metadata": app_meta,
                        }
                    )
            except Exception as e:
                error_msg = str(e).lower()
                if "user not allowed" in error_msg or "not allowed" in error_msg:
                    logging.warning(
                        f"Permission denied listing users (expected without service_role): {e}"
                    )
                    self.error = "Service Role Key required to view user list."
                else:
                    logging.exception(f"Could not list users via auth.admin: {e}")
                    self.error = "Could not fetch users. Service role key required."
                self.users = []
        except Exception as e:
            logging.exception(f"Error loading users: {e}")
            self.error = str(e)
        finally:
            self.is_loading = False

    @rx.event
    def open_detail(self, user: dict[str, object]):
        self.selected_user = user
        self.is_detail_open = True

    @rx.event
    def close_detail(self):
        self.is_detail_open = False

    @rx.event
    def copy_sql(self):
        return rx.set_clipboard("""UPDATE auth.users
SET raw_app_meta_data = raw_app_meta_data || '{"role": "admin"}'::jsonb
WHERE email = 'user@example.com';""")