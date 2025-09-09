from typing import Dict
from config.config import get_config
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from typing import List

class LLMSettings:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.initialize()
        return cls._instance
    
    def initialize(self):
        config = get_config()
        self._openai_api_key = config.openai_api_key
        self._embedding_model = OpenAIEmbedding(api_key=self._openai_api_key, model="text-embedding-ada-002")

    def get_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using LlamaIndex's OpenAIEmbedding.
        """
        text = text.replace("\n", " ")
     
        embedding = self._embedding_model.get_text_embedding(text)

       
        return embedding

def get_llm_settings() -> LLMSettings:
    return LLMSettings()