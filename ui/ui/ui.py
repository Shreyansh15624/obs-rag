import reflex as rx

# Importing the Brain of the Frontend
from ui.state import State

# Importing the Decors
from ui.pages.chat import chat_page

# Initializing the App
app = rx.App()

# Routing the UI securely to the Main Rendering Page
app.add_page(chat_page, route="/chat")