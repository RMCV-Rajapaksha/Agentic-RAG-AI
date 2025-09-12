import logging
import os
import textwrap
from database.db import DatabaseConnection
from config.config import get_config

try:
    from llama_index.embeddings.openai import OpenAIEmbedding
except ImportError:
    print("Required dependencies not installed. Please install:")
    print("uv add llama-index llama-index-embeddings-openai llama-index-vector-stores-postgres")
    exit(1)

# Configure basic logging to see output from the modules
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


config = get_config()
os.environ["OPENAI_API_KEY"] = config.openai_api_key


def main():
    """
    Main function to initialize the database connection,
    run a query, and display the results.
    """
    # --- Configuration ---
    # For this script to work, you need to have your OpenAI API key
    # set as an environment variable, for example:
    # export OPENAI_API_KEY='your_api_key_here'
    # It also assumes your config/config.py is correctly set up with
    # your database connection string.
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY environment variable not set.")
        print("\nPlease set your OPENAI_API_KEY environment variable to run this example.")
        return

    try:
        # 1. Initialize the database connection and vector store
        logger.info("Initializing DatabaseConnection...")
        db_connection = DatabaseConnection()
        
        # 2. Initialize the embedding model
        # Here we use OpenAI's model. You can replace this with any
        # other LlamaIndex-compatible embedding model.
        logger.info("Initializing embedding model...")
        embed_model = OpenAIEmbedding()

        # 3. Define the query
        query_text = "What are the main challenges in AI development?"
        logger.info(f"Preparing to query with: '{query_text}'")

        # 4. Run the query against the vector store
        results = db_connection.query_vector_store(
            query_text=query_text,
            embed_model=embed_model,
            similarity_top_k=5,  # Retrieve the top 5 most similar chunks
        )

        # 5. Display the results in a formatted way
        if results:
            width = 80  # Define a terminal width for clean output
            
            # Print a master header
            print("\n" + "=" * width)
            print(" " * ((width - 15) // 2) + "QUERY RESULTS")
            print("=" * width)
            
            # Wrap the original query for display
            query_wrapper = textwrap.TextWrapper(width=width, initial_indent="Query: ", subsequent_indent="       ")
            print(query_wrapper.fill(f"'{query_text}'"))
            print(f"\nFound {len(results)} related text chunks:")
            print("-" * width)

            # Wrapper for the result text
            text_wrapper = textwrap.TextWrapper(width=width - 4, initial_indent="", subsequent_indent="")

            for i, res in enumerate(results):
                # Print result header with score
                print(f"➡️  Result {i + 1} | Similarity Score: {res.score:.4f}")
                
                # Get, clean, and wrap the node content for readability
                content = res.node.get_content().strip().replace('\n', ' ')
                wrapped_text = text_wrapper.fill(content)
                
                # Indent the wrapped text block
                for line in wrapped_text.split('\n'):
                    print(f"    {line}")

                # Print a separator for all but the last result
                if i < len(results) - 1:
                    print("\n" + "." * (width // 2) + "\n")
            
            print("=" * width)
            
        else:
            print("\n--- No results found for the query. ---")


    except Exception as e:
        logger.error(f"An error occurred in the main function: {e}")
        # Depending on the error, you might want to print more user-friendly messages.
        print("\nAn unexpected error occurred. Please check the logs for details.")


if __name__ == "__main__":
    main()
