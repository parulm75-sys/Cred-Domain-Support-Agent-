import chromadb
import queries
from sentence_transformers import SentenceTransformer
client = chromadb.PersistentClient(path="chroma_db")
sen_collection = client.get_collection(name="cred_sentence")
fixed_collection = client.get_collection(name="cred_fixed")
model = SentenceTransformer('all-MiniLM-L6-v2')
def retrieve(query, collection, n_results=3):
    vector=model.encode(query)
    result=collection.query(query_embeddings=[vector.tolist()], n_results=n_results)
    return(result)
ans=retrieve("How can I increase my credit score?",fixed_collection,3)
for i in queries.QUERIES:
    result_fix=retrieve(i["query"], fixed_collection, 1)
    similarity_fix=1-result_fix["distances"][0][0]
    result_sen=retrieve(i["query"], sen_collection, 1)
    similarity_sen=1-result_sen["distances"][0][0]
    print(i["in_scope"]," Sentence: ",similarity_sen," Fixed: ",similarity_fix," ",i["query"])
    