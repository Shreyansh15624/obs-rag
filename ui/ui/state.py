
import reflex as rx
import os
import httpx
import asyncio

from dotenv import load_dotenv

load_dotenv()

# Locking the local API strictly to the Local Backend
BACKEND_API_URL = "http://localhost:8080/chat"

class State(rx.State):

    #----------- Basic Defaults -----------
    chat_history: list[tuple[str, str]] = [
        ("ai", "Hello user, let me assist you with your notes."),
    ]
    question: str = ""
    is_thinking: bool = False

    # ----------- Login Authentication State -----------
    entered_password: str = ""
    is_authenticated: bool = False

    def set_question(self, value: str):
        self.question = value
    
    # ------------------ KEY HANDLERS & CHAT ENGINE ------------------    
    async def handle_key(self, key: str):
        """Used strictly by the Chat Page"""
        if key == "Enter":
            return self.process_input()
    
    async def process_input(self):
        # CONCURRENCY BLOCK: Prevents sending multiple queries if AI is already thinking / input is empty
        if self.question.strip() == "" or self.is_thinking:
            return
        
        user_query = self.question
        self.chat_history.append(("user", user_query))
        self.question = ""
        self.is_thinking = True

        yield
        await asyncio.sleep(0.1)
        yield rx.scroll_to("chat_bottom")

        # Formatting the chat history into a list of dicts for the API
        api_history = [{"role": message[0],"content": message[1]} for message in self.chat_history[:-1]]

        wait_time = 99.0
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    BACKEND_API_URL,
                    json={"question": user_query, "history": api_history},
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