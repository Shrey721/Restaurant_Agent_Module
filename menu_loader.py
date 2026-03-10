# menu_loader.py
# Loads menu data and creates FAISS vector store

from langchain_community.document_loaders import UnstructuredExcelLoader #using unstructured excel loader to load menu data from excel file
from langchain_community.vectorstores import FAISS #using FAISS vector store to store menu data for retrieval during conversation
from langchain_huggingface import HuggingFaceEmbeddings #using hugginface embedding
from config import MENU_FILE, EMBEDDING_MODEL, EMBEDDING_DEVICE #config settings for menu file and embedding model/device


def load_menu(): #Loads menu data from excel file then creates embedding and uses FAISS vector store for retrieval.
    # load excel file
    loader = UnstructuredExcelLoader(MENU_FILE, mode="elements")
    data = loader.load()

    # setup embedding model
    embeddings = HuggingFaceEmbeddings(  # we use hugginface embedding for better performance on food related queries
        model_name=EMBEDDING_MODEL,
        model_kwargs={'device': EMBEDDING_DEVICE}, #using cpu for embedding
        encode_kwargs={'normalize_embeddings': False} #not normalizing embedding to preserve info
    )

    # create FAISS vector store
    db = FAISS.from_documents(data, embeddings) #storing menu data in FAISS vector store for retrieval during conversation

    return db 