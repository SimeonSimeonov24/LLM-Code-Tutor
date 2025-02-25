from gradio_client import Client
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Get the client URL from the .env file
client_url = os.getenv("CLIENT_URL")

# Initialize the client
client = Client(client_url)

# Helper function for querying Gradio Client
def query_gradio_client(prompt):
    result = client.predict(
            query=prompt,
            history=[],
            system="",
            radio="32B",
            api_name="/model_chat"
    )
    return result[1][0][1]