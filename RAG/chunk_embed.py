from pathlib import Path
from langchain_text_splitters import CharacterTextSplitter
import re
kb_folder = Path("kb")
kb_docs = {}
for file_path in kb_folder.glob("*.txt"):
    doc_id=file_path.stem
    content=file_path.read_text(encoding="utf-8")
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
    separator="",
    chunk_size=200,
    chunk_overlap=50
)
    chunks=text_splitter.split_text(text)
    return chunks
for text in kb_docs:
    print(fixed_chunk(kb_docs[text]))
