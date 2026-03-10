
import reflex as rx
import os
# import httpx
import asyncio

from dotenv import load_dotenv

load_dotenv("../.env")

IS_PRODUCTION = os.getenv("RENDER") == "true"

class State(rx.State):

    #----------- Basic Defaults -----------
    chat_history: list[tuple[str, str]] = [
        ("ai", "Hello user, let me assist you with your notes.")
    ]
    question: str = ""
    is_thinking: bool = False

    # ----------- Login Authentication State -----------
    entered_password: str = ""
    is_authenticated: bool = False
    login_error: str = ""

    def set_question(self, value: str):
        self.question = value
    
    def set_entered_password(self, value: str):
        self.entered_password = value
    
    def check_login_page(self):
        if not IS_PRODUCTION:
            self.is_authenticated = True
            return rx.redirect("/chat")
        if self.is_authenticated:
            return rx.redirect("/chat")
    
    def check_chat_page(self):
        if IS_PRODUCTION and not self.is_authenticated:
            return rx.redirect("/")
    
    def verify_password(self):
        correct_password = os.getenv("SERVER_PASSWORD")
        if self.entered_password == correct_password:
            self.is_authenticated = True
            self.login_error = ""
            return rx.redirect("/chat")
        else:
            self.is_authenticated = False
            self.login_error = "Incorrect Password! Access Denied!"
    
    # ------------------ KEY HANDLERS & CHAT ENGINE ------------------
    
    async def handle_login_key(self, key: str):
        """Used strictly by the Login Page"""
        if key == "Enter":
            return self.verify_password()
    
    async def handle_key(self, key: str):
        """Used strictly by the Chat Page"""
        if key == "Enter":
            return self.process_input()
    
    async def process_input(self):
        """The Chat Engine (Currently set to Mock AI)"""
        if self.question.strip() == "":
            return
        
        user_query = self.question
        self.chat_history.append(("user", user_query))
        self.question = ""
        self.is_thinking = True

        yield
        yield rx.scroll_to("chat_bottom")

        await asyncio.sleep(1.5)
        mock_text = f"🤖 **Mock AI:** I received your query: '{user_query}'. I am currently disconnected from the backend to save API tokens!"
        self.chat_history.append(("ai", mock_text))
        
        self.is_thinking = False

        yield
        yield rx.scroll_to("chat_bottom")
        