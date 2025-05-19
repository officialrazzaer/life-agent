import os
from langgraph.graph import StateGraph, END
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
from datetime import datetime, timedelta
from src.db.supabase_client import SupabaseManager
from src.db.vector_store import ChromaDBManager
from typing import TypedDict, List

load_dotenv()

# Define the state schema for LangGraph
class AgentState(TypedDict):
    input: str
    subquestions: List[str]
    tool_choices: List[str]
    tool_results: List[str]
    output: str

# Tool: Query daily logs from Supabase
@tool
def query_daily_logs_tool(query: str) -> str:
    """Fetch the last 7 days of daily logs for the user."""
    user_id = os.getenv("USER_UUID")
    if not user_id:
        return "[QueryDailyLogs] USER_UUID not set in environment."
    today = datetime.utcnow().date()
    week_ago = today - timedelta(days=7)
    supabase = SupabaseManager()
    filters = {"user_id": user_id}
    response = supabase.select_data(
        table_name="daily_logs",
        columns="*",
        filters=filters
    )
    if not response or not response.data:
        return "No daily logs found."
    logs = [log for log in response.data if log.get("date") and week_ago <= datetime.strptime(log["date"], "%Y-%m-%d").date() <= today]
    if not logs:
        return "No daily logs found in the last 7 days."
    return f"Daily logs for the last 7 days: {logs}"

# Tool: Semantic search in ChromaDB
@tool
def chroma_semantic_search_tool(query: str) -> str:
    """Perform a semantic search in ChromaDB for similar personal logs."""
    chroma = ChromaDBManager(collection_name="my_life_logs")
    results = chroma.query_collection(query_text=query, n_results=3)
    return f"Chroma semantic search results: {results}"

# Tool: Web search using DuckDuckGo
@tool
def web_search_tool(query: str) -> str:
    """Search the web for up-to-date information using DuckDuckGo."""
    search = DuckDuckGoSearchRun()
    return search.run(query)

class PersonalAIAgent:
    def __init__(self):
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4")
        self.tools = {
            "query_daily_logs": query_daily_logs_tool,
            "chroma_semantic_search": chroma_semantic_search_tool,
            "web_search": web_search_tool
        }
        self.graph = self._setup_graph()
        # Load persistent user context
        try:
            with open("about_me.txt", "r") as f:
                self.about_me = f.read()
        except Exception:
            self.about_me = ""

    def _decompose_node(self, state: AgentState) -> AgentState:
        # Use LLM to break the input into subquestions and assign tools
        prompt = (
            "You are an assistant with access to three tools: "
            "1. query_daily_logs (for personal structured data), "
            "2. chroma_semantic_search (for semantic search in personal logs), "
            "3. web_search (for up-to-date internet info). "
            "Given the user query, break it into subquestions. "
            "For each subquestion, decide which tool to use: 'query_daily_logs', 'chroma_semantic_search', or 'web_search'. "
            "Return a JSON list of subquestions and a parallel list of tool names. "
            "User query: {query}"
        )
        llm_response = self.llm.invoke(prompt.format(query=state["input"]))
        import json
        try:
            # Expecting a JSON like: {"subquestions": [...], "tool_choices": [...]}
            parsed = json.loads(llm_response.content if hasattr(llm_response, "content") else str(llm_response))
            state["subquestions"] = parsed["subquestions"]
            state["tool_choices"] = parsed["tool_choices"]
        except Exception as e:
            # Fallback: treat the whole input as one subquestion for daily logs
            state["subquestions"] = [state["input"]]
            state["tool_choices"] = ["query_daily_logs"]
        state["tool_results"] = []
        return state

    def _tool_loop_node(self, state: AgentState) -> AgentState:
        # For each subquestion, call the assigned tool and collect results
        results = []
        for subq, tool_name in zip(state["subquestions"], state["tool_choices"]):
            tool_func = self.tools.get(tool_name, query_daily_logs_tool)
            try:
                result = tool_func(subq)
            except Exception as e:
                result = f"[Error calling {tool_name}]: {e}"
            results.append(result)
        state["tool_results"] = results
        return state

    def _synthesis_node(self, state: AgentState) -> AgentState:
        # Use LLM to combine all tool results into a final answer
        prompt = (
            f"About the user (persistent context):\n{self.about_me}\n\n"
            "You are a helpful assistant. The user asked: {query}\n"
            "Here are the results from various tools (personal data, semantic search, web):\n"
            "{results}\n"
            "Please combine these into a single, helpful answer. Limit your response to 300 words."
        )
        llm_response = self.llm.invoke(prompt.format(query=state["input"], results="\n".join(state["tool_results"])))
        state["output"] = llm_response.content if hasattr(llm_response, "content") else str(llm_response)
        return state

    def _setup_graph(self):
        workflow = StateGraph(AgentState)
        workflow.add_node("decompose", self._decompose_node)
        workflow.add_node("tool_loop", self._tool_loop_node)
        workflow.add_node("synthesis", self._synthesis_node)
        workflow.add_edge("decompose", "tool_loop")
        workflow.add_edge("tool_loop", "synthesis")
        workflow.add_edge("synthesis", END)
        workflow.set_entry_point("decompose")
        return workflow.compile()

    def process_query(self, query: str) -> str:
        result = self.graph.invoke({"input": query})
        return result.get("output", str(result)) 