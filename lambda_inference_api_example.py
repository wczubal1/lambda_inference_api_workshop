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
model = "deepseek-r1-671b"

# Create a multi-turn chat completion request
chat_completion = client.chat.completions.create(
    messages=[{
        "role": "system",
        "content": """You are a helpful AI assistant"""
    }, 
    {
        "role": "user",
        "content": "Generate 10 random coin flips"
    }],
    model=model,
    #tools=[{"type": "function", "function": func} for func in LAMBDA_CLOUD_FUNCTIONS],
    #tool_choice="auto"  # Let the model decide whether to use functions or not
)

# Print the full chat completion response
print(chat_completion)