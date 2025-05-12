from typing import Dict, List
from openai import OpenAI
from loguru import logger
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from config import settings
from lambda_cloud import LAMBDA_CLOUD_FUNCTIONS, execute_function_call

console = Console()

class LambdaChat:
    """Chat interface using Lambda's Inference API with function calling support."""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LAMBDA_INFERENCE_API_KEY,
            base_url=settings.LAMBDA_INFERENCE_API_BASE
        )
        self.model = settings.DEFAULT_MODEL
        self.messages: List[Dict[str, str]] = [
            {
                "role": "system",
                "content": """You are a helpful AI assistant for Lambda AI, capable of both managing Lambda Cloud instances and answering general questions about Lambda AI.

For Lambda Cloud management, you can help users with the following functions:
- list_instances: List all instances
- create_instance: Create a new instance
- terminate_instance: Terminate an instance
- list_instance_types: List available instance types
- get_instance: Get instance details

For general questions about Lambda AI, you can provide information about:
- Lambda AI's mission and vision
- Lambda AI's products and services
- Lambda AI's technology and infrastructure
- Lambda AI's team and company information
- General AI and machine learning concepts

When handling user queries:
1. If the query is about managing Lambda Cloud instances, use the appropriate function calls
2. If the query is about Lambda AI or general AI topics, provide informative responses directly
3. Always be helpful, clear, and concise in your responses
4. When executing functions, explain what you're doing and why
5. If you encounter any errors, explain them clearly and suggest next steps
6. For general questions, provide accurate and up-to-date information about Lambda AI"""
            }
        ]

    def _format_function_result(self, function_name: str, result: Dict) -> str:
        """Format function call result for display."""
        data = result.get("data", {})
        if not data:
            return "No data found."
        return str(data)

    def chat(self, user_input: str) -> None:
        """Process a chat message and handle both function calls and general queries."""
        self.messages.append({"role": "user", "content": user_input})
        
        while True:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=self.messages,
                    tools=[{"type": "function", "function": func} for func in LAMBDA_CLOUD_FUNCTIONS],
                    tool_choice="auto"  # Let the model decide whether to use functions or not
                )
                
                if not response.choices:
                    raise ValueError("No response received from the model")
                
                message = response.choices[0].message
                if not message:
                    raise ValueError("Empty message received from the model")
                
                # self.messages.append(message)
                self.messages.append({
                    "role": "assistant",
                    "content": message.content
                })
                
                # Handle function calls if present
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        arguments = eval(tool_call.function.arguments)

                        console.print(Panel(
                            f"[yellow]Executing function: {function_name} with arguments: {arguments}[/yellow]",
                            title="Function Call"
                        ))

                        try:
                            result = execute_function_call(function_name, arguments)
                            formatted_result = self._format_function_result(function_name, result)
                            
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": formatted_result
                            })
                            
                            console.print(Panel(
                                Markdown(formatted_result),
                                title="Function Result"
                            ))
                        except Exception as e:
                            error_msg = f"Error executing {function_name}: {str(e)}"
                            console.print(Panel(
                                f"[red]{error_msg}[/red]",
                                title="Error"
                            ))
                            self.messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": function_name,
                                "content": error_msg
                            })
                    continue
                
                # Display assistant's response (for both function results and general queries)
                if hasattr(message, 'content') and message.content:
                    console.print(Panel(
                        Markdown(message.content),
                        title="Assistant"
                    ))
                else:
                    console.print(Panel(
                        "[yellow]I apologize, but I couldn't generate a proper response. Please try rephrasing your question.[/yellow]",
                        title="Assistant"
                    ))
                break
                
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
                break

def start_chat():
    """Start an interactive chat session."""
    chat = LambdaChat()
    console.print(Panel(
        "[bold blue]Welcome to Lambda AI Assistant![/bold blue]\n"
        "I can help you with:\n"
        "1. Managing your Lambda Cloud instances\n"
        "2. Answering questions about Lambda AI\n"
        "Type 'exit' or 'quit' to end the session.",
        title="Lambda AI Assistant"
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