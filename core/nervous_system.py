from typing import Annotated, TypedDict, List, Union
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import ToolNode
from core.brain import Brain
from memory.vector_db import LongTermMemory
from tools.finance import get_market_analysis, search_finance_news

class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    context: str

class NervousSystem:
    """
    NervousSystem manages the LangGraph state machine with ReAct pattern.
    """
    def __init__(self, brain: Brain, memory: LongTermMemory):
        self.brain = brain
        self.memory = memory
        
        # Define tools
        self.tools = [get_market_analysis, search_finance_news]
        self.tool_node = ToolNode(self.tools)
        
        # Bind tools to LLM
        self.llm = self.brain.get_llm().bind_tools(self.tools)
        
        self.workflow = StateGraph(AgentState)
        self._setup_graph()

    def _setup_graph(self):
        # Define the nodes
        self.workflow.add_node("retrieve_memory", self.retrieve_memory_node)
        self.workflow.add_node("agent", self.agent_node)
        self.workflow.add_node("action", self.tool_node)

        # Define the edges
        self.workflow.set_entry_point("retrieve_memory")
        self.workflow.add_edge("retrieve_memory", "agent")
        
        # Conditional edge for tool calling
        self.workflow.add_conditional_edges(
            "agent",
            self.should_continue,
            {
                "continue": "action",
                "end": END
            }
        )
        
        # After tool execution, go back to agent to summarize
        self.workflow.add_edge("action", "agent")

        # Compile the graph
        self.app = self.workflow.compile()

    def should_continue(self, state: AgentState):
        """Determines if the agent should call a tool or end."""
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "continue"
        return "end"

    def retrieve_memory_node(self, state: AgentState):
        """Node to fetch relevant context from long-term memory (e.g. User Profile)."""
        # Search for user preferences or risk profile
        last_message = state["messages"][-1].content
        relevant_docs = self.memory.search_memory(f"Kullanıcı profili risk tercihi: {last_message}")
        context = "\n".join([doc.page_content for doc in relevant_docs])
        return {"context": context}

    def agent_node(self, state: AgentState):
        """Main agent node that reasons and decides on tools."""
        system_prompt = (
            "Sen zeki ve profesyonel bir finansal asistansın. "
            "Kullanıcının risk profilini ve geçmişini göz önünde bulundurarak yanıt ver.\n\n"
            f"BİLİNEN KULLANICI BİLGİLERİ:\n{state['context']}\n\n"
            "Eğer güncel veriye ihtiyacın varsa araçları kullan. "
            "Kullanıcıya yanıt verirken samimi (kanka diyerek) ama bilgilendirici ol."
        )
        
        # Filter out repeated system prompts if any, and prepend the latest context
        messages = [HumanMessage(content=system_prompt)] + state["messages"]
        response = self.llm.invoke(messages)
        
        return {"messages": [response]}

    def run(self, user_input: str):
        """Runs the nervous system loop."""
        initial_state = {"messages": [HumanMessage(content=user_input)], "context": ""}
        result = self.app.invoke(initial_state)
        
        # Save interaction to memory for future retrieval
        final_response = result["messages"][-1].content
        self.memory.add_memory(f"Soru: {user_input}\nCevap: {final_response}")
        
        return final_response
