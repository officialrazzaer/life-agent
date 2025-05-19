## Phase 2: Intelligence Layer

### Step 7: LangChain Agent Setup

Now that the foundation is in place, build the intelligence layer using LangChain to create a reasoning agent:

```python
# src/agent/core.py
import os
from langchain.llms import OpenAI
from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class PersonalAIAgent:
    def __init__(self):
        self.llm = OpenAI(temperature=0, model_name="gpt-4")
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.tools = self._setup_tools()
        self.agent_executor = self._setup_agent()

    def _setup_tools(self):
        # Define tools the agent can use
        tools = [
            Tool(
                name="QueryDailyLogs",
                func=self._query_daily_logs,
                description="Search through daily logs to find patterns or specific entries"
            ),
            Tool(
                name="QueryGymLogs",
                func=self._query_gym_logs,
                description="Search through gym logs to analyze workout patterns and progress"
            ),
            # Add more tools for other data types
        ]
        return tools

    def _setup_agent(self):
        # Set up the agent with tools and memory
        # This is a simplified version - you'll need to implement the actual agent logic
        agent = LLMSingleActionAgent(
            llm_chain=LLMChain(llm=self.llm, prompt=self._get_prompt_template()),
            allowed_tools=[tool.name for tool in self.tools],
            # Add other required parameters
        )

        return AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=True
        )

    def _get_prompt_template(self):
        # Create a prompt template for the agent
        # This is a placeholder - you'll need to create a proper prompt template
        pass

    def _query_daily_logs(self, query: str) -> str:
        # Implement logic to query daily logs
        # This will use both structured queries and vector similarity search
        pass

    def _query_gym_logs(self, query: str) -> str:
        # Implement logic to query gym logs
        pass

    # Implement other tool functions

    def process_query(self, query: str) -> str:
        """Process a natural language query using the agent."""
        return self.agent_executor.run(query)
```
