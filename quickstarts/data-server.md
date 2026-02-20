# Data Server Quickstart

This quickstart will guide you through two different methods to set up a method to "talk with" documents through a RAG (retrieval augmented generation). It will work entirely on a local device, but the same principals will be able to be applied to more complicated deployments. 

### Notes: 
* This guide is tested on a M1 Mac, so other architectures may see slightly different interfaces. 

### Prerequisites: 
* General python knowledge
* A python installation and a working understanding of virtual environments
* A device on which you can freely download software

### Installations/things to download:
* [LM Studio](https://lmstudio.ai/) - This will be used to host a local model and contact the document server. Using the GUI is recommended to start with. 
* [FastMCP](https://fastmcp.wiki/en/getting-started/welcome) - This will be the interface between the model and your documents. 
* [ChromaDB](https://docs.trychroma.com/docs/overview/getting-started) - This will create a "knowledge store", holding your documentation is a way the model can access freely. 
* A set of documents. Please ensure these documents do not contain any personal information. While the stakes for this being true here are low, it is good practice to get in the habit of. I recommend using the documentation files for your personal favorite OSS project to start. 

## Model Setup

1. Install LMStudio GUI
2. Navigate to 'Model Search' in the sidebar on the left. This displays open source LLMs available through [Hugging Face](https://huggingface.co/models). Select a model small enough to fit on your device (the "download options" tab will display an estimate showing performance on your hardware) - I recommend something under 10B (Billion) parameters, but in specific Qwen3 4B will be sufficient. 
3. Download your selected model and load the model by selecting it in the top menu (or with Ctrl+L). 
4. Ask the model a few basic questions to test its memory usage. If it slows down your machine dramatically, return to step 2 and pick a smaller model. 

> Note: If you have a small number of files (<5), instead of setting up the other servers you can create a temporary rag system using the `rag-v1` plugin supplied with LMStudio base. Simply attach the files to your chat.

## MCP Server Setup

0. Set up a virtual python environment with your method of choice (conda, uv, virtenv, poetry, etc)
1. [Install FastMCP](https://fastmcp.wiki/en/getting-started/installation) - `pip install fastmcp`
2. Create a python file where your server code will live
3. Create your server with dummy commands - an example can be seen [here](../mcp_servers/dummy_server.py)

> Note: It is important to add typing and docstrings to each mcp.tool method. Otherwise, the LLM model will have to infer the types and functionality of each tool from the name alone, and is more likely to get it wrong. 

4. Start the server with 

```bash
fastmcp run {server python file}:mcp --transport http --port 8000
```
 where you replace the name of the file and make sure the server is named `mcp` (e.g. mcp = FastMCP("Some Name"))
	copy-paste for the above repository: 

```bash
	fastmcp run mcp_servers/dummy_server.py:mcp --transport http --port 8000
```

5. Connect this server to your LLM in LMStudio by updating the mcp.json - [See instructions here](https://lmstudio.ai/docs/app/mcp)

	a. Open the right sidebar next to the download button

	b. Move to `Integrations` and click `Install`. This will open a warning and your MCP.json. Update it as follows: 
    ```json
	{
		  "mcpServers": {
		    "Test Server": {
		      "url": "http://127.0.0.1:8000/mcp"
		    }
		}
	}
    ```
	Saving this update should show that your model sends a single post command to ensure it is alive. 
	
6. Enable this tool in the `Integrations` menu.
7. Verify the model can contact it by requesting the model pings it. You should get a warning that the model is attempting to contact a tool, and ask if it is allowed to proceed. After this the model will call the tool, showing a few post requests to the server, and a response from that model that it used the tool to return some text. 

> Note: If you stop and start the server while LMStudio is connected, it will no longer be able to properly contact it. You must restart both the server and LMStudio. 

## Setting up Chroma DB

1. [Install ChromaDB](https://docs.trychroma.com/docs/overview/getting-started#install-manually)
2. Create your server with your existing files. [View an example here.](../databases/documentation_server.py)

	a. This example takes a folder that is one level deep containing either html, md, or .txt files and adds them to a collection with generated UUIDs for each file. 
	
	b. Execute the script with 
	```bash
		python3 databases/document_server.py --name MyFunCollection --files my/file/directory
	```
	You can check the `--help` option for a full description. 

	c. If this script is insufficient for your needs, using the  `open_collection` and `add_file` functions, you can add any number of text files to a new collection. If your individual files are large enough that you are worried about the model's context window, you can chop them up into smaller blocks

> Note: If you forget what your collection is called, you can see the list of collections with the below script: 
```python
	import chromadb

	DB_PATH = ".chroma/"  # Can be changed based on where you saved your files
	chroma_client =  chromadb.PersistentClient(path=DB_PATH)

	collections = client.list_collections()
```

## Create an MCP to use your collection

1. Create a duplicate of the original MCP server
2. Use the PersistentClient to open up the collection you made before
```python
chroma_client =  chromadb.PersistentClient(path=DB_PATH)
your_collection = chroma_client.get_collection(NAME_OF_YOUR_COLLECTION_GOES_HERE)
```

3. Modify the tool to contain a `query` method (named whatever you want.) See the below example: 

```python 
@mcp.tool
def query_db(query_text: str) -> str:
    """Returns the relevant documents

    query_text: Text that will be embedded and searched against

    Returns 2 documents that closely match the query
    """

    query_result = your_collection.query(
        query_texts=query_text,
        n_results=2
    )['documents'][0]
    # Will return a dictionary with `documentation` where documents is of shape [n_queries, n_results]
    return " ".join(query_result)
```

> Note: a full example can be seen [here](../mcp_servers/chroma_server.py)

4. Run the server with 
```bash
fastmcp run {server python file}:mcp --transport http --port 8001
```
Here the port does not matter, it is just changed from the first example to make it easier to keep track of the steps.

5. Connect your server to LMStudio using the `mcp.json`
```json
{
  "mcpServers": {
    "Test Server": {
      "url": "http://127.0.0.1:8000/mcp"
    },
    "Chroma Server": {
      "url": "http://127.0.0.1:8001/mcp"
    }
  }
}
```
6. Query your database with a term you know to be in your documentation. If the model does not automatically use the tool, you can prompt it by including the exact name of the function along the lines of "Use query_db to look up ..."