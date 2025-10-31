# TestGPT Quick Reference

Quick reference for TestGPT features, configuration, and usage.

---

## 🌐 Supported Browsers

| Browser | Profile ID | Usage |
|---------|------------|-------|
| **Chrome (Desktop)** | `chromium-desktop` | Default browser |
| **Safari (macOS)** | `webkit-desktop` | Desktop Safari testing |
| **Safari (iOS)** | `webkit-ios` | Mobile iOS testing |
| **Firefox (Desktop)** | `firefox-desktop` | Firefox testing |

**Auto-selection rules:**
- `pointblank.club` → Always tests Safari iOS, Safari macOS, Chrome
- "Safari" in message → Safari (macOS)
- "iPhone" or "iOS" → Safari (iOS)
- "Chrome" → Chrome
- "cross-browser" → Chrome + Safari (macOS)
- Default → Chrome

**📄 Full docs:** [SUPPORTED_BROWSERS.md](./SUPPORTED_BROWSERS.md)

---

## 📱 Supported Viewports

### Mobile
- **iPhone SE** (375×667) - Smallest iOS
- **iPhone 13 Pro** (390×844) - Standard iOS
- **iPhone 13 Pro Landscape** (844×390)
- **Android Small** (360×640) - Budget Android
- **Android Medium** (412×915) - Standard Android

### Tablet
- **iPad Air** (820×1180) - Portrait
- **iPad Air Landscape** (1180×820)

### Desktop
- **Desktop Standard** (1920×1080) - Most common
- **Desktop Ultrawide** (2560×1440) - Large displays
- **Desktop Small** (1366×768) - Laptops

**Auto-selection rules:**
- "iPhone" → iPhone 13 Pro
- "iPad" → iPad Air
- "Android" → Android Medium
- "desktop" → Desktop Standard
- "responsive" → iPhone 13 Pro + iPad Air + Desktop Standard

---

## 📡 Network Conditions

| Profile | Description | Use Case |
|---------|-------------|----------|
| **normal** | Good broadband (50ms latency) | Default baseline |
| **slow-3g** | Slow mobile (400ms, 400kbps) | Slow connections |
| **flaky-edge** | Unstable connection (2% packet loss) | Edge cases |

**Auto-selection:**
- Always includes `normal`
- "slow" or "3G" → adds `slow-3g`
- "flaky" or "unstable" → adds `flaky-edge`

---

## 🚀 Usage Examples

### Slack Commands

```
@TestGPT test pointblank.club
→ Tests: Safari iOS, Safari macOS, Chrome on desktop

@TestGPT test mysite.com on iPhone
→ Tests: Safari iOS on iPhone 13 Pro

@TestGPT test mysite.com responsive
→ Tests: iPhone, iPad, Desktop on Chrome

@TestGPT test checkout flow on mobile with slow network
→ Tests: iPhone with slow-3g network

@TestGPT cross-browser test
→ Tests: Chrome + Safari on desktop
```

---

## 🔧 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Install Playwright browsers (one-time)
npx playwright install

# 3. Set environment variables
export ANTHROPIC_API_KEY="sk-ant-..."
export SLACK_BOT_TOKEN="xoxb-..."
export SLACK_APP_TOKEN="xapp-..."

# 4. Run TestGPT
python main.py
```

---

## 📊 How It Works

```
Slack Message
    ↓
Claude API Parser (extracts viewports/browsers/networks)
    ↓
Test Plan Builder (creates matrix of environment combinations)
    ↓
Dynamic MCP Manager (launches separate MCP server for each combo)
    ↓
Test Executor (runs autonomous AI agent for each environment)
    ↓
Results Aggregator (collects pass/fail for all environments)
    ↓
Slack Summary (formatted results with screenshots)
```

---

## 🐛 Debugging

**View logs:**
```bash
cat logs/latest.log
```

**Check MCP servers:**
```bash
ps aux | grep playwright
```

**Test single cell:**
```python
from testgpt_engine import TestGPTEngine

engine = TestGPTEngine()
result = await engine.process_test_request(
    "test pointblank.club on iPhone"
)
```

---

## 📁 Key Files

| File | Purpose |
|------|---------|
| `config.py` | Viewport/browser/network profiles |
| `config.json` | MCP launch arguments |
| `viewport_parser_claude.py` | Claude API parser |
| `mcp_manager.py` | Dynamic MCP server management |
| `test_executor.py` | Test execution engine |
| `testgpt_engine.py` | Main orchestration |
| `main.py` | Entry point (Slack bot) |

---

## 🔗 Documentation Links

- **[SUPPORTED_BROWSERS.md](./SUPPORTED_BROWSERS.md)** - Full browser documentation
- **[DYNAMIC_MULTI_VIEWPORT.md](./DYNAMIC_MULTI_VIEWPORT.md)** - Multi-viewport architecture
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Complete implementation guide
- **[DEBUG_GUIDE.md](./DEBUG_GUIDE.md)** - Debugging and troubleshooting
- **[README.md](./README.md)** - Project overview

---

## ⚙️ Configuration

**Add new viewport:**
Edit `config.py` and `config.json`:
```python
# config.py
"my-device": ViewportProfile(
    name="my-device",
    width=1024,
    height=768,
    display_name="My Custom Device",
    playwright_device="iPad",  # or None
    ...
)
```

```json
// config.json
"my-device": {
  "name": "my-device",
  "mcp_launch_args": ["--device=iPad"],
  ...
}
```

**Add new browser:**
Add to `BROWSER_PROFILES` in `config.py` and update `config.json`.

---

## 🎯 Pro Tips

1. **Always test pointblank.club with Safari** - Auto-enabled for this site
2. **Use "responsive" keyword** - Tests 3 viewports automatically
3. **Check logs for details** - `logs/latest.log` shows full execution
4. **Browsers are pre-installed** - Agent shouldn't call browser_install
5. **Each test gets clean state** - No context carryover between tests

---

**Last updated:** 2025-10-31
**Version:** 1.0 (Dynamic Multi-Viewport)
