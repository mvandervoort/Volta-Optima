import reflex as rx


class CookieConsentState(rx.State):
    consent_given: str = rx.Cookie(name="cookie_consent", max_age=31536000)
    show_banner: bool = True

    @rx.event
    def accept_cookies(self):
        self.consent_given = "true"
        self.show_banner = False

    @rx.event
    def reject_cookies(self):
        self.consent_given = "false"
        self.show_banner = False

    @rx.var
    def is_visible(self) -> bool:
        return (
            self.show_banner
            and self.consent_given != "true"
            and (self.consent_given != "false")
        )