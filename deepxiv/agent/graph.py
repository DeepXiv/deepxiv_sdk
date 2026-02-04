"""
LangGraph workflow for the ReAct agent.
"""
import time
import json
from typing import Dict, List, Literal, Optional
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from openai import OpenAI

from .state import AgentState
from .tools import get_tools_definition, ToolExecutor, format_paper_context
from .prompts import get_system_prompt


def call_llm(
    messages: List[Dict],
    client: OpenAI,
    model_name: str = "gpt-4",
    tools: Optional[List] = None,
    max_tries: int = 3,
    max_tokens: int = 4096,
    temperature: float = 0.7,
    stream: bool = False,
    print_process: bool = False
) -> tuple[str, Optional[List]]:
    """
    Call LLM with retry logic.

    Args:
        messages: List of messages
        client: OpenAI client instance
        model_name: Model name
        tools: Tool definitions
        max_tries: Max retry attempts
        max_tokens: Max tokens to generate
        temperature: Sampling temperature
        stream: Whether to use streaming output
        print_process: Whether to print the process

    Returns:
        Tuple of (content, tool_calls)
    """
    import random

    base_sleep_time = 1
    for attempt in range(max_tries):
        try:
            if print_process:
                print(f"--- Calling LLM, attempt {attempt + 1}/{max_tries} ---")

            # Prepare request parameters
            request_params = {
                "model": model_name,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream,
            }

            # Add tools if provided
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"

            if stream:
                # Streaming mode
                if print_process:
                    print("--- LLM streaming started ---")

                response_stream = client.chat.completions.create(**request_params)

                content = ""
                tool_calls = None
                tool_calls_dict = {}

                for chunk in response_stream:
                    if hasattr(chunk.choices[0], 'delta'):
                        delta = chunk.choices[0].delta

                        # Handle regular content
                        if hasattr(delta, 'content') and delta.content:
                            content += delta.content
                            if print_process:
                                print(delta.content, end='', flush=True)

                        # Handle tool calls (streaming)
                        if hasattr(delta, 'tool_calls') and delta.tool_calls:
                            for tc in delta.tool_calls:
                                idx = tc.index
                                if idx not in tool_calls_dict:
                                    tool_calls_dict[idx] = {
                                        'id': tc.id or '',
                                        'type': 'function',
                                        'function': {
                                            'name': '',
                                            'arguments': ''
                                        }
                                    }

                                if hasattr(tc, 'function'):
                                    if tc.function.name:
                                        tool_calls_dict[idx]['function']['name'] = tc.function.name
                                    if tc.function.arguments:
                                        tool_calls_dict[idx]['function']['arguments'] += tc.function.arguments

                if print_process and content:
                    print()  # New line after streaming

                # Convert tool_calls_dict to list
                if tool_calls_dict:
                    tool_calls = [tool_calls_dict[i] for i in sorted(tool_calls_dict.keys())]

                if content and content.strip():
                    if print_process:
                        print("--- LLM streaming completed successfully ---")
                    return content.strip(), tool_calls
                elif tool_calls:
                    if print_process:
                        print("--- LLM streaming completed with tool calls ---")
                    return "", tool_calls
                else:
                    if print_process:
                        print(f"Warning: Attempt {attempt + 1} received an empty response.")
            else:
                # Non-streaming mode
                response = client.chat.completions.create(**request_params)

                message = response.choices[0].message
                content = message.content or ""
                tool_calls = None

                # Check for tool calls
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    tool_calls = [
                        {
                            'id': tc.id,
                            'type': tc.type,
                            'function': {
                                'name': tc.function.name,
                                'arguments': tc.function.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]

                if content and content.strip():
                    if print_process:
                        print("--- LLM call successful ---")
                        print(f"Response: {content[:200]}...")
                    return content.strip(), tool_calls
                elif tool_calls:
                    if print_process:
                        print("--- LLM call successful, received tool calls ---")
                    return "", tool_calls
                else:
                    if print_process:
                        print(f"Warning: Attempt {attempt + 1} received an empty response.")

        except Exception as e:
            if print_process:
                print(f"Error: Attempt {attempt + 1} failed with error: {e}")

        if attempt < max_tries - 1:
            sleep_time = base_sleep_time * (2 ** attempt) + random.uniform(0, 1)
            sleep_time = min(sleep_time, 5)
            if print_process:
                print(f"Retrying in {sleep_time:.2f} seconds...")
            time.sleep(sleep_time)
        else:
            if print_process:
                print("Error: All retry attempts exhausted.")

    return "LLM server error!!!", None


def planning_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """Planning node - calls LLM to reason and decide actions."""
    configurable = config.get("configurable", {})

    max_time_seconds = configurable.get("max_time_seconds", 600)
    print_process = configurable.get("print_process", False)

    # Check time limit
    if time.time() - state["start_time"] > max_time_seconds:
        return {
            "prediction": "No answer found - timeout",
            "termination": "timeout",
            "status": state["status"] + ["timeout"]
        }

    # Check LLM call limit
    if state["num_llm_calls_available"] <= 0:
        return {
            "prediction": "No answer found - exceeded call limit",
            "termination": "exceeded_calls",
            "status": state["status"] + ["exceeded_calls"]
        }

    # Get messages
    messages = state.get("messages", [])

    # Initialize messages if empty
    if not messages:
        # Build system prompt with paper context
        paper_context = format_paper_context(state["papers"])
        current_date = time.strftime("%Y-%m-%d")
        system_content = get_system_prompt(paper_context, current_date)

        initial_messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": state["question"]}
        ]
        messages_to_add = initial_messages
        all_messages = initial_messages
    else:
        messages_to_add = []
        all_messages = messages

    # Get tools
    tools = get_tools_definition()

    # Get LLM config
    client = configurable.get("client")
    model_name = configurable.get("model_name", "gpt-4")
    max_tokens = configurable.get("max_tokens", 4096)
    temperature = configurable.get("temperature", 0.7)
    stream = configurable.get("stream", False)

    # Call LLM
    content, tool_calls = call_llm(
        messages=all_messages,
        client=client,
        model_name=model_name,
        tools=tools,
        max_tokens=max_tokens,
        temperature=temperature,
        stream=stream,
        print_process=print_process
    )

    if print_process:
        print(f"\n{'='*80}")
        print(f"Round {state['round'] + 1}")
        print(f"Response length: {len(content)} chars")
        print(f"Tool calls: {len(tool_calls) if tool_calls else 0}")
        print(f"{'='*80}\n")

    # Add assistant message
    assistant_message = {"role": "assistant", "content": content.strip()}
    if tool_calls:
        assistant_message["tool_calls"] = tool_calls
    messages_to_add.append(assistant_message)

    # Determine status
    new_status = state["status"].copy()
    if tool_calls:
        new_status.append("tool_call")
    elif '<answer>' in content and '</answer>' in content:
        new_status.append("answer")
    else:
        # Check if it looks like a final answer
        if state["round"] >= 1 and len(content.strip()) > 50:
            if print_process:
                print("⚠️ Response looks like a final answer")
            new_status.append("answer")
        else:
            new_status.append("continue")

    return {
        "messages": messages_to_add,
        "response": content.strip(),
        "status": new_status,
        "round": state["round"] + 1,
        "num_llm_calls_available": state["num_llm_calls_available"] - 1,
    }


def tool_call_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """Tool call node - executes tool calls."""
    configurable = config.get("configurable", {})
    print_process = configurable.get("print_process", False)
    tool_executor = configurable.get("tool_executor")

    # Get the last assistant message with tool calls
    messages = state.get("messages", [])
    tool_calls = None
    for msg in reversed(messages):
        if msg.get("role") == "assistant" and msg.get("tool_calls"):
            tool_calls = msg["tool_calls"]
            break

    if not tool_calls:
        return {
            "messages": [{"role": "tool", "content": "Error: No tool calls found."}],
            "status": state["status"] + ["tool_response"]
        }

    # Execute each tool call
    tool_results = []
    for tool_call in tool_calls:
        tool_id = tool_call.get("id", "")
        function_name = tool_call.get("function", {}).get("name", "")
        function_args_str = tool_call.get("function", {}).get("arguments", "{}")

        # Parse arguments
        try:
            function_args = json.loads(function_args_str) if isinstance(function_args_str, str) else function_args_str
        except:
            function_args = {}

        if print_process:
            print(f"\n📞 Calling tool: {function_name}")
            print(f"   Arguments: {function_args}")

        # Execute tool
        result = tool_executor.execute_tool_call(function_name, function_args, state)

        if print_process:
            print(f"✅ Tool result length: {len(result)} chars")
            print(f"   Preview: {result[:200]}...")

        tool_results.append({
            "role": "tool",
            "tool_call_id": tool_id,
            "content": result
        })

    return {
        "messages": tool_results,
        "status": state["status"] + ["tool_response"]
    }


def check_limits_node(state: AgentState, config: RunnableConfig) -> AgentState:
    """Check if limits are reached and request final answer if needed."""
    configurable = config.get("configurable", {})
    max_llm_calls = configurable.get("max_llm_calls", 20)
    print_process = configurable.get("print_process", False)

    # Check if approaching limit
    if state["round"] >= max_llm_calls - 2:
        if print_process:
            print(f"\n⚠️ Approaching call limit, requesting final answer...")

        messages = state.get("messages", []).copy()
        limit_message = """You are approaching the maximum number of calls. Please provide your final answer now based on all the information you have gathered.

Wrap your final answer in <answer></answer> tags."""

        messages.append({"role": "user", "content": limit_message})

        # Call for final answer (no tools)
        client = configurable.get("client")
        model_name = configurable.get("model_name", "gpt-4")
        max_tokens = configurable.get("max_tokens", 4096)
        temperature = configurable.get("temperature", 0.7)
        stream = configurable.get("stream", False)

        content, _ = call_llm(
            messages=messages,
            client=client,
            model_name=model_name,
            tools=None,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=stream,
            print_process=print_process
        )

        new_messages = [{"role": "assistant", "content": content.strip()}]

        if '<answer>' in content and '</answer>' in content:
            prediction = content.split('<answer>')[1].split('</answer>')[0].strip()
            termination = 'answer (limit reached)'
        else:
            prediction = content.strip()
            termination = 'limit reached'

        return {
            "messages": new_messages,
            "response": content.strip(),
            "prediction": prediction,
            "termination": termination,
            "status": state["status"] + ["answer"],
        }

    return {}


def router_node(state: AgentState) -> Literal["tool_call", "check_limits", "answer", "continue"]:
    """Router to determine next step."""
    if not state.get("status"):
        return "continue"

    last_status = state["status"][-1]

    if last_status == "tool_call":
        return "tool_call"
    elif last_status == "answer":
        return "answer"
    elif last_status in ["timeout", "exceeded_calls"]:
        return "answer"
    else:
        return "check_limits"


def finalize_node(state: AgentState) -> AgentState:
    """Finalize and extract answer."""
    response = state.get("response", "")

    if '<answer>' in response and '</answer>' in response:
        prediction = response.split('<answer>')[1].split('</answer>')[0].strip()
        termination = 'answer'
    else:
        # Try to find answer in messages
        messages = state.get("messages", [])
        found_answer = False

        for msg in reversed(messages):
            if msg.get("role") == "assistant":
                content = msg.get("content", "")
                if '<answer>' in content and '</answer>' in content:
                    prediction = content.split('<answer>')[1].split('</answer>')[0].strip()
                    termination = 'answer'
                    found_answer = True
                    break

        if not found_answer:
            # Use the last substantial assistant message
            for msg in reversed(messages):
                if msg.get("role") == "assistant":
                    content = msg.get("content", "")
                    if content and len(content.strip()) > 20 and not msg.get("tool_calls"):
                        prediction = content.strip()
                        termination = 'answer (no tags)'
                        found_answer = True
                        break

            if not found_answer:
                prediction = 'No answer found.'
                termination = 'no_answer'

    return {
        "prediction": prediction,
        "termination": termination
    }


def create_react_graph() -> StateGraph:
    """Create the ReAct workflow graph."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("planning", planning_node)
    workflow.add_node("tool_call", tool_call_node)
    workflow.add_node("check_limits", check_limits_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point
    workflow.set_entry_point("planning")

    # Add conditional edges from planning
    workflow.add_conditional_edges(
        "planning",
        router_node,
        {
            "tool_call": "tool_call",
            "check_limits": "check_limits",
            "answer": "finalize",
            "continue": "check_limits"
        }
    )

    # Route after check_limits
    def route_after_limits(state: AgentState) -> Literal["planning", "finalize"]:
        if state.get("status", []) and state["status"][-1] == "answer":
            return "finalize"
        return "planning"

    workflow.add_conditional_edges(
        "check_limits",
        route_after_limits,
        {
            "planning": "planning",
            "finalize": "finalize"
        }
    )

    # Tool call goes back to planning
    workflow.add_edge("tool_call", "planning")

    # Finalize is the end
    workflow.add_edge("finalize", END)

    return workflow.compile()


def create_initial_state(papers: Optional[Dict] = None) -> AgentState:
    """Create initial state for the agent."""
    return {
        "papers": papers or {},
        "messages": [],
        "question": "",
        "response": "",
        "status": [],
        "round": 0,
        "num_llm_calls_available": 20,
        "start_time": time.time(),
        "prediction": "",
        "termination": "",
        "paper_sections_cache": {},
        "full_paper_cache": {},
        "search_results_cache": []
    }
