from typing import TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.types import RetryPolicy
import time
import asyncio
class DemoState(TypedDict):
    value: str
    intent: str
attempt_count = 0
retry_pol = RetryPolicy(
    max_attempts=3,
    initial_interval=0.5,
    max_interval=4.0,
    backoff_factor=2.0,
    jitter=True,
    retry_on=RuntimeError
)
class GlobalTimeoutState(TypedDict):
    value: str

# Two nodes taking 1.5 seconds each (3.0 seconds total pipeline execution)
async def slow_step_one(state: GlobalTimeoutState) -> dict:
    print("NODE: slow_step_one running...")
    await asyncio.sleep(1.5)
    return {"value": "step_one_done"}

async def slow_step_two(state: GlobalTimeoutState) -> dict:
    print("NODE: slow_step_two running...")
    await asyncio.sleep(1.5)
    return {"value": "step_two_done"}
async def slow_node(state):
    print("NODE: slow_node running")
    await asyncio.sleep(3)
    return {"value": "should not reach here"}
async def timeout_demo():
    print("\n=== DEMO 2: PER-NODE TIMEOUT ===")
    try:
        await timeout_app.ainvoke({"value": "init"})
    except Exception as e:
        print(f"Caught: {type(e).__name__}: {e}")
def start(state):
    print("NODE: start running")
    return {"value": "started", "intent": "retry_test"}
def flaky_node(state):
    global attempt_count
    attempt_count += 1
    print(f"NODE: flaky attempt {attempt_count}")
    if attempt_count < 3:
        raise RuntimeError("Simulated transient failure")
    return {"intent": state["intent"]}
def end_state(state):
    print("NODE: end_state running")
    return {"value":"successful"}
graph=StateGraph(DemoState)
graph.add_node("flaky_node", flaky_node, retry_policy=retry_pol)
graph.add_node("start",start)
graph.add_node("end_state",end_state)
graph.set_entry_point("start")
graph.add_edge("start","flaky_node")
graph.add_edge("flaky_node","end_state")
graph.add_edge("end_state",END)
app = graph.compile()
timeout_graph = StateGraph(DemoState)
timeout_graph.add_node("slow_node", slow_node, timeout=1.0)
timeout_graph.set_entry_point("slow_node")
timeout_graph.add_edge("slow_node", END)
timeout_app = timeout_graph.compile()
global_graph = StateGraph(GlobalTimeoutState)
global_graph.add_node("slow_step_one", slow_step_one)
global_graph.add_node("slow_step_two", slow_step_two)

global_graph.add_edge(START, "slow_step_one")
global_graph.add_edge("slow_step_one", "slow_step_two")
global_graph.add_edge("slow_step_two", END)

global_app = global_graph.compile()

async def global_timeout_demo():
    print("\n=== DEMO 3: GLOBAL / PIPELINE TIMEOUT ===")
    try:
        # Wrap full invocation in asyncio.wait_for (2.0s budget vs 3.0s total pipeline)
        await asyncio.wait_for(
            global_app.ainvoke({"value": "init"}),
            timeout=2.0
        )
    except Exception as e:
        print(f"Caught: {type(e).__name__}: {e if str(e) else 'Pipeline exceeded overall execution budget'}")
if __name__ == "__main__":
    print("=== DEMO 1: RETRY ===")
    print(app.invoke({"value": "init"}))
    asyncio.run(timeout_demo())
    asyncio.run(global_timeout_demo())