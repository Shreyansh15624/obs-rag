import reflex as rx
from ui.state import State

def chat_bubble(message: tuple[str, str]):
    role = message[0]
    text = message[1]
    is_user = role == "user"

    return rx.vstack(
        rx.box(
            rx.markdown(
                text,
                component_map={
                    "strong": lambda text, **props: rx.text(text, font_weight="bold", display="inline", **props),
                    "b": lambda text, **props: rx.text(text, font_weight="bold", display="inline", **props),
                    "em": lambda text, **props: rx.text(text, font_style="italics", display="inline", **props),
                    "i": lambda text, **props: rx.text(text, font_style="italics", display="inline", **props),
                    "code": lambda text, **props: rx.code(text, color_scheme="green", display="inline", **props),
                    "a": lambda text, **props: rx.link(text, underline="always", **props),
                }
            ),
            background_color=rx.cond(role == "user", "#2b6cb0", "#2D3748"),
            color="white",
            padding_x="1.6em",
            padding_y="0px",
            border_radius="20px",
            border_bottom_right_radius=rx.cond(is_user, "2px", "12px"),
            border_bottom_left_radius=rx.cond(is_user, "12px", "2px"),
            margin_bottom="0.4em",
            align_self=rx.cond(is_user, "flex_end", "flex_start"),
            box_shadow="md",
        ),

        rx.cond(
            ~is_user,
            rx.divider(margin="1px", border_color="#333"),
            rx.box(),
        ),
        width="100%",
        align_items=rx.cond(is_user, "flex-end", "flex_start"),
        spacing="1",
    )

def chat_page():
    return rx.theme(
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

            # Chat Area
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(State.chat_history, chat_bubble),

                    # Thinking Indicator
                    rx.cond(
                        State.is_thinking,
                        rx.hstack(rx.spinner(size="2", color="gray", ), rx.text("Thinking...", color="gray")),
                    ),

                    # ANCHOR: The invisible line we will auto-scroll down to
                    rx.box(id="chat_bottom", height="1px"),

                    width="100%",
                    padding="2em",
                    align_items="stretch",
                    spacing="2", 
                ),
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
                    on_key_down=State.set_question,
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
                    rx.icon("Send"),
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
        appearance="dark",
    )