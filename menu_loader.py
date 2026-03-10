# menu_loader.py
# Loads menu data and creates FAISS vector store

from langchain_community.document_loaders import UnstructuredExcelLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import MENU_FILE, EMBEDDING_MODEL, EMBEDDING_DEVICE


def load_menu():
    # load excel file
    loader = UnstructuredExcelLoader(MENU_FILE, mode="elements")
    data = loader.load()

    # setup embeddings
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': EMBEDDING_DEVICE},
        encode_kwargs={'normalize_embeddings': False}
    )

    # create FAISS vector store
    db = FAISS.from_documents(data, embeddings)

    return db