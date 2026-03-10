import reflex as rx

# Importing the Brain of the Frontend
from ui.state import State

# Importing the Decors
from ui.pages.login import login_page
from ui.pages.chat import chat_page

# Initializing the App
app = rx.App()

# Routing the UI securely to the Main Rendering Page
app.add_page(login_page, route="/", on_load=State.check_login_page)
app.add_page(chat_page, route="/chat", on_load=State.check_chat_page)