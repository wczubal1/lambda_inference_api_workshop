#!/usr/bin/env python3
"""
Lambda Cloud Assistant - A chat interface for managing Lambda Cloud instances
using Lambda's Inference API with function calling capabilities.
"""

import typer
from loguru import logger
from lambda_chat import start_chat
from config import settings

app = typer.Typer()

@app.command()
def main(
    log_level: str = typer.Option(
        settings.LOG_LEVEL,
        "--log-level",
        "-l",
        help="Set the logging level"
    )
):
    """Start the Lambda Cloud Assistant chat interface."""
    # Configure logging
    logger.remove()  # Remove default handler
    logger.add(
        "lambda_assistant.log",
        rotation="1 day",
        retention="7 days",
        level=log_level.upper()
    )
    logger.add(lambda msg: print(msg), level=log_level.upper())
    
    try:
        start_chat()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
