
import reflex as rx
import os
import httpx
import asyncio

from dotenv import load_dotenv

load_dotenv()

IS_PRODUCTION = os.getenv("REMOTE") == "1"

API_URL = "https://second-brain-api-yttm.onrender.com/chat" if IS_PRODUCTION else "http://localhost:8080/chat"

class State(rx.State):

    #----------- Basic Defaults -----------
    chat_history: list[tuple[str, str]] = [
        ("ai", "Hello user, let me assist you with your notes.")
    ]
    question: str = ""
    is_thinking: bool = False

    # ----------- Login Authentication State -----------
    entered_password: str = ""
    is_authenticated: bool = False if IS_PRODUCTION else True
    login_error: str = ""

    def set_question(self, value: str):
        self.question = value
    
    def set_entered_password(self, value: str):
        self.entered_password = value
    
    def check_login_page(self):
        if not IS_PRODUCTION:
            self.is_authenticated = True
            return rx.redirect("/chat")
        elif self.is_authenticated:
            return rx.redirect("/chat")
    
    def check_chat_page(self):
        if not self.is_authenticated:
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
    
    def logout(self):
        self.is_authenticated = False
        self.entered_password = ""
        self.chat_history = [("ai", "Hello user, let me assist you with your notes.")] # To clear out the Chat History!
        return rx.redirect("/")
    
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
        if self.question.strip() == "":
            return
        
        user_query = self.question
        self.chat_history.append(("user", user_query))
        self.question = ""
        self.is_thinking = True

        yield

        await asyncio.sleep(0.1)

        yield rx.scroll_to("chat_bottom")

        # Preparing the payload for FastAPI
        my_password = os.getenv("SERVER_PASSWORD", "")

        # Formatting the chat history into a list of dicts for the API
        api_history = [{"role": message[0],"content": message[1]} for message in self.chat_history[:-1]]

        try:
            async with httpx.AsyncClient() as client:
                wait_time = 99.0
                response = await client.post(
                    API_URL,
                    json={"question": user_query, "history": api_history},
                    headers={"SERVER_PASSWORD": str(my_password)},
                    timeout=wait_time # We listen for a limited time (Will be updated later in development)
                )

                if response.status_code == 200:
                    # Success in getting the answer from the AI!
                    ai_text = response.json().get("answer", "Error: No 'answer' key in backend response")
                    self.chat_history.append(("ai", ai_text))
                elif response.status_code == 401:
                    self.chat_history.append(("ai", "Authentication Error: The backend rejected the entered password!"))
                else:
                    self.chat_history.append(("ai", f"API Error: {response.status_code}: {response.text}"))
        except httpx.TimeoutException:
            self.chat_history.append(("ai", f"Timeout Error: AI took too long to respond (over the set {wait_time}s waiting interval)!"))
        except Exception as e:
            self.chat_history.append(("ai", f"Connection Failed: {str(e)}!"))
        
        # Turning off the Thinking Spinner
        self.is_thinking = False

        yield
        yield rx.scroll_to("chat_bottom")
        