import reflex as rx
from ui.state import State

def login_page():
    return rx.center(
        rx.vstack(
            rx.heading("Second Brain Login", size="7", color="white"),
            rx.text("Enter the Password to Continue:", color="gray"),

            rx.input(
                placeholder="Server Password",
                type="password",
                value=State.entered_password,
                on_change=State.set_entered_password,
                on_key_down=State.handle_login_key,
                width="100%",
                bg="grey.900",
                color="white",
                border_color="grey.700",
            ),

            rx.button(
                "Unlock Vault",
                on_click=State.verify_password,
                width="100%",
                color_scheme="blue",
                cursor="pointer",
            ),

            rx.cond(
                State.login_error != "",
                rx.text(State.login_error, color="red", size="2"),
            ),

            padding="2em",
            bg="#111",
            border_radius="xl",
            box_shadow="lg",
            spacing="3",
        ),
        height="100vh",
        bg="#000",
    )
