# menu_loader.py
# Loads menu data and creates FAISS vector store

import pandas as pd
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from config import MENU_FILE, EMBEDDING_MODEL, EMBEDDING_DEVICE


def read_menu():
    df = pd.read_excel(MENU_FILE)
    items = []
    for _, row in df.iterrows():
        items.append({
            "name": str(row["Dish Name"]).strip(),
            "category": str(row["Category"]).strip(),
            "components": str(row["Main Components"]).strip(),
            "price": int(row["Price INR"]),
        })
    return items


def build_vector_store(items):
    # one document per dish, so a search returns individual dishes and not the whole sheet
    docs = []
    for item in items:
        text = f"{item['name']} ({item['category']}): {item['components']}. Price Rs.{item['price']}"
        docs.append(Document(page_content=text, metadata=item))

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": EMBEDDING_DEVICE},
        encode_kwargs={"normalize_embeddings": True},
    )

    return FAISS.from_documents(docs, embeddings)
