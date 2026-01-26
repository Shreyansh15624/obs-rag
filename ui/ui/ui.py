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
    is_thinking: bool = False
    
    def set_question(self, value: str):
        self.question = value
    
    # Feel Good Mechanics: Smart Enter Key
    # This logic detects if 'Enter' (Send) is hit / 'Shift+Enter' (New Line) is hit 
    async def handle_key(self, key: str):
        # Instead of a complex handler we use a simple check
        # We will trigger this using a specific event prop in the UI Component
        if key == "Enter":
            return self.process_input()
    
    async def process_input(self):
        # This runs when the 'Send' button is clicked / when the 'Enter Key' is hit
        if self.question.strip() == "": # Provents empty sends
            return
        
        
        # Adding the user_query to the Chat History
        user_query = self.question
        self.chat_history.append(("user", self.question))
        self.question = "" # For clearing the input box
        self.is_thinking = True # We turn on the spinner
        
        yield rx.scroll_to("chat_bottom") # Feel Good Mechanic: AutoScroll to bottom
        # We force the UI to update & scroll to the bottom before the API call finishes
        # Its done so we see our message getting passed in the UI before the AI replies
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://localhost:8080/chat",
                    json={"question": user_query},
                    headers={"X-API-Key": str(os.getenv("SERVER_PASSWORD")) or ""},
                    timeout=30.0 # We give the AI time to think
                )
                
                if response.status_code == 200:
                    ai_text = response.json()["answer"]
                    self.chat_history.append(("ai", ai_text))
                else:
                    self.chat_history.append(("ai", f"Error: {response.status_code}: {response.text}"))
        
        except Exception as e:
            self.chat_history.append(("ai", f"Connection Failed: {str(e)}"))
        
        self.is_thinking = False
        # Scrolling down again after the Answer arrives


# The UI: This runs in the browser & reacts to the State
def chat_bubble(message: tuple[str, str]) -> rx.Component:
    # It helps draw a message bubble
    role = message[0]
    text = message[1]
    
    is_user = role == "user"
    
    return rx.vstack(
        rx.box(
            rx.markdown(
                text,
                # Adding some markdown styling to make it look clean
                component_map={
                    # Forcing Bold Text Rendering
                    "strong": lambda text, **props: rx.text(text, font_weight="bold", display="inline", **props),
                    "b": lambda text, **props: rx.text(text, font_weight="bold", display="inline", **props),
                    
                    # Forcing Italics Text Rendering
                    "em": lambda text, **props: rx.text(text, font_style="italics", display="inline", **props),
                    "i": lambda text, **props: rx.text(text, font_style="italics", display="inline", **props),
                     
                    "code": lambda text, **props: rx.code(text, color_scheme="green", **props),
                    "a": lambda text, **props: rx.link(text, underline="always", **props),
                }
            ),
            # Styling based on whose message it is
            background_color=rx.cond(role == "user", "#2b6cb0", "#2D3748"),
            color="white",
            padding_x="1.6em",
            padding_y="0px",
            border_radius="20px",
            border_bottom_right_radius=rx.cond(is_user, "2px", "12px"),
            border_bottom_left_radius=rx.cond(is_user, "12px", "2px"),
            margin_bottom="0.4em",
            max_width="100%",
            align_self=rx.cond(is_user, "flex_end", "flex_start"),
            box_shadow="md",
        ),
        
        rx.cond(
            ~is_user,
            rx.divider(margin="1px", border_color="#333"),
            rx.box(),
        ),
        width="100%",
        align_items=rx.cond(is_user, "flex-end", "flex-start"),
        spacing="1",
    )

def index() -> rx.Component:
    return rx.theme(
        # A full visible screen main container, with no window scroll
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Obsidian RAG", size="5", color="white"),
                rx.badge("Online", color_scheme="green"),
                width="100%",
                padding="1em",
                border_bottom="1px solid #333",
                background_color="#111",
            ),
            
            # Chat Area (Expands to fill the space)
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(State.chat_history, chat_bubble),
                    
                    # Thinking Indicator
                    rx.cond(
                        State.is_thinking,
                        rx.hstack(rx.spinner(size="2", color="grey"), rx.text("Thinking...", color="grey")),
                    ),
                    
                    # ANCHOR: The invisible line we scroll down to
                    rx.box(id="chat_bottom", height="1px"),
                    
                    width="100%",
                    padding="2em",
                    align_items="stretch",
                    spacing="2",
                ),
                
                # This way the scroll area spans all the available height
                flex="1",
                width="100%",
                scrollbar="vertical",
                type="always",
            ),
            
            # Input Box
            rx.hstack(
                rx.text_area(
                    placeholder="Type your query...",
                    value=State.question,
                    on_change=State.set_question,
                    on_key_down=State.handle_key,
                    width="100%",
                    bg="grey.900",
                    color="white",
                    border_color="grey.700",
                    min_height="50px",
                    max_height="150px",
                    padding="0.4em",
                    border_radius="xl",
                ),
                
                # Send Button
                rx.icon_button(
                    rx.icon("send"),
                    on_click=State.process_input,
                    size="3",
                    variant="solid",
                    color_scheme="blue",
                    cursor="pointer",
                ),
                width="100%",
                padding="1em",
                background_color="#000",
                border_top="1px solid #333",
            ),
            
            # GLOBAL STYLES
            height="100vh",
            width="100%",
            spacing="0",
            overflow="hidden",
            background_color="#000",
        ),
        appearance="dark", # Forcing Dark Mode
    )

# The App Definition
app = rx.App()
app.add_page(index)