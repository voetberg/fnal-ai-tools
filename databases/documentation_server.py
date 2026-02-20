from collections.abc import Sequence
import os
import argparse
import chromadb
from uuid import uuid1

DB_PATH = ".chroma/"
chroma_client =  chromadb.PersistentClient(path=DB_PATH)

ACCEPTED_FILE_TYPES = [".md", ".mkd", ".txt", ".text", ".html"]

def open_collection(collection_name: str="TestCollection") -> chromadb.Collection:
    collection = chroma_client.get_or_create_collection(name=collection_name)
    return collection

def add_file(collection: chromadb.Collection, text: Sequence[str], ids: Sequence[str]) -> None:
    "From a list of files and IDs, update your collection."
    if len(text) != len(ids):
        raise ValueError("Must have the same number of text strings and IDs")
    if len(ids) != len(set(ids)): 
        raise ValueError("All IDs must be unique")
    
    collection.add(ids=ids, documents=text)

def _make_id() -> str:
    return f"{uuid1()}"

def _open_file(file_path: str) -> str:
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def add_files_from_directory(collection_name: str, file_directory: str) -> None: 
    directory_files = os.listdir(file_directory)
    accepted_files = [file for file in directory_files if any([file.endswith(file_type) for file_type in ACCEPTED_FILE_TYPES])]
    ids = [_make_id() for _ in range(len(accepted_files))]

    text_docs = []
    for f in accepted_files: 
        text_docs.append(_open_file(os.path.join(file_directory, f)))
    
    collection = open_collection(collection_name)
    add_file(collection, text=text_docs, ids=ids)
    

if __name__ == "__main__": 
    parser = argparse.ArgumentParser(prog="Create a new persistent chromadb")
    parser.add_argument("--name", help="Name of your new collection")
    parser.add_argument(
        "--files", 
        help="Relative path to your collection of files. Only supports a directory that is one deep."
    )

    args = parser.parse_args()
    name, dir = args.name, args.files

    add_files_from_directory(name, dir)
    