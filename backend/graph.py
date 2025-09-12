import os
from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage, SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from tools import guest, cargo, security, door_control,which_guest_of_staff, staff_info, send_guest_email
from langchain_ollama import ChatOllama

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]
    kapı: str
    alarm: str
    password_attempts: int
tools = [guest, cargo, security, door_control,which_guest_of_staff, staff_info, send_guest_email]


model = ChatOllama(model="gpt-oss", base_url="http://192.168.0.94:11434", temperature=0).bind_tools(tools)
def call_model(state: AgentState) -> AgentState:
    
    with open("./data/system_prompt.txt", "r", encoding="utf-8") as f:
        system_prompt_text = "".join(f.readlines())

    system_prompt = SystemMessage(content=system_prompt_text)
    # Kapı durumu bilgisini içeren bir SystemMessage oluştur
    door_status_message = SystemMessage(content=f"Mevcut durumda, kapı: {state['kapı']}.")
    alarm_status_message = SystemMessage(content=f"Mevcut durumda, alarm: {state['alarm']}.")
    password_attempts_message = SystemMessage(content=f"Mevcut durumda, parola deneme sayısı: {state['password_attempts']}.")   
    # Model çağrısı için mesaj listesini oluştur
    messages_to_send = [system_prompt, door_status_message, alarm_status_message, password_attempts_message] + state["messages"]
    response = model.invoke(messages_to_send)

    return {"messages": [response]}

# ---- Tool Node ----
tool_node = ToolNode(tools=tools)

# ---- Router Node ----
def should_continue(state: AgentState):
    
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "continue"
    else:
        return "end"

# ---- Graph Definition ----
# Build the graph that defines the flow of the agent.
graph = StateGraph(AgentState)

graph.add_node("call_model", call_model)
graph.add_node("tool_node", tool_node)


graph.set_entry_point("call_model")


graph.add_conditional_edges(
    "call_model",
    should_continue,
    {
        "continue": "tool_node",
        "end": END,
    }
)

graph.add_edge("tool_node", "call_model")


app = graph.compile()


def get_graph():
    """Returns the compiled LangGraph application."""
    # Build the graph that defines the flow of the agent.
    graph = StateGraph(AgentState)

    graph.add_node("call_model", call_model)
    graph.add_node("tool_node", tool_node)

    graph.set_entry_point("call_model")

    graph.add_conditional_edges(
        "call_model",
        should_continue,
        {
            "continue": "tool_node",
            "end": END,
        }
    )

    graph.add_edge("tool_node", "call_model")

    return graph.compile()