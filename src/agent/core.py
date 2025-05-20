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
import logging

load_dotenv()

# Set up basic logging
logging.basicConfig(level=logging.INFO)

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

# Tool: Query gym logs from Supabase
@tool
def query_gym_logs_tool(query: str) -> str:
    """Fetch recent gym logs for the user."""
    user_id = os.getenv("USER_UUID")
    if not user_id:
        return "[QueryGymLogs] USER_UUID not set in environment."
    supabase = SupabaseManager()
    filters = {"user_id": user_id}
    response = supabase.select_data(
        table_name="gym_logs",
        columns="*",
        filters=filters
    )
    if not response or not response.data:
        return "No gym logs found."
    return f"Gym logs: {response.data}"

# Tool: Query financial transactions from Supabase
@tool
def query_financial_transactions_tool(query: str) -> str:
    """Fetch recent financial transactions for the user."""
    user_id = os.getenv("USER_UUID")
    if not user_id:
        return "[QueryFinancialTransactions] USER_UUID not set in environment."
    supabase = SupabaseManager()
    filters = {"user_id": user_id}
    response = supabase.select_data(
        table_name="financial_transactions",
        columns="*",
        filters=filters
    )
    if not response or not response.data:
        return "No financial transactions found."
    return f"Financial transactions: {response.data}"

# Tool: Custom SQL query
@tool
def custom_sql_tool(sql: str) -> str:
    """Run a custom SQL query on Supabase. Use for advanced calculations or joins."""
    supabase = SupabaseManager()
    try:
        result = supabase.execute_sql(sql)
        return f"SQL result: {result.data}"
    except Exception as e:
        return f"[SQL Error]: {e}"

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
            "query_gym_logs": query_gym_logs_tool,
            "query_financial_transactions": query_financial_transactions_tool,
            "custom_sql": custom_sql_tool,
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
            "You are an assistant with access to these tools and data sources: "
            "1. Supabase tools (query_daily_logs, query_gym_logs, query_financial_transactions, custom_sql) for all structured user data (logs, gym, finance, etc.). "
            "2. chroma_semantic_search for semantic memory and unstructured logs. "
            "3. web_search for up-to-date internet info. "
            "You MUST always use the available Supabase tools to answer any question about the user's data, logs, or history. Do NOT answer from your own knowledge if a tool is available. "
            "Given the user query, break it into subquestions. "
            "For each subquestion, decide which tool to use: 'query_daily_logs', 'query_gym_logs', 'query_financial_transactions', 'custom_sql', 'chroma_semantic_search', or 'web_search'. "
            "Return a JSON list of subquestions and a parallel list of tool names. "
            "User query: {query}"
        )
        llm_response = self.llm.invoke(prompt.format(query=state["input"]))
        import json
        try:
            parsed = json.loads(llm_response.content if hasattr(llm_response, "content") else str(llm_response))
            state["subquestions"] = parsed["subquestions"]
            state["tool_choices"] = parsed["tool_choices"]
        except Exception as e:
            state["subquestions"] = [state["input"]]
            state["tool_choices"] = ["query_daily_logs"]
        # Calculation keywords and table mapping
        calc_keywords = ["average", "avg", "sum", "total", "count", "min", "max"]
        table_keywords = {
            "transaction": "financial_transactions",
            "finance": "financial_transactions",
            "gym": "gym_logs",
            "log": "daily_logs",
            "bjj": "jiujitsu_logs"
        }
        user_id = os.getenv("USER_UUID")
        for i, (subq, tool) in enumerate(zip(state["subquestions"], state["tool_choices"])):
            subq_lower = subq.lower()
            # If calculation keyword and table keyword present, force custom_sql_tool
            if any(kw in subq_lower for kw in calc_keywords):
                for tkw, table in table_keywords.items():
                    if tkw in subq_lower:
                        # Generate SQL for common calculations
                        if "average" in subq_lower or "avg" in subq_lower:
                            sql = f"SELECT AVG(transaction_amount) FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        elif "sum" in subq_lower or "total" in subq_lower:
                            sql = f"SELECT SUM(transaction_amount) FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        elif "count" in subq_lower:
                            sql = f"SELECT COUNT(*) FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        elif "min" in subq_lower:
                            sql = f"SELECT MIN(transaction_amount) FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        elif "max" in subq_lower:
                            sql = f"SELECT MAX(transaction_amount) FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        else:
                            sql = f"SELECT * FROM {table} WHERE user_id = '{user_id}' AND transaction_date >= CURRENT_DATE - INTERVAL '7 days';"
                        state["subquestions"][i] = sql
                        state["tool_choices"][i] = "custom_sql"
                        logging.info(f"[Agent] Detected calculation query. Forcing custom_sql_tool with SQL: {sql}")
            # Fallback: if the query is about spending/expenses/finance but the tool is not financial, add it
            finance_keywords = ["spending", "expense", "expenses", "finance", "financial", "money", "transaction", "transactions", "cost", "budget"]
            if any(word in subq_lower for word in finance_keywords):
                if state["tool_choices"][i] != "query_financial_transactions" and not any(kw in subq_lower for kw in calc_keywords):
                    state["tool_choices"][i] = "query_financial_transactions"
        state["tool_results"] = []
        return state

    def _tool_loop_node(self, state: AgentState) -> AgentState:
        # For each subquestion, call the assigned tool and collect results
        results = []
        for subq, tool_name in zip(state["subquestions"], state["tool_choices"]):
            tool_func = self.tools.get(tool_name, query_daily_logs_tool)
            try:
                logging.info(f"[Agent] Using tool: {tool_name} for subquestion: {subq}")
                result = tool_func(subq)
                logging.info(f"[Agent] Tool result: {result}")
            except Exception as e:
                result = f"[Error calling {tool_name}]: {e}"
                logging.error(result)
            results.append(result)
        state["tool_results"] = results
        return state

    def _synthesis_node(self, state: AgentState) -> AgentState:
        # Use LLM to combine all tool results into a final answer
        # If any tool result is not empty or error, only synthesize from tool results
        if any(r and not r.startswith("[Error") and "No " not in r for r in state["tool_results"]):
            prompt = (
                f"About the user (persistent context):\n{self.about_me}\n\n"
                "You are a helpful assistant. The user asked: {query}\n"
                "Here are the results from various tools (personal data, semantic search, web):\n"
                "{results}\n"
                "Please combine these into a single, helpful answer. Limit your response to 300 words."
            )
            llm_response = self.llm.invoke(prompt.format(query=state["input"], results="\n".join(state["tool_results"])))
            state["output"] = llm_response.content if hasattr(llm_response, "content") else str(llm_response)
        else:
            # If all tool results are empty or errors, fallback to a generic message
            state["output"] = "No relevant data found in your Supabase or ChromaDB tables for this query."
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