from typing import Dict, List
from openai import OpenAI
from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config import settings

console = Console()

class DeepseekChat:
    """General Chat interface for an AI model with reasoning capabilities."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.API_KEY,
            base_url=settings.API_BASE_URL
        )
        self.model = settings.DEFAULT_MODEL
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant capable of answering general questions on a wide array of topics.

When handling user queries:
1. Provide informative and contextually relevant responses.
2. Be clear, concise, and accurate.
3. If further elaboration is needed, guide the user with well-structured explanations."""
            }
        ]

    def chat(self, user_input: str) -> None:
        """Process a chat message and provide responses based on user input."""
        self.messages.append({"role": "user", "content": user_input})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages
            )

            if not response.choices:
                raise ValueError("No response received from the model")

            message = response.choices[0].message
            if not message:
                raise ValueError("Empty message received from the model")

            self.messages.append({
                "role": "assistant",
                "content": message.content
            })

            console.print(Panel(
                Markdown(message.content),
                title="Assistant"
            ))

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            console.print(Panel(
                f"[red]I apologize, but I encountered an error while processing your request. Please try again.[/red]",
                title="Error"
            ))
            # Add a system message to help recover from the error
            self.messages.append({
                "role": "system",
                "content": "The previous response encountered an error. Please continue the conversation naturally."
            })


def start_chat():
    """Start an interactive chat session."""
    chat = DeepseekChat()
    print(f"DEBUG: Using model {settings.DEFAULT_MODEL}")  # Add this line
    console.print(Panel(
        "[bold blue]Welcome to the AI Assistant![/bold blue]\n"
        f"I am using the {settings.DEFAULT_MODEL} model.\n"
        "I can assist you with a wide range of topics.\n"
        "Type 'exit' or 'quit' to end the session.",
        title="AI Assistant"
    ))

    while True:
        try:
            user_input = console.input("\n[bold green]You:[/bold green] ")
            if user_input.lower() in ("exit", "quit"):
                console.print("[yellow]Goodbye![/yellow]")
                break
            chat.chat(user_input)
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            logger.error(f"Session error: {str(e)}")
            console.print(f"[red]Error: {str(e)}[/red]")