# Berkeley Hackathon Workshop <> Lambda Inference API Demo

This repo contains a Chat CLI application that allows you to interact with Lambda's Cloud API via chat.
We use Lambda's Inference API with function calling to support this functionality.

## Prerequisites
- Lambda API Key

### Option 1: Run locally with Virtual Environment

1. Clone the repository:
```bash
git clone https://github.com/LambdaLabsML/lambda_inference_api_function_calling_workshop.git
cd lambda-cloud-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```env
LAMBDA_INFERENCE_API_KEY=your_lambda_api_key
LAMBDA_CLOUD_API_KEY=your_lambda_api_key
LAMBDA_INFERENCE_API_BASE=https://api.lambda.ai/v1
LAMBDA_CLOUD_API_BASE=https://cloud.lambda.ai/api/v1
DEFAULT_MODEL=llama-4-scout
LOG_LEVEL=INFO
SSH_KEY_NAME='' (add your SSH Key Name after creating it in the Lambda Cloud Dashboard)
```

5. Start the chat interface:
```bash
python main.py
```

### Option 2: Run with Docker

Alternatively, you can run the application using Docker:

1. Build the Docker image:
```bash
docker build -t lambda-cloud-assistant .
```

2. Run the container:
```bash
docker run -it --env-file .env lambda-cloud-assistant
```

Note: Make sure your `.env` file is in the same directory when running the Docker container.


### Available Commands

The assistant can help you with the following operations:
- List your running on-demand instances
- Create a new on-demand instance
- Terminate a running on-demand instance
- List available on-demand instances
- Get specific on-demand instance details

## Development

### Project Structure

```
.
├── README.md
├── requirements.txt
├── main.py              # Entry point
├── config.py           # Configuration management
├── lambda_cloud.py     # Lambda Cloud API client
├── lambda_chat.py      # Chat interface
└── .env               # Environment variables (not in version control)
```

### Logging

Logs are written to `lambda_assistant.log`.