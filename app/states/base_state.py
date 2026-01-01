import reflex as rx
from typing import Optional
from app.states.rate_limit_state import RateLimitState


class State(RateLimitState):
    """The base state for the app."""

    user: Optional[dict] = None
    user_role: str = "user"

    @rx.event
    def logout(self):
        self.user = None
        self.user_role = "user"
        return rx.redirect("/")

    @rx.var
    def is_authenticated(self) -> bool:
        return self.user is not None

    @rx.var
    def is_admin(self) -> bool:
        return self.user_role == "admin"