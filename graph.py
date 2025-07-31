from langgraph.graph import StateGraph, END
from nodes import (
    router_node, 
    email_retrieval_node, 
    email_send_node, 
    final_response_node
)
from state import EmailState

#now we need a function that decides what node should run next

def graph_router(state:EmailState)->str:
    """Determines what node should run next based on the email action"""
    action = state.get("email_action")
    
    if action == "search":
        return "search"
    elif action == "send":
        return "send"
    elif action =="unclear":
        return "respond"
    else:
        return "respond"
    
workflow = StateGraph(EmailState)#creating the graph

#adding the nodes to the graph
workflow.add_node("route",router_node)
workflow.add_node("search",email_retrieval_node)
workflow.add_node("send",email_send_node)
workflow.add_node("respond",final_response_node)

#adding the edges to the graph
workflow.set_entry_point("route")#always start at the routernode to decide where to go next
workflow.add_conditional_edges(
    "route",
    graph_router,#then we either go to search,send , or respond depending on graph_routers output
    {
        "search":"search",
        "send":"send",
        "respond":"respond"
    }
)
#so after graphrouter picks either search,send, or respond we have to specificy what happens after that
workflow.add_edge("search","respond")
workflow.add_edge("send","respond")
workflow.add_edge("respond",END)


email_assistant = workflow.compile() #-> this will be used in main.py