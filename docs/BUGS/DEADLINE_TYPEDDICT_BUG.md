# Critical Bug: TypedDict Key Mismatch for Deadline

> **Severity**: CRITICAL
> **Discovered**: 2025-10-20
> **Fixed**: 2025-10-20 (commit 6adc1b3)
> **Impact**: Deadlines were not displayed to users despite being parsed correctly

## Summary

The deadline field was being parsed correctly by GPT-5 Nano and stored in the LangGraph state, but the `format_response_node` could not access it due to a **TypedDict key mismatch** between the schema definition and the actual code usage.

## The Bug

### 1. TypedDict Schema Definition
[src/ai/graphs/voice_task_creation.py:48](../src/ai/graphs/voice_task_creation.py#L48)
```python
class VoiceTaskState(TypedDict):
    # ...
    parsed_deadline_text: str | None  # ❌ WRONG KEY NAME
    # ...
```

### 2. Actual Code Usage
Throughout the codebase:
```python
# parse_task_node (line 137)
return {
    **state,
    "parsed_deadline": parsed.deadline,  # ✅ Setting this key
}

# create_task_db_node (line 258)
if state.get("parsed_deadline"):  # ✅ Reading this key
    deadline = datetime.fromisoformat(state["parsed_deadline"])

# format_response_node (line 366)
if state.get("parsed_deadline"):  # ✅ Reading this key
    deadline_dt = datetime.fromisoformat(state["parsed_deadline"])
```

### 3. Result
- LangGraph state schema defined `parsed_deadline_text`
- Code set and read `parsed_deadline`
- LangGraph could not properly manage the undefined key
- `state.get("parsed_deadline")` always returned `None`

## Evidence from Production

### User Report
User: "В сообщении я явно сказал что завтра в 10 утра нужно сделать задачу. А в задаче Дедлайн: не указан."

Translation: "In the message I clearly said tomorrow at 10 AM to do the task. But the task shows Deadline: not specified."

### Production Logs (Before Fix)
```
2025-10-20 13:09:27 [info] task_parsed deadline=2025-10-21T10:00:00 ✅
2025-10-20 13:09:28 [info] format_response_deadline_check deadline_value=None ❌
```

**Analysis**:
- GPT-5 Nano correctly parsed: `deadline=2025-10-21T10:00:00`
- But `format_response_node` received: `deadline_value=None`
- Deadline was lost between nodes!

## Root Cause Analysis

### Why This Was Hard to Find

1. **TypedDict is not enforced at runtime**
   - Python's `TypedDict` only provides type hints for static analysis
   - No runtime validation that keys match the schema
   - Code works fine in isolation

2. **LangGraph uses TypedDict for state schema**
   - LangGraph relies on TypedDict to understand state structure
   - Keys not in the TypedDict may be ignored during state updates
   - The `**state` spread preserved the key, but LangGraph didn't propagate it

3. **State preservation looked correct**
   ```python
   # This looked correct:
   return {
       **state,  # Spreads all existing keys
       "created_task_id": task.id
   }
   ```
   But LangGraph only propagates keys defined in the TypedDict!

4. **No type checking in development**
   - Type checker would have caught this: `"parsed_deadline" not in VoiceTaskState`
   - But without running `mypy`, the error was silent

## The Fix

### 1. Update TypedDict Definition
[src/ai/graphs/voice_task_creation.py:48](../src/ai/graphs/voice_task_creation.py#L48)
```python
class VoiceTaskState(TypedDict):
    # ...
    parsed_deadline: str | None  # ✅ FIXED: Matches code usage
    # ...
```

### 2. Update State Initialization
[src/ai/graphs/voice_task_creation.py:515](../src/ai/graphs/voice_task_creation.py#L515)
```python
initial_state: VoiceTaskState = {
    # ...
    "parsed_deadline": None,  # ✅ FIXED: Was "parsed_deadline_text"
    # ...
}
```

### 3. Update Test Expectations
[tests/unit/test_format_response.py:467-468](../tests/unit/test_format_response.py#L467-L468)
```python
# Should not crash, show error message for invalid format
assert "Дедлайн:" in result["telegram_response"]
assert "ошибка формата" in result["telegram_response"]
```

## Testing

### Before Fix
- 43 tests passing
- Deadline feature broken in production
- User complaints about missing deadlines

### After Fix
- 44 tests passing (updated invalid deadline test)
- Deadline parsing works end-to-end
- Production logs show deadline flowing correctly

### Verification in Production
```bash
# Send voice message: "Починить фрезер завтра в 10 утра"
# Expected logs:
2025-10-20 13:20:15 [info] task_parsed deadline=2025-10-21T10:00:00 ✅
2025-10-20 13:20:15 [info] format_response_deadline_check deadline_value=2025-10-21T10:00:00 ✅
```

## Lessons Learned

### 1. Always Run Type Checkers
Run `mypy` or similar tool in CI/CD:
```bash
mypy src/ --strict
```

This would have caught:
```
error: Key "parsed_deadline" is not defined in VoiceTaskState
```

### 2. TypedDict Limitations
TypedDict provides type hints but no runtime validation. Consider using Pydantic models for runtime validation:
```python
from pydantic import BaseModel

class VoiceTaskState(BaseModel):
    parsed_deadline: str | None = None
    # Runtime validation ensures key exists
```

### 3. Integration Tests with State Flow
Unit tests don't catch state propagation issues in LangGraph. Need integration tests that run the full graph:
```python
@pytest.mark.integration
async def test_deadline_flows_through_graph():
    """Test that deadline flows from parse to format."""
    result = await process_voice_message(...)
    assert result.get("parsed_deadline") is not None
```

### 4. Production Log Analysis is Critical
The bug was invisible in unit tests but obvious in production logs:
- Unit tests mocked individual nodes (all passed)
- Only full graph execution revealed the issue
- Detailed logging enabled quick diagnosis

## Prevention

### 1. Add Type Checking to CI
```yaml
# .github/workflows/tests.yml
- name: Type check
  run: mypy src/ --strict
```

### 2. Add State Validation Tests
```python
def test_state_keys_match_typeddict():
    """Ensure all state keys exist in VoiceTaskState."""
    from src.ai.graphs.voice_task_creation import VoiceTaskState

    required_keys = VoiceTaskState.__annotations__.keys()

    # Check that code doesn't use undefined keys
    # (can be automated with AST parsing)
```

### 3. LangGraph State Audit
Periodically audit that all state keys in code match TypedDict:
```bash
# Find all state key references
grep -r "state\[\"" src/ai/graphs/
grep -r "state.get(\"" src/ai/graphs/

# Compare with TypedDict definition
```

## Related Documentation

- [Voice Task Creation Workflow](../05-ai-specifications/langgraph-flows.md)
- [Deadline Parsing Feature](DEADLINE_PARSING.md)
- [TypedDict Documentation](https://docs.python.org/3/library/typing.html#typing.TypedDict)
- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/state/)

---

**Status**: FIXED
**Commit**: 6adc1b3
**Production Verification**: ✅ CONFIRMED
**User Impact**: ✅ RESOLVED
