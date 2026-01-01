import reflex as rx
from .base_state import State
from app.services.supabase_client import supabase
import logging


class ResetPasswordState(State):
    new_password: str = ""
    confirm_password: str = ""
    is_loading: bool = False
    error_message: str = ""
    success: bool = False
    access_token: str = ""
    refresh_token: str = ""
    is_token_set: bool = False

    @rx.event
    def on_load(self):
        """Trigger client-side script to extract hash fragment tokens."""
        return rx.call_script(
            "window.location.hash", callback=ResetPasswordState.receive_tokens
        )

    @rx.event
    def receive_tokens(self, hash_fragment: str):
        """Parse tokens from the URL hash fragment returned by client script."""
        if not hash_fragment or "access_token" not in hash_fragment:
            return
        if hash_fragment.startswith("#"):
            hash_fragment = hash_fragment[1:]
        params = {}
        for pair in hash_fragment.split("&"):
            if "=" in pair:
                key, value = pair.split("=", 1)
                params[key] = value
        access_token = params.get("access_token")
        refresh_token = params.get("refresh_token")
        if access_token and refresh_token:
            self.access_token = access_token
            self.refresh_token = refresh_token
            if supabase:
                try:
                    supabase.auth.set_session(access_token, refresh_token)
                    self.is_token_set = True
                    user_response = supabase.auth.get_user()
                    if user_response and user_response.user:
                        self.user = {
                            "id": user_response.user.id,
                            "email": user_response.user.email,
                            "app_metadata": user_response.user.app_metadata,
                            "user_metadata": user_response.user.user_metadata,
                            "aud": user_response.user.aud,
                            "created_at": user_response.user.created_at,
                        }
                except Exception as e:
                    logging.exception(f"Error setting session from tokens: {e}")
                    self.error_message = "Ongeldige of verlopen link."

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value
        self.error_message = ""

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value
        self.error_message = ""

    @rx.event
    async def reset_password(self):
        self.is_loading = True
        self.error_message = ""
        self.success = False
        if not self.new_password or not self.confirm_password:
            self.error_message = "Vul alstublieft beide wachtwoordvelden in."
            self.is_loading = False
            return
        if len(self.new_password) < 8:
            self.error_message = "Wachtwoord moet minimaal 8 tekens bevatten."
            self.is_loading = False
            return
        if self.new_password != self.confirm_password:
            self.error_message = "Wachtwoorden komen niet overeen."
            self.is_loading = False
            return
        try:
            if not supabase:
                import asyncio

                await asyncio.sleep(1)
                self.success = True
                yield rx.toast.success("Wachtwoord succesvol gewijzigd (Demo).")
                self.is_loading = False
                return
            if not self.is_token_set and self.access_token and self.refresh_token:
                supabase.auth.set_session(self.access_token, self.refresh_token)
            response = supabase.auth.update_user({"password": self.new_password})
            if response and (
                response.user or (hasattr(response, "data") and response.data.user)
            ):
                self.success = True
                yield rx.toast.success("Wachtwoord succesvol gewijzigd.")
            else:
                self.error_message = "Kon wachtwoord niet wijzigen. Probeer opnieuw een reset link aan te vragen."
        except Exception as e:
            logging.exception(f"Password update error: {e}")
            self.error_message = "Er is een fout opgetreden. Mogelijk is uw sessie verlopen. Vraag een nieuwe link aan."
        finally:
            self.is_loading = False