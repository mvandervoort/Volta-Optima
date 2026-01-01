import reflex as rx
import os
import sys
import platform
import logging


class AdminSettingsState(rx.State):
    supabase_connected: bool = False
    questdb_connected: bool = False
    resend_configured: bool = False
    python_version: str = ""
    platform_info: str = ""
    app_version: str = "1.0.0"

    @rx.event
    def on_load(self):
        self.supabase_connected = bool(
            os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")
        )
        self.questdb_connected = bool(os.getenv("QUESTDB_URL"))
        self.resend_configured = bool(os.getenv("RESEND_API_KEY"))
        self.python_version = sys.version.split()[0]
        self.platform_info = platform.platform()