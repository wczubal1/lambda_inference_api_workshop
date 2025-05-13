# Berkeley Hackathon Workshop <> Lambda Inference API Demo

This repo contains a Chat CLI application that allows you to interact with Lambda's Cloud API via chat.
We use Lambda's Inference API with function calling to support this functionality.

## Prerequisites
- Lambda API Key

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
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
```

## Usage

Start the chat interface:

```bash
python main.py
```

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

Logs are written to `lambda_assistant.log` with daily rotation and 7-day retention.