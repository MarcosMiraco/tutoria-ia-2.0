from langgraph.graph import StateGraph, MessagesState, START
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode, tools_condition

from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate

from ai.tools import llm_rag_tool
from ai.prompt import SYSTEM_PROMPT

from datetime import datetime
from dotenv import load_dotenv
load_dotenv()



class GeneralAssistant:

    def __init__(self):
        # self.llm = init_chat_model(model="gpt-4o-mini", temperature=0.6)
        self.llm = init_chat_model(model="qwen2.5:7b", temperature=0.6, model_provider="ollama")
        self.thread = { "configurable": { "thread_id": "agent-1" }}
        self.tools = [llm_rag_tool]
        self.graph = self.build_graph()

    # UTIL
    def save_graph_schema(self, graph):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"graph_{timestamp}.mmd"
        mermaid_code = graph.get_graph(xray=True).draw_mermaid()
        with open(file_path, "w") as f:
            f.write(mermaid_code)
    # NODE BUILDERS
    def make_tool_caller_node(self, system_prompt):
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{messages}")
        ])
        chain = ( prompt | self.llm.bind_tools(self.tools) )

        def tool_caller_node(state: MessagesState) -> MessagesState:
            response = chain.invoke({ "messages": state["messages"]})
            return { "messages": [response] } 
        return tool_caller_node
    

    def build_graph(self):
        # BUILDING NODES
        assistant = self.make_tool_caller_node(SYSTEM_PROMPT)
        # GRAPH SETUP
        builder = StateGraph(MessagesState)
        # NODES
        builder.add_node("assistant", assistant)
        builder.add_node("tools", ToolNode(self.tools))
        # EDGES
        builder.add_edge(START, "assistant")
        builder.add_conditional_edges("assistant", tools_condition)
        builder.add_edge("tools", "assistant")
        

        # COMPILATION
        memory = MemorySaver()
        graph = builder.compile(checkpointer=memory)
        # self.save_graph_schema(graph)
        return graph

    def ask(self, query_input):
        initial_state = { "messages": [query_input] }
        final_state = self.graph.invoke(input=initial_state, config=self.thread)
        
        for message in reversed(final_state["messages"]):
            if hasattr(message, "content") and message.content and not getattr(message, "tool_calls", None):
                return message.content
        
        return final_state["messages"][-1].content
    
