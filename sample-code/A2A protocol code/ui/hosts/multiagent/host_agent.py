from typing import List, Any
import os
from a2a.types import AgentCard
try:
    from google.adk.agents import LlmAgent
except ImportError:
    # Fallback if google.adk is not installed or different version
    class LlmAgent:
        def __init__(self, name, model, description, instruction=None, tools=None, sub_agents=None):
            self.name = name
            self.model = model
            self.description = description
            self.instruction = instruction
            self.tools = tools
            self.sub_agents = sub_agents

class HostAgent:
    def __init__(self, sub_agents: List[Any], http_client: Any, callback: Any):
        self.sub_agents = sub_agents
        self.http_client = http_client
        self.callback = callback
        self.agent_cards: List[AgentCard] = []

    def register_agent_card(self, agent_card: AgentCard):
        self.agent_cards.append(agent_card)

    def create_agent(self):
        # Return a simple agent for now.
        # In a real implementation, this would likely configure the agent 
        # with tools to call the registered remote agents.
        
        model_name = os.getenv("GOOGLE_MODEL_NAME", "gemini-1.5-flash-latest")
        model = model_name

        if "deepseek" in model_name.lower():
            try:
                from google.adk.models.lite_llm import LiteLlm
                # Ensure model name has provider prefix if not present
                if "/" not in model_name:
                    # Default to deepseek provider if not specified
                    model_name = f"deepseek/{model_name}"
                
                print(f"Using LiteLlm with model: {model_name}")
                model = LiteLlm(model=model_name)
            except ImportError as e:
                print(f"Could not import LiteLlm: {e}. Falling back to string.")

        return LlmAgent(
            name="host_agent",
            model=model, 
            description="Host Agent for A2A communication",
            instruction="You are a host agent coordinating other agents."
        )
