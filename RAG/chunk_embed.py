from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re
import chromadb
model = SentenceTransformer('all-MiniLM-L6-v2')
def load_kb():
    kb_folder = Path("kb")
    kb_docs = {}
    for file_path in kb_folder.glob("*.txt"):
        doc_id=file_path.stem
        content=file_path.read_text(encoding="utf-8")
        content = " ".join(content.split())
        kb_docs[doc_id]=content
    for doc_id, text in kb_docs.items():
        print(f"Loaded '{doc_id}': {len(text)} characters")
    return kb_docs
def sen_chunk(text):
    splitter=re.split(r"(?<=[.!?])\s+", text)
    result=[]
    for i in range(0,len(splitter),2):
        result.append(" ".join(splitter[i:i+2]))
    return result
def fixed_chunk(text):
    text_splitter = CharacterTextSplitter(
    separator=" ",
    chunk_size=200,
    chunk_overlap=50
)
    chunks=text_splitter.split_text(text)
    return chunks
def embed_doc(kb_docs):
    # Parallel lists for Sentence Strategy
    sen_docs = []
    sen_ids = []
    sen_metadatas = []
    # Parallel lists for Fixed-Size Strategy
    fixed_docs = []
    fixed_ids = []
    fixed_metadatas = []
    for doc_id,text in kb_docs.items():
        sentence_chunks=sen_chunk(text)
        for idx,content in enumerate(sentence_chunks):
            sen_docs.append(content)
            sen_ids.append(f"{doc_id}_sen_{idx}")
            sen_metadatas.append({
                "parent_doc_id":doc_id,
                "strategy":"sentence",
                "chunk_index":idx
            })
        fixed_chunks=fixed_chunk(text)
        for idx,content in enumerate(fixed_chunks):
                fixed_docs.append(content)
                fixed_ids.append(f"{doc_id}_fixed_{idx}")
                fixed_metadatas.append({
                    "parent_doc_id":doc_id,
                    "strategy":"fixed",
                    "chunk_index":idx
                })
    return([sen_ids,sen_docs,sen_metadatas,fixed_ids,fixed_docs,fixed_metadatas])
def add_sen_collection(sen_ids,sen_docs,sen_metadatas):
    sen_vectors = model.encode(sen_docs)
    client = chromadb.PersistentClient(path="chroma_db")
    sen_collection = client.get_or_create_collection(name="cred_sentence",metadata={"hnsw:space": "cosine"})
    sen_collection.upsert(
            ids=sen_ids,
            documents=sen_docs,
            embeddings=sen_vectors.tolist(),
            metadatas=sen_metadatas
        )
def add_fixed_collection(fixed_ids,fixed_docs,fixed_metadatas):
    fixed_vectors = model.encode(fixed_docs)
    client = chromadb.PersistentClient(path="chroma_db")
    fixed_collection = client.get_or_create_collection(name="cred_fixed",metadata={"hnsw:space": "cosine"})
    fixed_collection.upsert(
            ids=fixed_ids,
            documents=fixed_docs,
            embeddings=fixed_vectors.tolist(),
            metadatas=fixed_metadatas)
if __name__ == "__main__":
    kb_docs=load_kb()
    lists=embed_doc(kb_docs)
    for i in lists:
        print(len(i))
#  Embedding and ChromaDB
    add_sen_collection(lists[0],lists[1],lists[2])
    add_fixed_collection(lists[3],lists[4],lists[5])