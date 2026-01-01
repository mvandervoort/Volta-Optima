import reflex as rx
from .base_state import State
from app.services.email_service import EmailService
import logging
import time
import datetime
import asyncio


class FeedbackState(State):
    """State for managing the feedback widget and screenshot capture."""

    is_open: bool = False
    feedback_type: str = "Suggestion"
    description: str = ""
    screenshot_data: str = ""
    is_capturing: bool = False
    is_submitting: bool = False
    website_url: str = ""
    form_loaded_at: float = 0.0
    is_hidden_for_screenshot: bool = False

    @rx.event
    def toggle_modal(self):
        """Toggles the feedback modal visibility."""
        self.is_open = not self.is_open
        if self.is_open:
            self.form_loaded_at = time.time()

    @rx.event
    def set_feedback_type(self, value: str):
        """Sets the type of feedback (Bug, Suggestion, etc)."""
        self.feedback_type = value

    @rx.event
    def set_website_url(self, value: str):
        """Explicit setter for honeypot field to avoid deprecation warning."""
        self.website_url = value

    @rx.event
    def set_description(self, value: str):
        """Sets the feedback description text."""
        self.description = value

    @rx.event
    def mark_form_interaction(self, _val: str):
        """Helper to track when user starts interacting with the form."""
        if self.form_loaded_at == 0:
            self.form_loaded_at = time.time()

    @rx.event
    async def capture_screenshot(self):
        """Triggers browser-side screenshot capture using html2canvas library with high quality settings."""
        self.is_capturing = True
        self.is_hidden_for_screenshot = True
        yield
        await asyncio.sleep(0.3)
        yield rx.call_script(
            """
            (async () => {
                try {
                    if (!window.html2canvas) {
                        const script = document.createElement('script');
                        script.src = 'https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js';
                        document.head.appendChild(script);
                        await new Promise(r => script.onload = r);
                    }

                    const canvas = await html2canvas(document.body, {
                        logging: false,
                        useCORS: true,
                        // Use device pixel ratio for better quality, capped at 2 to keep file size reasonable
                        scale: Math.min(window.devicePixelRatio || 1, 2),
                        ignoreElements: (el) => el.classList.contains('feedback-widget-container') || el.tagName === 'IFRAME'
                    });
                    // Use higher quality setting (0.92 is usually the sweet spot for visual quality vs size)
                    const data = canvas.toDataURL('image/jpeg', 0.92);
                    return data;
                } catch (e) {
                    console.error('Screenshot capture failed:', e);
                    return '';
                }
            })()
            """,
            callback=FeedbackState.receive_screenshot,
        )

    @rx.event
    def receive_screenshot(self, data: str):
        """Callback handler for the captured screenshot data."""
        self.screenshot_data = data
        self.is_capturing = False
        self.is_hidden_for_screenshot = False
        if not data:
            return rx.toast.error(
                "Screenshot maken mislukt. Controleer uw browserinstellingen."
            )

    @rx.event
    def clear_screenshot(self):
        """Removes the attached screenshot."""
        self.screenshot_data = ""

    @rx.var
    def has_screenshot(self) -> bool:
        """Boolean check for existing screenshot data."""
        return self.screenshot_data != ""

    def _is_bot(self) -> bool:
        """Simple check for bot submission using honeypot and time-on-page."""
        if self.website_url:
            return True
        if self.form_loaded_at == 0 or time.time() - self.form_loaded_at < 2.0:
            return True
        return False

    @rx.event
    async def submit_feedback(self):
        """Sends the feedback email via Resend service."""
        if self._is_bot():
            yield rx.toast.error(
                "Fout bij verzenden. Probeer het opnieuw door het formulier handmatig in te vullen."
            )
            return
        if not self.description:
            yield rx.toast.error("Vul a.u.b. een beschrijving in.")
            return
        self.is_submitting = True
        yield
        user_email = "Anoniem"
        if self.user:
            user_email = self.user.get("email", "Anoniem")
        page_url = self.router.page.path
        try:
            success = EmailService.send_feedback_email(
                to_email="info@energie-insight.nl",
                feedback_type=self.feedback_type,
                description=self.description,
                screenshot_base64=self.screenshot_data,
                page_url=page_url,
                user_email=user_email,
            )
            if success:
                self.is_open = False
                self.description = ""
                self.screenshot_data = ""
                yield rx.toast.success(
                    "Bedankt! Uw feedback is succesvol verzonden naar info@energie-insight.nl"
                )
            else:
                yield rx.toast.error(
                    "Kon feedback niet verzenden. Probeer het later opnieuw of mail ons direct."
                )
        except Exception as e:
            logging.exception(f"Error submitting feedback: {e}")
            yield rx.toast.error("Er is een onverwachte fout opgetreden.")
        finally:
            self.is_submitting = False