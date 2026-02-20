from typing import Optional
from fastmcp import FastMCP
import chromadb

from databases.documentation_server import DB_PATH

# FILL ME IN!
COLLECTION_NAME = "????"


mcp = FastMCP("Chroma Server")
chroma_client = chromadb.PersistentClient(DB_PATH)
collection = chroma_client.get_collection(COLLECTION_NAME)


@mcp.tool
def ping() -> str:
    """A command to test that the MCP server is connected"""
    return "pong"

@mcp.tool
def ping_db() -> int:
    """Get a heartbeat from the chroma DB"""
    return chroma_client.heartbeat()

@mcp.tool
def query_db(query_text: str, contains_exact: Optional[str] = None) -> str:
    """Returns the relevant documents

    query_text: Text that will be embedded and searched against
    contains_exact: Used if an exact match to a term is requested

    Returns 2 documents that closely match the query
    """
    if contains_exact is not None: 
        contains_exact = {"$contains": contains_exact}

    query_result = collection.query(
        query_texts=query_text,
        where_document=contains_exact,
        n_results=2
    )['documents'][0]  # Can take the first index bc you only send one query
    # Will return a dictionary with `documentation` where documents is of shape [n_queries, n_results]
    
    return " ".join(query_result)

if __name__ == "__main__": 
    mcp.run()