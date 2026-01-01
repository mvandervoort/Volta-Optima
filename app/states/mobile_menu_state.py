import reflex as rx


class MobileMenuState(rx.State):
    is_open: bool = False
    menu_key: int = 0

    @rx.event
    def toggle(self):
        self.is_open = not self.is_open

    @rx.event
    def close(self):
        self.is_open = False
        self.menu_key += 1

    @rx.event
    def open(self):
        self.is_open = True

    @rx.event
    def set_open(self, value: bool):
        self.is_open = value