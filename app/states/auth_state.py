import reflex as rx
from .base_state import State
from app.services.supabase_client import supabase
import logging


class AuthState(State):
    email: str = ""
    password: str = ""
    full_name: str = ""
    is_loading: bool = False
    error: str = ""
    redirect_url: str = ""
    reset_email: str = ""
    reset_sent: bool = False
    is_resetting: bool = False

    @rx.event
    def set_reset_email(self, email: str):
        self.reset_email = email

    @rx.event
    def set_redirect_url(self, url: str):
        self.redirect_url = url

    @rx.event
    def set_email(self, email: str):
        self.email = email

    @rx.event
    def set_password(self, password: str):
        self.password = password

    @rx.event
    def set_full_name(self, full_name: str):
        self.full_name = full_name

    def _set_user_session(self, user):
        """Helper to set user session from Supabase User object.

        ROLES MANAGEMENT:
        Roles are managed directly via Supabase Auth app_metadata.
        To make a user an admin:
        1. Go to Supabase Dashboard > Authentication > Users
        2. Find the user and click 'Edit user'
        3. In 'User Metadata' (app_metadata), add: {"role": "admin"}
        4. Save. The user must re-login to pick up the new role.
        """
        self.user = {
            "id": user.id,
            "email": user.email,
            "app_metadata": user.app_metadata,
            "user_metadata": user.user_metadata,
            "aud": user.aud,
            "created_at": user.created_at,
        }
        self.user_role = user.app_metadata.get("role", "user")

    async def _demo_login(self):
        """Fallback login for demo/testing purposes when Supabase isn't configured"""
        import asyncio

        await asyncio.sleep(1)
        self.user = {"email": self.email, "full_name": "Demo User", "id": "demo-id"}
        self.user_role = "admin" if "admin" in self.email.lower() else "user"
        self.is_loading = False
        target = self.redirect_url or "/"
        self.redirect_url = ""
        return rx.redirect(target)

    @rx.event
    async def login(self):
        self.is_loading = True
        self.error = ""
        if not self.email or not self.password:
            self.error = "Please enter both email and password"
            self.is_loading = False
            return
        try:
            if not supabase:
                await self._demo_login()
                return
            response = supabase.auth.sign_in_with_password(
                {"email": self.email, "password": self.password}
            )
            if response.user:
                self._set_user_session(response.user)
                target = self.redirect_url or "/"
                self.redirect_url = ""
                return rx.redirect(target)
        except Exception as e:
            logging.exception(f"Login error: {e}")
            self.error = str(e)
            if "Invalid login credentials" in str(e):
                self.error = "Invalid email or password."
        finally:
            self.is_loading = False

    @rx.event
    async def request_password_reset(self):
        self.is_resetting = True
        self.reset_sent = False
        if not self.reset_email:
            yield rx.toast.error("Vul alstublieft uw e-mailadres in.")
            self.is_resetting = False
            return
        try:
            if not supabase:
                import asyncio

                await asyncio.sleep(1)
                self.reset_sent = True
                yield rx.toast.success("Reset link verzonden (Demo).")
                self.is_resetting = False
                return
            from app.constants import BASE_URL

            redirect_url = f"{BASE_URL}/reset-password"
            supabase.auth.reset_password_for_email(
                self.reset_email, options={"redirect_to": redirect_url}
            )
            self.reset_sent = True
            yield rx.toast.success(
                "Als uw e-mailadres bij ons bekend is, ontvangt u een reset link."
            )
        except Exception as e:
            logging.exception(f"Password reset request error: {e}")
            yield rx.toast.error(
                "Er is een fout opgetreden bij het aanvragen van het wachtwoordherstel."
            )
        finally:
            self.is_resetting = False

    @rx.event
    async def signup(self):
        self.is_loading = True
        self.error = ""
        if not self.email or not self.password:
            self.error = "Please enter email and password"
            self.is_loading = False
            return
        try:
            if not supabase:
                self.error = "Supabase not configured for signup."
                self.is_loading = False
                return
            options = {}
            if self.full_name:
                options["data"] = {"full_name": self.full_name}
            response = supabase.auth.sign_up(
                {"email": self.email, "password": self.password, "options": options}
            )
            if response.user:
                if response.session:
                    self._set_user_session(response.user)
                    return rx.redirect("/")
                else:
                    rx.toast.success(
                        "Account created! Please check your email to confirm."
                    )
                    return rx.redirect("/login")
        except Exception as e:
            logging.exception(f"Signup error: {e}")
            self.error = str(e)
        finally:
            self.is_loading = False

    new_password: str = ""
    confirm_password: str = ""
    password_reset_success: bool = False
    password_reset_error: str = ""

    @rx.event
    def set_new_password(self, value: str):
        self.new_password = value

    @rx.event
    def set_confirm_password(self, value: str):
        self.confirm_password = value

    @rx.event
    async def confirm_password_reset(self):
        self.is_loading = True
        self.password_reset_error = ""
        if not self.new_password or not self.confirm_password:
            self.password_reset_error = "Vul alstublieft beide wachtwoordvelden in."
            self.is_loading = False
            return
        if len(self.new_password) < 8:
            self.password_reset_error = "Wachtwoord moet minimaal 8 tekens bevatten."
            self.is_loading = False
            return
        if self.new_password != self.confirm_password:
            self.password_reset_error = "Wachtwoorden komen niet overeen."
            self.is_loading = False
            return
        try:
            if not supabase:
                import asyncio

                await asyncio.sleep(1)
                self.password_reset_success = True
                yield rx.toast.success("Wachtwoord succesvol gewijzigd (Demo).")
                yield rx.redirect("/login")
                self.is_loading = False
                return
            response = supabase.auth.update_user({"password": self.new_password})
            if response.user:
                self.password_reset_success = True
                yield rx.toast.success("Wachtwoord succesvol gewijzigd.")
                yield rx.redirect("/login")
            else:
                self.password_reset_error = "Kon wachtwoord niet wijzigen. Probeer opnieuw een reset link aan te vragen."
        except Exception as e:
            logging.exception(f"Password update error: {e}")
            self.password_reset_error = (
                "Er is een fout opgetreden. Is uw reset link nog geldig?"
            )
        finally:
            self.is_loading = False