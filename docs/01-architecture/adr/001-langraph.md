# ADR-001: Use LangGraph for AI Workflow Orchestration

**Status**: ✅ Accepted  
**Date**: 2025-10-17  
**Deciders**: Константин (CEO), Development Team  
**Tags**: architecture, ai, orchestration

---

## Context

Business Planner requires complex AI workflows for processing voice messages into structured tasks. The voice-to-task flow involves multiple steps:

1. Voice transcription (Whisper API)
2. Text parsing for structure (GPT-5 Nano)
3. Business context detection (GPT-5 Nano)
4. Deadline interpretation (GPT-5 Nano)
5. Time estimation with RAG (GPT-5 Nano + vector search)
6. Task creation and response formatting

Additionally, we need:
- **State management** between steps
- **Error handling** and retry logic
- **Checkpointing** for long-running processes
- **Parallel execution** where possible
- **Extensibility** for future workflows (daily planning, weekly analytics)

---

## Decision

We will use **LangGraph** for orchestrating all AI workflows in Business Planner.

---

## Alternatives Considered

### 1. Simple Sequential Chains (LangChain)
**Description**: Basic sequential execution of AI calls

**Pros**:
- ✅ Simple to understand
- ✅ Easy to implement
- ✅ Less boilerplate code

**Cons**:
- ❌ No built-in state management
- ❌ Difficult error handling
- ❌ No checkpointing
- ❌ Hard to implement conditional logic
- ❌ No parallel execution
- ❌ Doesn't scale to complex workflows

**Verdict**: ❌ **Rejected** - Too simplistic for our needs

---

### 2. Custom Async Pipeline
**Description**: Build our own async workflow orchestrator

**Pros**:
- ✅ Full control
- ✅ No external dependencies
- ✅ Can optimize exactly for our use case

**Cons**:
- ❌ Significant development time
- ❌ Need to implement state management
- ❌ Need to implement checkpointing
- ❌ Need to implement error handling
- ❌ Maintenance burden
- ❌ Reinventing the wheel

**Verdict**: ❌ **Rejected** - Too much custom infrastructure work

---

### 3. Apache Airflow / Prefect
**Description**: General-purpose workflow orchestration

**Pros**:
- ✅ Mature and battle-tested
- ✅ Great UI for monitoring
- ✅ Scheduling capabilities

**Cons**:
- ❌ Overkill for our use case
- ❌ Designed for data pipelines, not AI
- ❌ Heavy infrastructure requirements
- ❌ Not optimized for LLM workflows
- ❌ Slower execution for real-time use

**Verdict**: ❌ **Rejected** - Too heavy, not AI-focused

---

### 4. LangGraph ⭐
**Description**: Graph-based orchestration specifically for LLM workflows

**Pros**:
- ✅ **Built for LLM workflows** - Designed specifically for AI applications
- ✅ **State management** - Built-in state handling between nodes
- ✅ **Checkpointing** - Can save and resume workflow state
- ✅ **Conditional edges** - Easy branching logic
- ✅ **Parallel execution** - Can run independent nodes in parallel
- ✅ **Error handling** - Retry logic and error nodes
- ✅ **Streaming** - Supports streaming responses
- ✅ **Extensible** - Easy to add new workflows
- ✅ **Debugging** - Visual representation of workflows
- ✅ **LangChain integration** - Works with existing LangChain components

**Cons**:
- ⚠️ Relatively new (but actively developed by LangChain team)
- ⚠️ Smaller community than Airflow
- ⚠️ Learning curve for graph-based thinking

**Verdict**: ✅ **Accepted** - Best fit for AI workflows

---

## Rationale

### Why LangGraph Wins

#### 1. **AI-Native Design**
LangGraph is specifically built for LLM workflows, not adapted from general pipeline tools:
- Understands LLM concepts (prompts, context, streaming)
- Optimized for AI API calls (retries, timeouts, rate limiting)
- Built-in support for common LLM patterns

#### 2. **State Management**
Critical for our multi-step workflows:
```python
class VoiceTaskState(TypedDict):
    audio: bytes
    transcript: str
    parsed_data: dict
    business_id: int
    similar_tasks: list
    estimated_duration: int
    task: Task
```
State flows through nodes automatically.

#### 3. **Checkpointing**
For long-running or expensive operations:
- Save state after each node
- Resume if failure occurs
- Avoid re-running expensive AI calls
- Critical for weekly analytics (GPT-5 usage)

#### 4. **Conditional Logic**
Easy to implement business rules:
```python
def route_by_business(state: VoiceTaskState) -> str:
    if state["business_id"] == BusinessID.INVENTUM:
        return "inventum_specific_processing"
    return "default_processing"

graph.add_conditional_edges("parse", route_by_business)
```

#### 5. **Parallel Execution**
When tasks are independent:
```python
# Run in parallel: time estimation + member suggestion
graph.add_node("estimate_time", estimate_time_node)
graph.add_node("suggest_member", suggest_member_node)
# Both run simultaneously after parse_node
```

#### 6. **Error Handling**
Built-in retry and fallback:
```python
@retry(max_attempts=3, backoff=exponential)
async def parse_node(state: VoiceTaskState):
    try:
        return await gpt_parse(state["transcript"])
    except RateLimitError:
        # Automatic retry with backoff
        raise
    except ValidationError as e:
        # Route to error handling node
        return {"error": str(e), "next": "error_handler"}
```

#### 7. **Extensibility**
Easy to add new workflows:
- `voice_task_creation_graph`
- `daily_planning_graph`
- `weekly_analytics_graph`
- `task_completion_graph`

All share common nodes and patterns.

---

## Implementation Strategy

### Phase 1: Core Workflow (Week 1-2)
```python
from langgraph.graph import StateGraph

# Voice-to-Task Graph
voice_task_graph = StateGraph(VoiceTaskState)

# Add nodes
voice_task_graph.add_node("transcribe", transcribe_voice_node)
voice_task_graph.add_node("parse", parse_task_node)
voice_task_graph.add_node("detect_business", detect_business_node)
voice_task_graph.add_node("estimate_time", estimate_time_rag_node)
voice_task_graph.add_node("create_task", create_task_node)
voice_task_graph.add_node("format_response", format_response_node)

# Define edges
voice_task_graph.add_edge("transcribe", "parse")
voice_task_graph.add_edge("parse", "detect_business")
voice_task_graph.add_edge("detect_business", "estimate_time")
voice_task_graph.add_edge("estimate_time", "create_task")
voice_task_graph.add_edge("create_task", "format_response")

# Set entry and finish
voice_task_graph.set_entry_point("transcribe")
voice_task_graph.set_finish_point("format_response")

# Compile with checkpointing
app = voice_task_graph.compile(
    checkpointer=PostgresCheckpointer()
)
```

### Phase 2: Advanced Workflows (Week 3-4)
- Daily planning graph
- Weekly analytics graph  
- Task completion with learning graph

### Phase 3: Optimization (Week 5+)
- Parallel node execution
- Caching frequently used nodes
- Streaming responses to user

---

## Consequences

### Positive
- ✅ **Maintainable**: Clear workflow structure
- ✅ **Debuggable**: Visual graph representation
- ✅ **Extensible**: Easy to add new features
- ✅ **Reliable**: Built-in error handling and retries
- ✅ **Performant**: Parallel execution where possible
- ✅ **Stateful**: No need to pass state manually
- ✅ **Testable**: Can test individual nodes
- ✅ **Resumable**: Checkpointing prevents data loss

### Negative
- ⚠️ **Learning curve**: Team needs to learn graph-based thinking
- ⚠️ **Debugging complexity**: More complex than linear code
- ⚠️ **Dependency**: Relies on LangGraph library maintenance

### Mitigation
- **Learning**: Create examples and documentation
- **Debugging**: Use LangGraph's built-in visualization tools
- **Dependency**: LangGraph is maintained by LangChain (well-funded)

---

## Compliance

### With Project Requirements
- ✅ Supports voice → task workflow
- ✅ Enables RAG time estimation
- ✅ Allows business context isolation (per-node filtering)
- ✅ Scalable for future features (analytics, planning)
- ✅ Fast enough for real-time (<10 second goal)

### With Tech Stack
- ✅ Works with FastAPI (async)
- ✅ Integrates with PostgreSQL (checkpointing)
- ✅ Supports OpenAI APIs (GPT-5 Nano, Whisper)
- ✅ Compatible with Redis (caching)

---

## References

- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [LangGraph GitHub](https://github.com/langchain-ai/langgraph)
- [LangChain Blog on LangGraph](https://blog.langchain.dev/langgraph/)
- Project: `planning/PROJECT_PLAN.md`
- Brief: `docs/00-project-brief.md`

---

## Review History

- **2025-10-17**: Initial version - LangGraph selected
- **Status**: ✅ Accepted and ready for implementation

---

**Decision**: Use LangGraph for all AI workflow orchestration  
**Confidence**: High (9/10)  
**Risk**: Low  
**Impact**: High (core architecture decision)



