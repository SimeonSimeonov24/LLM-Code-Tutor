from gradio_client import Client
from dotenv import load_dotenv, find_dotenv
import os

# Load environment variables from the .env file
if not find_dotenv():
    raise FileNotFoundError(".env file not found")
load_dotenv()

# Get the client URL from the .env file
client_url = os.getenv("CLIENT_URL")
if not client_url:
    raise ValueError("CLIENT_URL not found in .env file")

# Initialize the client
try:
    client = Client(client_url)
except Exception as e:
    raise ConnectionError(f"Failed to initialize client: {e}")

# Helper function for querying Gradio Client
def query_gradio_client(prompt):
    try:
        result = client.predict(
                query=prompt,
                history=[],
                system="",
                radio="32B",
                api_name="/model_chat"
        )
        return result[1][0][1]
    except Exception as e:
        raise RuntimeError(f"Failed to query Gradio Client: {e}")