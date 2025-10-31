# How to Run TestGPT

## ✅ Fixed Issues

1. **Agent initialization error** - Removed invalid `show_tool_calls` parameter
2. **URL parsing** - Now handles Slack-formatted URLs correctly: `<http://example.com|example.com>`
3. **Signup flow** - Added support for registration/recruitment flows with phone number extraction
4. **Main entrypoint** - Created `main.py` as single entry point for all triggers
5. **Responsive viewport issues** - Fixed device emulation to use Playwright's proper device context API
6. **Agent autonomy** - Restored full autonomous control with high-level goals instead of prescriptive steps

---

## 🚀 Quick Start

### Run the Slack Bot

```bash
python main.py
```

**That's it!** The main.py is now the single entrypoint.

Or you can be explicit:
```bash
python main.py slack
```

---

## 📋 What main.py Does

1. **Verifies environment variables** (Slack tokens, Anthropic API key)
2. **Starts Slack bot listener**
3. **Connects to Playwright MCP** when first request comes in
4. **Initializes TestGPT engine** with MCP tools
5. **Handles requests** from Slack mentions
6. **Posts results** back to Slack

---

## 🧪 Test Without Slack (Demo Mode)

```bash
python test_testgpt.py
```

This runs mock tests without requiring Slack or Playwright.

---

## 💬 Example Slack Commands

### Test Landing Page
```
@TestGPT test https://example.com
```

### Responsive Cross-Browser Test
```
@TestGPT test pointblank.club responsive on safari and iphone
```

### Registration/Signup Test
```
@TestGPT test recruitment page on pointblank.club -> register for point blank recruitment using test credentials, use phone number 1111111111
```

**What happens:**
- Detects "recruitment" and "register" → signup flow
- Extracts phone number: 1111111111
- Creates test that:
  1. Navigates to pointblank.club
  2. Finds registration button
  3. Clicks it
  4. Fills phone number field
  5. Takes screenshot

### List Saved Scenarios
```
@TestGPT list scenarios
```

### Re-run a Test
```
@TestGPT re-run pointblank responsive test
```

---

## 🔍 What Gets Fixed

### Issue 1: Agent Initialization Error
**Before:**
```python
Agent(..., show_tool_calls=True)  # ❌ Not a valid parameter
```

**After:**
```python
Agent(..., markdown=False)  # ✅ Removed invalid parameter
```

### Issue 2: URL Parsing from Slack
**Before:**
```
Target URL: <http://pointblank.club|pointblank.club>  # ❌ Not parsed correctly
```

**After:**
```python
# Handle Slack-formatted URLs
slack_url_pattern = re.compile(r'<(https?://[^|>]+)(?:\|[^>]+)?>')
slack_urls = slack_url_pattern.findall(message)
# Result: "http://pointblank.club"  ✅
```

### Issue 3: Signup Flow Support
**Before:**
- Only had landing and pricing flows

**After:**
- Added `get_pointblank_signup_flow(phone_number)`
- Detects "register", "recruitment", "signup"
- Extracts phone number from message
- Creates multi-step signup test flow

### Issue 4: Responsive Viewport Emulation
**Problem:**
Even though Playwright set window size, websites didn't resize properly. The page would load at one dimension, then window would resize, but CSS media queries and responsive layout wouldn't trigger correctly - content would just "cut out."

**Root Cause:**
```javascript
// WRONG - This breaks responsive behavior:
await page.goto('https://example.com');
await page.setViewportSize({width: 390, height: 844}); // ❌ Too late!
// Page already loaded at different size, CSS already executed
```

**Solution:**
Use Playwright's device emulation API from the START, before page load:

```javascript
// CORRECT - For iPhone:
const device = playwright.devices['iPhone 13 Pro'];
const context = await browser.newContext({...device});
const page = await context.newPage();
await page.goto('https://example.com'); // ✅ Renders correctly from initial load
```

**What changed:**
- Agent instructions now include explicit device emulation examples
- For mobile: Use `playwright.devices['iPhone 13 Pro']` etc.
- For desktop: Set viewport in browser context before creating page
- Pages now render at target dimensions from initial load
- CSS media queries and responsive layouts work correctly

### Issue 5: Agent Lost Autonomy
**Problem:**
Agent was receiving prescriptive step-by-step instructions:
```
Step 1: Click selector X
Step 2: Fill field Y
Step 3: Wait for Z
```
This limited the agent's ability to adapt and make decisions.

**Solution:**
Now agent gets high-level goals and full control:
```
YOUR MISSION:
Execute this test flow:
1. Navigate to https://pointblank.club
2. Find and click: registration button
3. Fill form field 'phone' with value '1111111111'

AUTONOMOUS DECISION MAKING:
You have FULL CONTROL. Make your own decisions about:
- How to launch browser with proper device emulation
- Which selectors work best for finding elements
- When to wait for page load or elements
- How to verify expected outcomes
- How to adapt if elements aren't found immediately
```

**What changed:**
- Implemented `_execute_flow_autonomously()` method
- Agent receives high-level goals, not prescriptive steps
- Agent decides selectors, timing, and approach
- Agent can adapt if elements not found
- Agent opens browsers with proper device contexts

---

## 📁 File Changes

### New Files
- ✅ **main.py** - Single entrypoint for all triggers (Slack, GitHub, Web UI)
- ✅ **RUNNING.md** - This file

### Updated Files
- ✅ **test_executor.py** - Fixed Agent initialization
- ✅ **request_parser.py** - Added Slack URL parsing, improved flow detection
- ✅ **agent_instructions.py** - Added signup flow template
- ✅ **test_plan_builder.py** - Added signup flow support with phone number extraction

---

## 🎯 Expected Output

When you run `python main.py`:

```
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║  TestGPT - Multi-Environment QA Testing Platform                    ║
║                                                                      ║
║  Powered by: Agno + Playwright MCP + Claude Sonnet 4                ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

✅ All environment variables found

🚀 Starting in mode: slack

⚡️ Starting TestGPT Slack bot...
💡 Mention the bot in any channel to trigger QA testing
======================================================================
⚡️ Bolt app is running!
```

**When you mention the bot in Slack:**

```
📝 Received message from user U09QJMKUB7A: test recruitment page...

======================================================================
🔧 Initializing TestGPT Engine
======================================================================
📡 Connecting to Playwright MCP...
✅ Playwright MCP connected

🤖 Initializing TestGPT orchestration engine...
✅ TestGPT engine initialized

======================================================================
✅ TestGPT Ready for Multi-Environment Testing
======================================================================

🚀 TestGPT Processing Request
📋 Step 1: Parsing Slack request...
   Target URL: http://pointblank.club
   Flows: signup
   Viewports: desktop-standard
   Browsers: chromium-desktop, webkit-ios, webkit-desktop
   Networks: normal

🏗️  Step 2: Building test plan with matrix expansion...
   Matrix cells: 3

▶️  Step 4: Executing test matrix...
   🌐 Browser: Chrome (Desktop)
   📱 Viewport: desktop-standard (1920×1080)
   📡 Network: Good Broadband
      Step 1: navigate - https://pointblank.club
      ✅ Step 1 passed
      Step 2: wait_for_selector - button, a, [class*='register']...
      ✅ Step 2 passed
      ...

✅ TestGPT Processing Complete
```

---

## 🐛 Troubleshooting

### "Agent.__init__() got an unexpected keyword argument 'show_tool_calls'"
**Fixed!** Updated test_executor.py to remove this parameter.

### URL shows as "<http://example.com|example.com>"
**Fixed!** Updated request_parser.py to parse Slack URL format.

### Signup flow not detected
**Fixed!** Added "recruit" to flow patterns and created signup flow template.

### main.py not found
Make sure you're in the TestGPT directory:
```bash
cd /Users/akashsingh/Desktop/TestGPT
python main.py
```

---

## 🚀 Future Modes (Coming Soon)

### GitHub Webhooks
```bash
python main.py github
```

Will listen for GitHub PR comments and run tests automatically.

### Web UI
```bash
python main.py web
```

Will start web dashboard for triggering tests via UI.

---

## ✅ Summary

**Single command to run everything:**
```bash
python main.py
```

**What it does:**
1. Verifies environment
2. Starts Slack bot
3. Connects to Playwright MCP
4. Listens for @mentions
5. Runs multi-environment QA tests
6. Posts results to Slack

**All issues fixed!** ✅ Ready to test your signup flow.
