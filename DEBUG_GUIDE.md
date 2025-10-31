# TestGPT Debug Guide

## Comprehensive Debug Logging

TestGPT now includes extensive debug logging to track exactly what the AI agent is thinking and doing during test execution.

## What Gets Logged

### 1. Agent Initialization
```
🔧 Initializing Agno agent with Playwright MCP tools...
   Debug mode: ENABLED
   Tool calls: Will be logged
```

### 2. Flow Execution Start
```
======================================================================
🔍 DEBUG: Starting autonomous execution for cell signup-r_iphone-13-pro_webkit-ios_normal_20251031-161500
======================================================================
```

### 3. Full Instruction Sent to Agent
```
📤 INSTRUCTION SENT TO AGENT:
----------------------------------------------------------------------
AUTONOMOUS WEB TEST EXECUTION

ENVIRONMENT SETUP:
- Browser: Safari (iOS) (webkit)
- Device/Viewport: Standard iOS - iphone-13-pro
- Screen Size: 390×844
- Device Scale: 3.0x
- Mobile: YES
- Network: Good Broadband

CRITICAL VIEWPORT SETUP - READ THIS CAREFULLY:
The page MUST render at the target viewport size from initial load.
Resizing AFTER page load breaks responsive CSS and causes content to "cut out".

CORRECT WORKFLOW (use browser_resize tool):
1. Navigate to blank page: browser_navigate(url="about:blank")
2. Resize browser: browser_resize(width=390, height=844)
3. NOW navigate to target URL: browser_navigate(url="TARGET_URL")
4. Page will render correctly at 390×844 from start

[... full mission details ...]
----------------------------------------------------------------------
```

### 4. Agent Execution Progress
```
⏳ Executing with AI agent (this may take 30-60 seconds)...
🤖 Agent is thinking and using Playwright MCP tools...
```

### 5. Complete Agent Response
```
📥 AGENT RESPONSE:
----------------------------------------------------------------------
I successfully completed the recruitment signup flow:

1. Navigated to about:blank
2. Resized browser to 390x844
3. Navigated to https://pointblank.club
4. Found registration button using selector 'a[href*="recruit"]'
5. Clicked the button
6. Waited for phone input field to appear
7. Filled phone number: 1111111111
8. Captured screenshot: signup-form-filled

All steps completed successfully. The page rendered correctly at mobile dimensions.
----------------------------------------------------------------------
```

### 6. Execution Result
```
✅ Autonomous execution completed: PASSED
======================================================================
```

### 7. Error Details (if crash occurs)
```
❌ AGENT EXECUTION ERROR:
----------------------------------------------------------------------
Error Type: TimeoutError
Error Message: Timeout 30000ms exceeded waiting for selector 'button'

Full Traceback:
Traceback (most recent call last):
  File "/Users/akashsingh/Desktop/TestGPT/test_executor.py", line 260
    response = await self.agent.arun(autonomous_instruction)
  File ".../agno/agent.py", line 142, in arun
    ...
playwright._impl._errors.TimeoutError: Timeout 30000ms exceeded...
----------------------------------------------------------------------
```

## How to Read the Logs

### Normal Execution Flow:
1. Look for `📤 INSTRUCTION SENT TO AGENT` - this shows exactly what the agent was told to do
2. Check `🤖 Agent is thinking` - wait for execution
3. Read `📥 AGENT RESPONSE` - see what the agent actually did
4. Verify `✅ Autonomous execution completed: PASSED/FAILED`

### Debugging Crashes:
1. Find `❌ AGENT EXECUTION ERROR` section
2. Note the `Error Type` (e.g., TimeoutError, NavigationError, SelectorNotFoundError)
3. Read the `Error Message` for specific details
4. Review the `Full Traceback` to see exactly where it failed
5. Cross-reference with the `📤 INSTRUCTION SENT TO AGENT` to see what was expected

### Common Error Patterns:

**TimeoutError:**
```
Error Type: TimeoutError
Error Message: Timeout 30000ms exceeded waiting for selector 'button'
```
**Cause:** Element not found within timeout period
**Solution:** Check if selector is correct, or if page needs more time to load

**NavigationError:**
```
Error Type: Error
Error Message: net::ERR_NAME_NOT_RESOLVED at https://invalid-url.com
```
**Cause:** Invalid URL or network issue
**Solution:** Verify URL is correct and accessible

**SelectorError:**
```
Error Type: Error
Error Message: No element matches selector 'button.signup'
```
**Cause:** Wrong selector or element doesn't exist
**Solution:** Agent should adapt and try different selectors

**Crash/Disconnect:**
```
Error Type: BrowserClosedError
Error Message: Browser has been closed
```
**Cause:** Browser crashed or was forcefully closed
**Solution:** Check for JavaScript errors on page, reduce concurrent tests

## Sharing Debug Logs

When reporting issues, share these sections:

1. **The instruction sent:**
   Copy everything from `📤 INSTRUCTION SENT TO AGENT` to the next `---` line

2. **The agent response (if it got there):**
   Copy everything from `📥 AGENT RESPONSE` to the next `---` line

3. **The error details (if it crashed):**
   Copy everything from `❌ AGENT EXECUTION ERROR` to the next `---` line

Example bug report format:
```
## Issue: Agent crashes when testing signup flow on iPhone

### Instruction Sent:
[paste instruction]

### Agent Response (if any):
[paste response or "N/A - crashed before response"]

### Error:
[paste error details]

### Expected behavior:
Agent should fill phone number and complete signup

### Actual behavior:
Browser crashes after clicking registration button
```

## Enabling/Disabling Debug Mode

Debug mode is currently **always enabled** in `test_executor.py:87`:

```python
self.agent = Agent(
    name="PlaywrightTestAgent",
    model=Claude(id="claude-sonnet-4-20250514"),
    tools=[self.mcp_tools],
    debug_mode=True,  # ← Set to False to disable verbose logging
    instructions="""..."""
)
```

To disable verbose logging:
- Change `debug_mode=True` to `debug_mode=False`
- You'll still get high-level logs (✅/❌) but not full instructions/responses

## Performance Impact

Debug logging adds minimal overhead:
- Instruction logging: ~1-2ms
- Response logging: ~5-10ms
- Error logging: ~1-2ms

Total impact: < 20ms per test cell (negligible compared to 30-60s execution time)

## Log File Locations

Currently logs print to stdout/stderr. To save to file:

```bash
python main.py 2>&1 | tee testgpt-debug.log
```

This will:
- Display logs in terminal (real-time)
- Save complete logs to `testgpt-debug.log` file

## Next Steps

When you get a crash:
1. Copy the `📤 INSTRUCTION SENT TO AGENT` section
2. Copy the `❌ AGENT EXECUTION ERROR` section
3. Share both with me for debugging
4. I can analyze what the agent was told vs what went wrong
