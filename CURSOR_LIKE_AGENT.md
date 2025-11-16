# Cursor-Like Agent Capabilities

## Overview

This update adds **Cursor-like iterative tool execution** to Cite-Agent, enabling:

- **Natural directory navigation**: `cd ~/Downloads` → `ls` → `find *.csv`
- **Persistent working directory**: cd commands are remembered between tool calls
- **No special syntax**: No more "Run:" prefix or absolute path requirements
- **Iterative multi-step execution**: LLM controls tool invocation, sees results, decides next action

## How It Works

### Architecture Comparison

**Before (Traditional Mode):**
```
User: "cd ~/Downloads and list CSV files"
  ↓
Pre-planner LLM decides ONE command upfront
  ↓
Executes command
  ↓
Main LLM sees results, generates response
```

**After (Function Calling Mode):**
```
User: "cd ~/Downloads and list CSV files"
  ↓
LLM: "I'll call execute_shell_command(cd ~/Downloads)"
  ↓
Result: "Changed directory to /home/user/Downloads"
  ↓
LLM: "Now I'll call execute_shell_command(find *.csv)"
  ↓
Result: "file1.csv\nfile2.csv\n..."
  ↓
LLM: "Here are the CSV files in ~/Downloads: ..."
```

## Activation

Enable function calling mode via environment variable:

```bash
# Enable Cursor-like mode
export NOCTURNAL_FUNCTION_CALLING=1

# Optional: Enable debug output
export NOCTURNAL_DEBUG=1

# Run your agent
python3 -c "
import asyncio
from cite_agent import EnhancedNocturnalAgent, ChatRequest

async def main():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Natural navigation - no special syntax!
    response = await agent.process_request(
        ChatRequest(question='cd ~/Downloads', user_id='me', conversation_id='test')
    )
    print(response.response)

    # ls will now list Downloads directory
    response = await agent.process_request(
        ChatRequest(question='ls', user_id='me', conversation_id='test')
    )
    print(response.response)

    await agent.close()

asyncio.run(main())
"
```

## What Changed

### 1. **Function Calling Mode Enabled** (`enhanced_ai_agent.py:4598`)
- Environment variable `NOCTURNAL_FUNCTION_CALLING=1` routes to iterative tool execution
- Default OFF for backward compatibility

### 2. **Persistent Working Directory** (`tool_executor.py:326-434`)
- `cd` commands update `agent.file_context['current_cwd']`
- All subsequent commands execute in that directory
- Directory persists across tool calls

### 3. **Rich System Prompt** (`enhanced_ai_agent.py:4374-4391`)
- Includes current working directory
- Teaches LLM to use tools naturally
- No special syntax requirements

### 4. **Directory-Aware Tools** (`tool_executor.py`)
- `list_directory`: Uses current cwd for relative paths
- `read_file`: Resolves relative paths from cwd
- `write_file`: Creates files relative to cwd
- `execute_shell_command`: Prepends `cd $cwd &&` to commands

## Testing

Run the test script:

```bash
# Make sure API keys are configured
export CEREBRAS_API_KEY_1="your_key"
# ... or whatever provider you use

# Run tests
NOCTURNAL_FUNCTION_CALLING=1 python3 test_cursor_like_agent.py
```

### Expected Test Flow

1. **"where am I?"** → Shows current directory
2. **"cd ~/Downloads"** → Changes to Downloads, persists
3. **"ls"** → Lists Downloads directory (not project root)
4. **"find *.csv"** → Finds CSV files in Downloads
5. **"cd ~"** → Returns home
6. **"pwd"** → Confirms we're home

### Critical Success Criteria

- ✅ Directory navigation persists (cd → ls works in new directory)
- ✅ Relative paths work (no absolute paths needed)
- ✅ No "Run:" prefix required
- ✅ Multi-step operations work (cd then ls)

## Configuration

### Environment Variables

```bash
# Enable function calling mode (default: off)
NOCTURNAL_FUNCTION_CALLING=1

# Enable debug output (default: off)
NOCTURNAL_DEBUG=1

# API configuration (existing)
NOCTURNAL_ACCOUNT_EMAIL=...
NOCTURNAL_ACCOUNT_PASSWORD=...
```

### Backward Compatibility

- Default: Traditional mode (no changes to existing behavior)
- Function calling mode: Opt-in via environment variable
- All existing tests and workflows continue to work

## Benefits Over ChatGPT/Traditional Mode

1. **Iterative Tool Execution**: LLM sees tool results, decides next action
2. **Persistent State**: Directory changes remembered
3. **Natural Language**: "cd ~/Downloads" instead of "Run: cd ~/Downloads"
4. **Multi-Step Workflows**: LLM chains commands based on results
5. **Context-Aware**: System prompt includes current directory

## Known Limitations

1. **API Compatibility**: Requires OpenAI-compatible function calling API
2. **Token Usage**: Multi-step may use more tokens (multiple LLM calls)
3. **Container Environments**: May have TLS/proxy issues (why it's opt-in)

## Files Changed

- `cite_agent/enhanced_ai_agent.py`: Enable FC mode, add system prompt with cwd
- `cite_agent/tool_executor.py`: Persistent cwd tracking for all file operations
- `cite_agent/function_calling.py`: Accept system_prompt parameter
- `test_cursor_like_agent.py`: Test script for Cursor-like workflow

## Next Steps

1. Test with your actual API keys and local files
2. Monitor token usage vs traditional mode
3. Consider expanding to more tools (git, python execution, etc.)
4. Add more sophisticated multi-step planning if needed
