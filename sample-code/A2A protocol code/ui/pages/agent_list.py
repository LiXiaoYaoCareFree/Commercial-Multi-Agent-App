import asyncio

import mesop as me

from components.agent_list import agents_list
from components.dialog import dialog, dialog_actions
from components.header import header
from components.page_scaffold import page_frame, page_scaffold
from state.agent_state import AgentState, AgentEntry, AgentListState
from state.host_agent_service import AddRemoteAgent, ListRemoteAgents
from state.state import AppState
from utils.agent_card import get_agent_card
from a2a.types import AgentCard
from typing import Any
import asyncio


def map_agent_card_to_entry(card: AgentCard) -> AgentEntry:
    streaming = False
    push_notifications = False
    if card.capabilities:
        streaming = card.capabilities.streaming or False
        push_notifications = card.capabilities.push_notifications or False
    
    return AgentEntry(
        name=card.name or '',
        url=card.url or '',
        description=card.description or '',
        organization=card.provider.organization if card.provider else '',
        default_input_modes=card.default_input_modes or [],
        default_output_modes=card.default_output_modes or [],
        streaming=streaming,
        push_notifications=push_notifications
    )


async def refresh_agents(e: me.ClickEvent) -> None:
    list_state = me.state(AgentListState)
    agents = await ListRemoteAgents()
    list_state.agents = [map_agent_card_to_entry(agent) for agent in agents]
    list_state.initialized = True


def agent_list_page(app_state: AppState) -> None:
    """Agents List Page."""
    state = me.state(AgentState)
    list_state = me.state(AgentListState)
    
    with page_scaffold():  # pylint: disable=not-context-manager
        with page_frame():
            with header('Remote Agents', 'smart_toy'):
                me.button('Refresh', on_click=refresh_agents)
            
            if not list_state.initialized:
                try:
                    agents = asyncio.run(ListRemoteAgents())
                    list_state.agents = [map_agent_card_to_entry(agent) for agent in agents]
                    list_state.initialized = True
                except Exception as e:
                    print(f"Error loading agents: {e}")
                    list_state.agents = []
                    list_state.initialized = True
            
            agents_list(list_state.agents)
            with dialog(state.agent_dialog_open):
                with me.box(
                    style=me.Style(
                        display='flex', flex_direction='column', gap=12
                    )
                ):
                    me.input(
                        label='Agent Address',
                        on_blur=set_agent_address,
                        placeholder='localhost:10000',
                    )
                    input_modes_string = ', '.join(state.input_modes)
                    output_modes_string = ', '.join(state.output_modes)

                    if state.error != '':
                        me.text(state.error, style=me.Style(color='red'))
                    if state.agent_name != '':
                        me.text(f'Agent Name: {state.agent_name}')
                    if state.agent_description:
                        me.text(f'Agent Description: {state.agent_description}')
                    if state.agent_framework_type:
                        me.text(
                            f'Agent Framework Type: {state.agent_framework_type}'
                        )
                    if state.input_modes:
                        me.text(f'Input Modes: {input_modes_string}')
                    if state.output_modes:
                        me.text(f'Output Modes: {output_modes_string}')

                    if state.agent_name:
                        me.text(
                            f'Streaming Supported: {state.stream_supported}'
                        )
                        me.text(
                            f'Push Notifications Supported: {state.push_notifications_supported}'
                        )
                with dialog_actions():
                    if not state.agent_name:
                        me.button('Read', on_click=load_agent_info)
                    elif not state.error:
                        me.button('Save', on_click=save_agent)
                    me.button('Cancel', on_click=cancel_agent_dialog)


def set_agent_address(e: me.InputBlurEvent) -> None:
    state = me.state(AgentState)
    state.agent_address = e.value


async def load_agent_info(e: me.ClickEvent) -> None:
    state = me.state(AgentState)
    try:
        state.error = ''
        agent_card_response = get_agent_card(state.agent_address)
        state.agent_name = agent_card_response.name or ''
        state.agent_description = agent_card_response.description or ''
        state.agent_framework_type = (
            agent_card_response.provider.organization
            if agent_card_response.provider
            else ''
        )
        state.input_modes = agent_card_response.default_input_modes or []
        state.output_modes = agent_card_response.default_output_modes or []
        
        if agent_card_response.capabilities:
            state.stream_supported = agent_card_response.capabilities.streaming or False
            state.push_notifications_supported = (
                agent_card_response.capabilities.push_notifications or False
            )
        else:
            state.stream_supported = False
            state.push_notifications_supported = False
            
    except Exception as e:
        print(e)
        state.agent_name = ''
        state.error = f'Cannot connect to agent as {state.agent_address}'


def cancel_agent_dialog(e: me.ClickEvent) -> None:
    state = me.state(AgentState)
    state.agent_dialog_open = False


async def save_agent(e: me.ClickEvent) -> None:
    state = me.state(AgentState)
    await AddRemoteAgent(state.agent_address)
    state.agent_address = ''
    state.agent_name = ''
    state.agent_description = ''
    state.agent_dialog_open = False
    # Refresh the list
    list_state = me.state(AgentListState)
    agents = await ListRemoteAgents()
    list_state.agents = [map_agent_card_to_entry(agent) for agent in agents]

