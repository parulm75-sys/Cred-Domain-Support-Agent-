from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter
from sentence_transformers import SentenceTransformer
import re
import chromadb
kb_folder = Path("kb")
kb_docs = {}
for file_path in kb_folder.glob("*.txt"):
    doc_id=file_path.stem
    content=file_path.read_text(encoding="utf-8")
    content = " ".join(content.split())
    kb_docs[doc_id]=content
for doc_id, text in kb_docs.items():
    print(f"Loaded '{doc_id}': {len(text)} characters")
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
def embed_doc():
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
    print(sen_docs[0],fixed_docs[0])
    return([sen_ids,sen_docs,sen_metadatas,fixed_ids,fixed_docs,fixed_metadatas])
lists=embed_doc()
for i in lists:
    print(len(i))

#  Embedding and ChromaDB
model = SentenceTransformer('all-MiniLM-L6-v2')
sen_vectors = model.encode(lists[1])
fixed_vectors=model.encode(lists[4])
client = chromadb.PersistentClient(path="chroma_db")
sen_collection = client.get_or_create_collection(name="cred_sentence")
sen_collection.upsert(
    ids=lists[0],
    documents=lists[1],
    embeddings=sen_vectors.tolist(),
    metadatas=lists[2]
)
fixed_collection = client.get_or_create_collection(name="cred_fixed")
fixed_collection.upsert(
    ids=lists[3],
    documents=lists[4],
    embeddings=fixed_vectors.tolist(),
    metadatas=lists[5]
)
print(sen_collection.count())