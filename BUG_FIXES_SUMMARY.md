# Bug Fixes Summary - TestGPT

## 🆕 Latest Fixes (2025-10-31 - Session 2)

### **Issue 5: Subdomain URLs Being Stripped (careers.pointblank.club → pointblank.club)**

**Problem:**
- User requests "Test careers.pointblank.club"
- Agent navigates to "pointblank.club" instead
- Subdomain is lost during URL extraction

**Root Cause:**
1. URL extraction regex didn't properly handle multi-level domains
2. Fallback logic defaulted to "pointblank.club" if message contained "pointblank"
3. For "careers.pointblank.club", if extraction failed, fallback triggered and stripped subdomain

**Fix:** `request_parser.py` (lines 148-177)
- Improved URL extraction regex to explicitly match subdomains: `r'\b((?:[\w-]+\.)+[\w-]+\.(?:com|org|net|io|club|dev|ai|tech|app|co))\b'`
- Removed problematic pointblank.club fallback that triggered on any mention of "pointblank"
- Added logging to debug URL extraction
- Now correctly extracts: careers.pointblank.club, api.github.com, subdomain.domain.tld

---

### **Issue 6: Bot Processing Old Messages Without Being Tagged**

**Problem:**
- Bot processes messages from 5+ minutes ago
- Bot sometimes processes messages where it wasn't even mentioned
- On restart, bot may replay old Slack events

**Root Cause:**
- No timestamp-based filtering
- When bot restarts, Slack may resend recent events
- Event deduplication alone wasn't enough

**Fix:** `main.py` (lines 134-144)
```python
# Get event timestamp
event_ts = float(event.get("event_ts") or event.get("ts"))
current_time = time.time()

# Ignore events older than 5 minutes (300 seconds)
age_seconds = current_time - event_ts
if age_seconds > 300:
    print(f"⚠️  Skipping old event (age: {age_seconds:.1f}s)")
    return
```

---

### **Issue 7: Agent Not Following Custom User Instructions**

**Problem:**
- User asks: "Test github.com, are you able to view the repositories of SkySingh04?"
- Agent only performs generic landing page test
- Agent doesn't understand custom instructions like "view repositories" or "search for user"

**Root Cause:**
- Agent only received pre-defined test flows (navigate, click, verify)
- User's raw message was not passed to the agent
- Agent had no context about what the user actually wanted to test

**Fix:** Multiple files modified
- `models.py` (line 181): Added `user_request: str = ""` to TestPlan
- `test_plan_builder.py` (line 83): Pass `user_request=parsed_request.raw_message` when building plan
- `test_executor.py` (lines 182, 116, 217, 256, 283-296): Thread user_request through execution pipeline
- `test_executor.py` (lines 283-296): Include user request in agent instructions

**New Agent Instruction Format:**
```
YOUR MISSION:
USER REQUEST:
"Test github.com, are you able to view the repositories of SkySingh04?"

YOUR GOAL:
Interpret the user's request above and execute it autonomously on the target website.
Make decisions about how to accomplish the user's goal, including:
- Which pages to navigate to
- Which elements to interact with
- What information to gather or verify
- How to report your findings
```

---

## 🐛 Previous Issues Fixed (Session 1)

### **Issue 1: Test Marked as FAILED Despite Agent Reporting SUCCESS**

**Problem:**
- Agent completes all test steps successfully and reports: `Test Outcome: PASSED`
- Executor marks the test as: `✅ Autonomous execution completed: FAILED`
- Slack shows test as FAILED with vague error message

**Root Cause:**
The parser was looking for `"test status:"` but the agent uses different formats:
- "Test Outcome: PASSED"
- "Test Status: PASSED"
- "Final Status: PASSED"

**Fix:** `test_executor.py` (lines 485-510)
```python
# Now checks multiple status indicator formats
status_indicators = [
    "test status:",
    "test outcome:",
    "final status:",
    "overall status:"
]

for indicator in status_indicators:
    if indicator in output_lower:
        status_section = output_lower.split(indicator)[-1][:100]
        if "passed" in status_section:
            overall_passed = True
```

---

### **Issue 2: Slack Bot Processing Same Message Multiple Times**

**Problem:**
- User sends one message
- Bot shows 2+ acknowledgments
- Same test runs multiple times
- Slack may retry events if no acknowledgment received quickly

**Root Cause:**
No event deduplication - Slack's retry mechanism causes duplicate event processing.

**Fix:** `main.py` (lines 126-141)
```python
# Track processed events to prevent duplicates
processed_events = set()

@app.event("app_mention")
def handle_mention(event, say):
    # Deduplicate events (Slack may retry)
    event_id = event.get("event_ts") or event.get("ts")
    if event_id in processed_events:
        print(f"⚠️  Skipping duplicate event: {event_id}")
        return

    processed_events.add(event_id)
    # Keep only last 1000 event IDs to prevent memory leak
    if len(processed_events) > 1000:
        processed_events.clear()
```

---

### **Issue 3: Hardcoded pointblank.club URL in Example Instructions**

**Problem:**
- Test instructions contain example: `"url": "https://pointblank.club"`
- Confusing when testing different URLs
- Could mislead the agent

**Fix:** `test_executor.py` (line 416)
```python
# Before:
"url": "https://pointblank.club"  // Replace with actual target URL

# After:
"url": "YOUR_TARGET_URL_HERE"
```

---

### **Issue 4: Wrong URL Being Tested (careers.pointblank.club → pointblank.club)**

**Problem:**
- User requests: "Test Careers.pointblank.club"
- Agent navigates to: "pointblank.club" instead

**Root Cause Analysis:**

This is likely happening in the URL extraction logic. Let me check:

**Potential Issues:**
1. **Case sensitivity in URL parsing** - "Careers.pointblank.club" vs "careers.pointblank.club"
2. **URL normalization** - Parser might be stripping subdomains
3. **Default URL fallback** - Parser might default to pointblank.club for pointblank-related requests

**Where to Check:**
- `request_parser.py`: `_extract_urls()` method
- Check if subdomain is being stripped during parsing

**Recommended Fix:**
Review URL extraction regex in `request_parser.py` to ensure subdomains are preserved.

---

## 📊 Summary of Changes

### Session 2 Changes:
| File | Lines Changed | Issue Fixed |
|------|---------------|-------------|
| `request_parser.py` | 148-177 | Improved subdomain URL extraction |
| `request_parser.py` | 76-81 | Removed problematic pointblank fallback |
| `main.py` | 134-144 | Event timestamp filtering (ignore old events) |
| `main.py` | 67-87 | Asyncio exception handler (suppress MCP cleanup warnings) |
| `models.py` | 181 | Added user_request field to TestPlan |
| `test_plan_builder.py` | 83 | Pass user request when building plan |
| `test_executor.py` | 182, 116, 217, 256, 283-296 | Thread user request to agent instructions |
| `testgpt_engine.py` | 163-177 | Wrapped cleanup in try/except to suppress errors |

### Session 1 Changes:
| File | Lines Changed | Issue Fixed |
|------|---------------|-------------|
| `test_executor.py` | 485-510 | Test status parsing (multiple formats) |
| `test_executor.py` | 416 | Removed hardcoded example URL |
| `main.py` | 126-141 | Event deduplication |

---

## 🎯 Testing Recommendations

### Test 1: Verify Status Detection Works
```
@TestGPT test github.com
```
**Expected:**
- Agent completes successfully
- Test marked as PASSED (not FAILED)
- Slack shows green checkmark

### Test 2: Verify No Duplicate Processing
```
@TestGPT test pointblank.club
```
**Expected:**
- Only ONE acknowledgment message
- Only ONE test execution
- No duplicate Slack posts

### Test 3: Verify Subdomain URLs Work ✨ NEW
```
@TestGPT test careers.pointblank.club
```
**Expected:**
- URL extraction logs show: "📎 Extracted domain without protocol: careers.pointblank.club"
- Agent navigates to https://careers.pointblank.club (not pointblank.club)
- Subdomain is fully preserved

### Test 4: Verify Custom User Instructions Work ✨ NEW
```
@TestGPT Test github.com, are you able to view the repositories of SkySingh04?
```
**Expected:**
- Agent receives the custom request in instructions
- Agent attempts to search for user "SkySingh04"
- Agent navigates to profile and reports what repositories it finds
- NOT just a generic landing page test

### Test 5: Verify Old Events Are Ignored ✨ NEW
```
1. Start the bot
2. Wait 10 minutes
3. @TestGPT test github.com
```
**Expected:**
- Event is processed normally (age < 5 minutes)

Then:
```
1. Stop the bot (Ctrl+C)
2. Send message: @TestGPT test pointblank.club
3. Wait 6 minutes
4. Restart the bot
```
**Expected:**
- Logs show: "⚠️ Skipping old event (age: 360.0s)"
- Message is NOT processed

---

## 🐛 Known Limitations

### **1. Vague Error Messages in Slack**
**Status:** Improved but could be better
**Impact:** When tests fail, Slack shows truncated error messages
**Recommendation:** Format failure summaries better in `result_formatter.py`

### **2. MCP Cleanup Warnings**
**Status:** ✅ FULLY FIXED (Session 2)
**Impact:** Cosmetic - showed warnings but didn't affect functionality
**Fix:**
- `testgpt_engine.py` (lines 163-177): Wrapped cleanup in try/except to suppress RuntimeError
- `main.py` (lines 67-87): Added asyncio exception handler to suppress async generator cleanup warnings
**Current Behavior:** Clean shutdown with NO error messages

---

## 📝 Future Improvements

1. **Better Error Reporting:**
   - Show specific step failures in Slack
   - Include clickable links to full logs
   - Add screenshot links directly in failure messages

2. **URL Validation:**
   - Validate URLs before testing
   - Warn user if URL looks malformed
   - Suggest corrections for common typos

3. **Event Queue:**
   - Process Slack messages in a queue
   - Handle multiple concurrent requests gracefully
   - Show "Test N of M in queue" status

4. **Agent Response Parsing:**
   - Use structured JSON output from agent
   - Enforce consistent status reporting format
   - Validate agent responses before parsing

---

## ✅ Quick Reference

### Check if Fixes Applied:
```bash
# Should show these files as modified:
git status

# Should compile without errors:
python -m py_compile main.py test_executor.py

# Should show event deduplication:
grep "processed_events" main.py

# Should show multiple status indicators:
grep "test outcome:" test_executor.py
```

### Verify Runtime:
```bash
python main.py

# In Slack:
@TestGPT test github.com

# Check logs:
cat logs/latest.log | grep "Test Outcome:"
cat logs/latest.log | grep "✅ Autonomous execution completed"
```

---

**Last Updated:** 2025-10-31
**Version:** Session 2 - Subdomain URLs, Custom Instructions, Event Filtering
