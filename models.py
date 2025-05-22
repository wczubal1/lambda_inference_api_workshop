from openai import OpenAI
from config import settings

# Set API credentials and endpoint
openai_api_key = settings.LAMBDA_INFERENCE_API_KEY
openai_api_base = settings.LAMBDA_INFERENCE_API_BASE

# Initialize the OpenAI client
client = OpenAI(
    api_key=openai_api_key,
    base_url=openai_api_base,
)
print('here')
# List available models from the Lambda Inference API and print the result
models = client.models.list()
print(models)