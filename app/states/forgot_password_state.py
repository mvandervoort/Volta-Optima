import reflex as rx
from .base_state import State
from app.services.supabase_client import supabase
import logging


class ForgotPasswordState(State):
    email: str = ""
    is_loading: bool = False
    error_message: str = ""
    success_message: str = ""
    has_sent: bool = False

    @rx.event
    def set_email(self, email: str):
        self.email = email
        self.error_message = ""

    @rx.event
    async def send_reset_email(self):
        if not self.email:
            self.error_message = "Vul alstublieft uw e-mailadres in."
            return
        self.is_loading = True
        self.error_message = ""
        self.success_message = ""
        try:
            if not supabase:
                import asyncio

                await asyncio.sleep(1)
                self.has_sent = True
                self.success_message = "Reset link verzonden (Demo mode)."
                yield rx.toast.success("Reset link verzonden (Demo).")
            else:
                from app.constants import BASE_URL

                redirect_url = f"{BASE_URL}/reset-password"
                supabase.auth.reset_password_for_email(
                    self.email, options={"redirect_to": redirect_url}
                )
                self.has_sent = True
                self.success_message = (
                    "Als uw e-mailadres bij ons bekend is, ontvangt u een reset link."
                )
                yield rx.toast.success("Reset instructies verzonden.")
        except Exception as e:
            logging.exception(f"Password reset request error: {e}")
            self.error_message = "Er is een fout opgetreden. Probeer het later opnieuw."
            yield rx.toast.error("Er is een fout opgetreden.")
        finally:
            self.is_loading = False