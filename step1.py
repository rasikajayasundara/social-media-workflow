from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from app.agents import copywriter, strategist, designer, reviewer
from app.state import ContentBrief, PostCopy, PostState

# class State(TypedDict, total=False):
#     topic:str
#     post:str

# def planner(state: State) -> dict:
#     print("Planner got:", state)
#     return {
#         "topic": "Weekly planning",}

# def writer(state: State) -> dict:
#     print("Writer got:", state)
#     return {
#         "post": f"3 tips about {state['topic']}.",
#     }

# def hashTag(state: State) -> dict:
#     print("HashTag got:", state)
#     return {
#         "post": f"{state['post']} #planning #tips",
#     }

def approval(state: PostState) -> dict:
    print("Approval got:", state)
    return {}

MAX_REVISIONS = 2

def route_after_review(state: dict) -> str:
    r = state["review"]
    if r["severity"] == "major" and state.get("revision", 0) < MAX_REVISIONS:
        return "revise"
    return "approval"           # good enough, or loop limit reached


def revise(state: dict) -> dict:
    return {"revision": state.get("revision", 0) + 1}

graph = StateGraph(PostState)
graph.add_node("strategist", strategist)
graph.add_node("copywriter", copywriter)
graph.add_node("designer", designer)
graph.add_node("approval", approval)
graph.add_node("reviewer", reviewer)
graph.add_node("revise", revise)
# graph.add_node("hashTag", hashTag)




graph.add_edge(START, "strategist")
graph.add_edge("strategist", "copywriter")
graph.add_edge("strategist", "designer")
graph.add_edge("copywriter","reviewer")
graph.add_edge("designer","reviewer")
graph.add_conditional_edges("reviewer", route_after_review)
graph.add_edge("revise", "copywriter")
graph.add_edge("approval", END)
# graph.add_edge("copywriter", "hashTag")
# graph.add_edge("hashTag", END)



app = graph.compile()
result = app.invoke({"user_brief": "How to plan your week effectively"})
print("final:", result)
print("------------------")
print(app.get_graph().draw_mermaid()) 