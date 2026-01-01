import reflex as rx
from dotenv import load_dotenv

load_dotenv()

config = rx.Config(app_name="app", frontend_static_pre_render=False, plugins=[rx.plugins.TailwindV3Plugin()])
