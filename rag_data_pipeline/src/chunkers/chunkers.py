from typing import List
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter


class MarkdownChunker:
    """
    A utility class for chunking raw Markdown text into smaller pieces
    using LlamaIndex SentenceSplitter.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def chunk_markdown(self, markdown_text: str) -> List[str]:
        """
        Splits raw Markdown content into smaller text chunks.

        Args:
            markdown_text (str): The Markdown text to split.

        Returns:
            List[str]: A list of text chunks.
        """
        return self.splitter.split_text(markdown_text)


class DocumentChunker:
    """
    A utility class for chunking LlamaIndex Document objects into nodes.
    """

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = SentenceSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )

    def chunk_documents(self, documents: List[Document]):
        """
        Splits LlamaIndex Document objects into nodes.

        Args:
            documents (List[Document]): List of LlamaIndex Document objects.

        Returns:
            List[Node]: A list of LlamaIndex nodes.
        """
        return self.splitter.get_nodes_from_documents(documents)
