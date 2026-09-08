from RAG.queries import QUERIES
from RAG.retrieve import generate,sen_collection
from agent.guardrails import overlap
JUDGE_PROMPT ="""You are an impartial AI judge evaluating the quality of a Retrieval-Augmented Generation (RAG) system output.

Evaluate the response based on the three metrics below, scoring each on a scale from 0.0 to 1.0:

1. Context Relevance (0.0 - 1.0):
   - Measures whether the retrieved context contains relevant information needed to answer the query.
   - 1.0 = Highly relevant context; 0.0 = Totally irrelevant or empty context.

2. Groundedness (0.0 - 1.0):
   - Measures whether the generated answer is strictly supported and factual according to the retrieved context (no hallucinations).
   - 1.0 = Completely grounded in context; 0.0 = Contains ungrounded or fabricated claims.

3. Answer Relevance (True,False):
   - Measures how directly and completely the answer addresses the user's initial query.
   - True = Directly addresses the query;False = Completely off-topic or evasive.

---
User Query:
{query}

Retrieved Context:
{context}

Generated Answer:
{answer}
---

Provide your evaluation in the following format:
Context Relevance: <score_between_0_and_1>
Groundedness: <score_between_0_and_1>
Answer Relevance: <True,False>
Reasoning: <brief explanation>
"""
def eval_score():
    avg_context=0
    avg_ground=0
    avg_ans_rev=0
    for q in QUERIES:
        out=generate(q["query"],sen_collection)
        ground=1
        if out["doc_id"]==None:
            ground=0
        context_text = " ".join(out["content"]) if ground else ""
        answer_rel = overlap(q["query"], context_text) if ground else 0
        print(f"Query: {q['query']} | Context: {out['similarity_score']} | Ground: {ground} | Answer: {answer_rel}")
        avg_context+=out["similarity_score"]
        avg_ground+=ground
        avg_ans_rev += answer_rel
    print(f" Average :  \nContext Relevance: {avg_context/15} Groundedness: {avg_ground/15}   Answer relevance: {avg_ans_rev/15} ")
if __name__=="__main__":
    eval_score()