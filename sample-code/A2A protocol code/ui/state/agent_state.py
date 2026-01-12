import mesop as me
from dataclasses import field
from typing import Any

@me.stateclass
class AgentEntry:
    """Flattened agent entry for display to avoid nested deserialization issues."""
    name: str = ''
    url: str = ''
    description: str = ''
    organization: str = ''
    default_input_modes: list[str] = field(default_factory=list)
    default_output_modes: list[str] = field(default_factory=list)
    streaming: bool = False
    push_notifications: bool = False

@me.stateclass
class AgentListState:
    """Separate state for the list of agents."""
    agents: list[AgentEntry] = field(default_factory=list)
    # Flag to track if we have attempted to load data at least once
    initialized: bool = False

@me.stateclass
class AgentState:
    """Agents Dialog/Form State"""

    agent_dialog_open: bool = False
    agent_address: str = ''
    agent_name: str = ''
    agent_description: str = ''
    input_modes: list[str] = field(default_factory=list)
    output_modes: list[str] = field(default_factory=list)
    stream_supported: bool = False
    push_notifications_supported: bool = False
    error: str = ''
    agent_framework_type: str = ''
