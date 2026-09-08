from agent.graph import checkpoint_app
if __name__=="__main__":
    config = {"configurable": {"thread_id": "ckpt_demo_1"}}
    # Phase I: Interrupting (initial Run)
    result = checkpoint_app.invoke(
    {"query": "What is the status of my application 23", "history": []},
    config=config
    )
    # Phase 2: checkpoint state
    state = checkpoint_app.get_state(config)
    print("Saved state:", state.values)
    print("Next node:", state.next)
    # Phase 3: resuming same thread
    final = checkpoint_app.invoke(None, config=config)
    print(final["response"])