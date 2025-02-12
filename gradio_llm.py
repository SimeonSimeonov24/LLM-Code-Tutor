from gradio_client import Client
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the client URL from the .env file
client_url = os.getenv("CLIENT_URL")

# Initialize the client
client = Client(client_url)

def query_gradio_client(prompt):
    result = client.predict(
        message=prompt,
        api_name="/chat"
    )
    return result
