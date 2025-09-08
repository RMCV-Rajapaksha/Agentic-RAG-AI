from config.settings import get_llm_settings  

def create_embeddings(text: str):
    """
    Create an embedding for the given text using the singleton OpenAIEmbedding instance.
    
    Args:
        text (str): The text to embed.
    
    Returns:
        list[float]: The embedding vector.
    """
    embed_model = get_llm_settings()._embedding_model
    embedding = embed_model.get_text_embedding(text)
    return embedding


