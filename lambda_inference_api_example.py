from dotenv import load_dotenv
import os
from openai import OpenAI
from lambda_cloud import LAMBDA_CLOUD_FUNCTIONS

# Load environment variables
load_dotenv()

# Set API credentials and endpoint
openai_api_key = os.getenv("LAMBDA_INFERENCE_API_KEY")
openai_api_base = os.getenv("LAMBDA_INFERENCE_API_BASE")

# Initialize the OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)

# Choose the model
model = "llama-4-scout"

# Create a multi-turn chat completion request
chat_completion = client.chat.completions.create(
    messages=[{
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
2. If the query is about Lambda AI or general AI topics, provide informative responses directly. Do not use the functions to answer these questions. Just answer the question directly.
3. Always be helpful, clear, and concise in your responses
4. When executing functions, explain what you're doing and why
5. If you encounter any errors, explain them clearly and suggest next steps
6. For general questions, provide accurate and up-to-date information about Lambda AI"""
    }, 
    {
        "role": "user",
        "content": "What are the currently available on-demand instances?"
    }],
    model=model,
    tools=[{"type": "function", "function": func} for func in LAMBDA_CLOUD_FUNCTIONS],
    tool_choice="auto"  # Let the model decide whether to use functions or not
)

# Print the full chat completion response
print(chat_completion)