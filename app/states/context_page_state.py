import reflex as rx


class ContextPageState(rx.State):
    active_section: str = "the-challenge"

    @rx.event
    def set_active_section(self, section_id: str):
        self.active_section = section_id