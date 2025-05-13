# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables with default values
ENV LAMBDA_INFERENCE_API_BASE=https://api.lambda.ai/v1
ENV LAMBDA_CLOUD_API_BASE=https://cloud.lambda.ai/api/v1
ENV DEFAULT_MODEL=llama-4-scout
ENV LOG_LEVEL=INFO

# Set the entrypoint
ENTRYPOINT ["python", "main.py"]
