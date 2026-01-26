import reflex as rx
import httpx
import os
from dotenv import load_dotenv

load_dotenv("../.env")

# The State: The Brain of the Fontend, runs on the server & stores data 
class State(rx.State):
    chat_history: list[tuple[str, str]] = [
        ("ai", "Hello user, let me assist you with your notes.")
    ]
    
    def add_message(self, text: str):
        # Simple function that adds a message to the list
        self.chat_history.append(("user", text))
        # AI response logic coming soon.
    
    question: str = ""
    
    async def process_input(self):
        # This runs when the 'Send' button is clicked / when the 'Enter Key' is hit
        if self.question == "":
            return
        
        
        # Adding the user_query to the Chat History
        user_query = self.question
        self.chat_history.append(("user", self.question))
        
        self.question = "" # For clearing the input box
        yield # We force the UI to update before the API call finishes
        # Its done to be able to see our message getting passed in the UI before the AI replies
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8080/chat",
                    json={"question": user_query},
                    headers={"X-API-Key": str(os.getenv("SERVER_PASSWORD"))},
                    timeout=30.0 # We give the AI time to think
                )
                
                if response.status_code == 200:
                    ai_text = response.json()["answer"]
                    self.chat_history.append(("ai", ai_text))
                else:
                    self.chat_history.append(("ai", f"Error: {response.status_code}: {response.text}"))
        
        except Exception as e:
            self.chat_history.append(("ai", f"Connection Failed: {str(e)}"))


# The UI: This runs in the browser & reacts to the State
def chat_bubble(message: tuple[str, str]) -> rx.Component:
    # It helps draw a message bubble
    role = message[0]
    text = message[1]
    return rx.box(
        rx.text(text, color="white"),
        background_color=rx.cond(role == "user", "blue.500", "gray.600"),
        padding="1em",
        border_radius="lg",
        margin_bottom="0.5em",
        max_width="80%",
        align_self=rx.cond(role == "user", "flex_end", "flex_start"),
    )

def index() -> rx.Component:
    return rx.theme(
        rx.container(
            rx.vstack(
                # The Chat Area
                rx.vstack(
                    rx.foreach(State.chat_history, chat_bubble),
                    width="padding",
                    padding="2em",
                    align_items="stretch", # Ensures that bubbles align properly to left / right
                ),

                # The Input Box Area
                rx.hstack(
                    rx.input(
                        placeholder="Type a query...",
                        value=State.question,
                        on_change=State.set_question,
                        id="input_box",
                        width="100%",
                    ),
                    # Using lambda to test the add_message function
                    rx.button(
                        "Send",
                        on_click=State.process_input
                    ),
                    width="100%",
                    padding="1em",
                    position="sticky",
                    bottom="0",
                    background_color="white", # Keeping the input visible
                ),
                height="100vh", # Fullscreen Height
                justify="between", # Push input bottom
            ),
            height="100vh",
        ),
        appearance="light" # Forcing light mode
    )

# The App Definition
app = rx.App()
app.add_page(index)