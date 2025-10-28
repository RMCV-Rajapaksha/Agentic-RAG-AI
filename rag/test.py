from llama_index.llms.azure_inference import AzureAICompletionsModel
from llama_index.core.llms import ChatMessage
from azure.core.credentials import AzureKeyCredential
from config.config import get_config

config = get_config()

llm = AzureAICompletionsModel(
    endpoint=config.azure_inference_endpoint,
    credential=AzureKeyCredential(config.azure_inference_credential),
    model_name="gpt-4o"
)

messages = [
    ChatMessage(
        role="system", content="You are a pirate with colorful personality."
    ),
    ChatMessage(role="user", content="Hello"),
]

response = llm.chat(messages)
print(response)