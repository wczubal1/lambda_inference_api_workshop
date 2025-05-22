#!/usr/bin/env python3
"""
Lambda Cloud Assistant - A chat interface for managing Lambda Cloud instances
using Lambda's Inference API with function calling capabilities.
"""

# import typer
# from loguru import logger
# #from lambda_chat import start_chat
# from general_chat import start_chat
# from config import settings

# app = typer.Typer()

# @app.command()
# def main(
#     log_level: str = typer.Option(
#         settings.LOG_LEVEL,
#         "--log-level",
#         "-l",
#         help="Set the logging level"
#     )
# ):
#     """Start the Lambda Cloud Assistant chat interface."""
#     # Configure logging
#     logger.remove()  # Remove default handler
#     logger.add(
#         "lambda_assistant.log",
#         rotation="1 day",
#         retention="7 days",
#         level=log_level.upper()
#     )
#     logger.add(lambda msg: print(msg), level=log_level.upper())
    
#     try:
#         start_chat()
#     except Exception as e:
#         logger.error(f"Application error: {str(e)}")
#         raise typer.Exit(1)

# if __name__ == "__main__":
#     app()

import os
from dotenv import load_dotenv
from openai import OpenAI
from config import settings
from loguru import logger

# Load environment variables
load_dotenv()

def main():
    """Starts a continuous chat session with the Lambda Inference API."""

    # Initialize the OpenAI client
    client = OpenAI(
        api_key=settings.LAMBDA_INFERENCE_API_KEY,
        base_url=settings.LAMBDA_INFERENCE_API_BASE,
    )

    # Choose the model
    model = settings.DEFAULT_MODEL

    # Initialize the message history
    messages = [{
        "role": "system",
        "content": "You are a helpful AI assistant."
    }]

    # Start the chat loop
    while True:
        try:
            # Get user input
            user_input = input("\nYou: ")

            # Exit condition
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye!")
                break

            # Add user message to the history
            messages.append({"role": "user", "content": user_input})

            # Create a chat completion request
            chat_completion = client.chat.completions.create(
                messages=messages,
                model=model
            )

            # Get the assistant's response
            assistant_response = chat_completion.choices[0].message.content

            # Print the assistant's response
            print(f"Assistant: {assistant_response}")

            # Add assistant message to the history
            messages.append({"role": "assistant", "content": assistant_response})

        except Exception as e:
            logger.error(f"API call failed: {e}")
            print(f"Error: {e}")

if __name__ == "__main__":
    main()