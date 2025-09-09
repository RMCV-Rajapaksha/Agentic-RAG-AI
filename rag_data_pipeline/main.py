
from llama_index.core import SimpleDirectoryReader, StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.vector_stores.postgres import PGVectorStore
import textwrap


from sqlalchemy import make_url



import os

os.environ["OPENAI_API_KEY"] = "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"



import psycopg2

connection_string = "postgres://postgres:newpassword@localhost:5432"


db_name = "vector_db"
conn = psycopg2.connect(connection_string)
conn.autocommit = True


documents = SimpleDirectoryReader("./data/paul_graham").load_data()
print("Document ID:", documents[0].doc_id)

with conn.cursor() as c:
    c.execute(f"DROP DATABASE IF EXISTS {db_name}")
    c.execute(f"CREATE DATABASE {db_name}")






url = make_url(connection_string)
vector_store = PGVectorStore.from_params(
    database=db_name,
    host=url.host,
    password=url.password,
    port=url.port,
    user=url.username,
    table_name="paul_graham_essay",
    embed_dim=1536,  # openai embedding dimension
    hnsw_kwargs={
        "hnsw_m": 16,
        "hnsw_ef_construction": 64,
        "hnsw_ef_search": 40,
        "hnsw_dist_method": "vector_cosine_ops",
    },
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(
    documents, storage_context=storage_context, show_progress=True
)


query_engine = index.as_query_engine()
print("Query Engine Ready-----------------------------------------------------------")
response = query_engine.query("What did the author do?")


print(textwrap.fill(str(response), 100))



print("---------------------------------------")
response = query_engine.query("What happened in the mid 1980s?")

print(textwrap.fill(str(response), 1000))


vector_store = PGVectorStore.from_params(
    database="vector_db",
    host="localhost",
    password="password",
    port=5432,
    user="postgres",
    table_name="paul_graham_essay",
    embed_dim=1536,  # openai embedding dimension
    hnsw_kwargs={
        "hnsw_m": 16,
        "hnsw_ef_construction": 64,
        "hnsw_ef_search": 40,
        "hnsw_dist_method": "vector_cosine_ops",
    },
)

index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
query_engine = index.as_query_engine()





