
from a2a.types import AgentCard
import json

def inspect_agent_card():
    # Create a dummy agent card with None values if possible
    # We need to know the fields.
    print("Fields:", AgentCard.model_fields.keys())
    
    try:
        # Try to instantiate one
        card = AgentCard(
            name="test",
            description="desc",
            url="http://localhost",
            version="1.0",
            defaultInputModes=["text"],
            defaultOutputModes=["text"],
            capabilities={"streaming": True},
            skills=[],  # Added skills
            # Try to force additionalInterfaces to None if it accepts it
            additionalInterfaces=None 
        )
        print("Card created:", card)
        print("Dump (exclude_none=True):", card.model_dump(exclude_none=True))
        print("Dump (exclude_none=False):", card.model_dump(exclude_none=False))
    except Exception as e:
        print("Error creating card:", e)

if __name__ == "__main__":
    inspect_agent_card()
