from gradio_client import Client

client = Client("Krass/Qwen-Qwen2.5-Coder-32B-Instruct")

def query_gradio_client(prompt):
    result = client.predict(
        message=prompt,
        api_name="/chat"
    )
    return result
