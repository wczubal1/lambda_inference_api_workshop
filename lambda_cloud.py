from typing import Dict, List, Any
import requests
from loguru import logger
from config import settings

class LambdaCloudClient:
    """Client for interacting with Lambda Cloud API."""
    
    def __init__(self):
        self.base_url = settings.LAMBDA_CLOUD_API_BASE
        self.headers = {
            "Authorization": f"Bearer {settings.LAMBDA_CLOUD_API_KEY}",
            "Content-Type": "application/json"
        }

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to Lambda Cloud API."""
        if endpoint == "launch_instance":
            url = "https://cloud.lambda.ai/api/v1/instance-operations/launch"
        elif endpoint == "instance_terminate":
            url = "https://cloud.lambda.ai/api/v1/instance-operations/terminate"
        else:
            url = f"{self.base_url}/{endpoint.lstrip('/')}"
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            raise

    def list_instances(self) -> List[Dict]:
        """List all instances."""
        return self._make_request("GET", "instances")

    def create_instance(self, instance_data: Dict) -> Dict:
        """Create a new instance."""
        instance_data["ssh_key_names"] = [settings.SSH_KEY_NAME]
        return self._make_request("POST", "launch_instance", json=instance_data)

    def terminate_instance(self, instance_id: str) -> Dict:
        """Terminate an instance."""
        data = {"instance_ids": [instance_id]}
        return self._make_request("POST", "instance_terminate", json=data)

    def list_instance_types(self) -> List[Dict]:
        """List available instance types."""
        return self._make_request("GET", "instance-types")

    def get_instance(self, instance_id: str) -> Dict:
        """Get instance details."""
        return self._make_request("GET", f"instances/{instance_id}")

# Function definitions for the AI model
LAMBDA_CLOUD_FUNCTIONS = [
    {
        "name": "list_instances",
        "description": "List your currently running Lambda Cloud instances. Only call this if the user asks for a list of instances that they are currently running.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "create_instance",
        "description": "Create a new Lambda Cloud instance",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the instance"
                },
                "instance_type_name": {
                    "type": "string",
                    "description": "Type of instance to create. This should be the exact name of the instance type, presented in the API. Example: gpu_1x_a10"
                },
                "region_name": {
                    "type": "string",
                    "description": "Region to create the instance in"
                },
            },
            "required": ["name", "instance_type_name", "region_name"]
        }
    },
    {
        "name": "terminate_instance",
        "description": "Terminate a Lambda Cloud instance. Only call this if the user asks to terminate an instance. Ask for the instance ID if you don't have it.",
        "parameters": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "ID of the instance to terminate"
                }
            },
            "required": ["instance_id"]
        }
    },
    {
        "name": "list_instance_types",
        "description": "List currently available Lambda Cloud instance types. Only call this if the user asks for of on-demand instances that are currently available.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "get_instance",
        "description": "Get details of a specific Lambda Cloud instance. Only call this if the user asks for the details of a specific instance. Ask for the instance ID if you don't have it.",
        "parameters": {
            "type": "object",
            "properties": {
                "instance_id": {
                    "type": "string",
                    "description": "ID of the instance to get details for"
                }
            },
            "required": ["instance_id"]
        }
    }
]

# Initialize client
cloud_client = LambdaCloudClient()

def execute_function_call(function_name: str, arguments: Dict[str, Any]) -> Dict:
    """Execute a Lambda Cloud API function call."""
    try:
        if function_name == "list_instances":
            return cloud_client.list_instances()
        elif function_name == "create_instance":
            return cloud_client.create_instance(arguments)
        elif function_name == "terminate_instance":
            return cloud_client.terminate_instance(arguments["instance_id"])
        elif function_name == "list_instance_types":
            return cloud_client.list_instance_types()
        elif function_name == "get_instance":
            return cloud_client.get_instance(arguments["instance_id"])
        else:
            raise ValueError(f"Unknown function: {function_name}")
    except Exception as e:
        logger.error(f"Function execution failed: {str(e)}")
        raise 