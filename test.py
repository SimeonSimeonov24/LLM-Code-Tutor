from gradio_client import Client

client = Client("Nymbo/Qwen2.5-Coder-32B-Instruct-Serverless")
result = client.predict(
		message="Hello!!",
		system_message="",
		max_tokens=512,
		temperature=0.7,
		top_p=0.95,
		api_name="/chat"
)
print(result)