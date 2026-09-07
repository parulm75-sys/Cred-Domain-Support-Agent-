import chromadb
import queries
from sentence_transformers import SentenceTransformer
client = chromadb.PersistentClient(path="chroma_db")
sen_collection = client.get_collection(name="cred_sentence")
fixed_collection = client.get_collection(name="cred_fixed")
model = SentenceTransformer('all-MiniLM-L6-v2')
THRESHOLD = 0.45
def retrieve(query, collection, n_results=3):
    vector=model.encode(query)
    result=collection.query(query_embeddings=[vector.tolist()], n_results=n_results)
    return(result)
def generate(query,collection):
    chunks=retrieve(query,collection,3)
    similarity = 1 - chunks["distances"][0][0]
    if(similarity>=THRESHOLD):
        return {
            "doc_id": list(dict.fromkeys([m["parent_doc_id"] for m in chunks["metadatas"][0]])),
            "content":chunks["documents"][0],
            "similarity_score":similarity
        }
    else:
        return {
            "doc_id":None,
            "content":"I don't know",
            "similarity_score":similarity
        }
def prec_recall(exp_doc_id,retrieved):
    if(retrieved["doc_id"]==None):
        recall=0.0
        precision=0.0
    elif exp_doc_id["doc_id"] in retrieved["doc_id"]:
        recall=1.0
        precision=1/len(retrieved["doc_id"])
    else:
        recall=0.0
        precision=0.0
    return [recall,precision]
if __name__ == "__main__":
    for i in queries.QUERIES:
        result_fix=retrieve(i["query"], fixed_collection, 1)
        similarity_fix=1-result_fix["distances"][0][0]
        result_sen=retrieve(i["query"], sen_collection, 1)
        similarity_sen=1-result_sen["distances"][0][0]
        print(i["in_scope"]," Sentence: ",similarity_sen," Fixed: ",similarity_fix," ",i["query"])
    for i in queries.QUERIES:
        print(generate(i["query"],sen_collection))
    #Recall and Precision
    recall_avg_sen=0.0
    recall_avg_fixed=0.0
    precision_avg_sen=0.0
    precision_avg_fixed=0.0
    for i in queries.QUERIES:
        out=generate(i['query'],sen_collection)
        recall,precision=prec_recall(i,out)
        recall_avg_sen+=recall
        precision_avg_sen+=precision
        print(f"Query :{i['query']} sentence strategy recall: {recall} precision: {precision}")
        if(precision!=0):
              print(f" or 1/{len(out['doc_id'])}")
        out=generate(i['query'],fixed_collection)
        recall,precision=prec_recall(i,out)
        recall_avg_fixed+=recall
        precision_avg_fixed+=precision
        print(f"fixed strategy recall: {recall} precision: {precision}")
        if(precision!=0):
              print(f" or 1/{len(out['doc_id'])}")
    length=12
    print(f" Average values for sentence recall: {recall_avg_sen/length} precision: {precision_avg_sen/length}")
    print(f" Average values for sentence recall: {recall_avg_fixed/length} precision: {precision_avg_fixed/length}")