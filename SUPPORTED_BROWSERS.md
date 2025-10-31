# Supported Browsers

TestGPT supports the following browsers for automated testing:

## 🌐 Available Browsers

### Desktop Browsers

| Browser Name | Profile ID | Engine | Display Name |
|--------------|------------|--------|--------------|
| **Chrome** | `chromium-desktop` | chromium | Chrome (Desktop) |
| **Safari (macOS)** | `webkit-desktop` | webkit | Safari (macOS) |
| **Firefox** | `firefox-desktop` | firefox | Firefox (Desktop) |

### Mobile Browsers

| Browser Name | Profile ID | Engine | Display Name |
|--------------|------------|--------|--------------|
| **Safari (iOS)** | `webkit-ios` | webkit | Safari (iOS) |

---

## 📱 How Browser Selection Works

### 1. Automatic Selection (Claude API)

When you send a test request, Claude API automatically selects appropriate browsers based on:

- **Keywords in your message**:
  - "Safari" → `webkit-desktop` or `webkit-ios`
  - "Chrome" → `chromium-desktop`
  - "Firefox" → `firefox-desktop`
  - "iOS" or "iPhone" → `webkit-ios`
  - "cross-browser" → `chromium-desktop` + `webkit-desktop`

- **Target URL**:
  - **pointblank.club** → Always tests with `webkit-ios`, `webkit-desktop`, AND `chromium-desktop` (for Safari comparison)

- **Default**: If nothing specified → `chromium-desktop`

### 2. Example Requests

```
"test pointblank.club"
→ Browsers: Safari (iOS), Safari (macOS), Chrome (Desktop)

"test mysite.com on Safari"
→ Browser: Safari (macOS)

"test mysite.com on iPhone"
→ Browser: Safari (iOS)

"cross-browser test"
→ Browsers: Chrome (Desktop), Safari (macOS)

"test on Chrome"
→ Browser: Chrome (Desktop)
```

---

## 🔧 Browser Installation

All browsers are installed via Playwright:

```bash
npx playwright install
```

This installs:
- ✅ Chromium (Chrome) - ~129 MB
- ✅ WebKit (Safari) - ~70 MB
- ✅ Firefox - ~89 MB

**Note**: Browsers are installed once and reused across all tests. The agent should NOT call `browser_install` during test execution.

---

## ⚙️ Configuration

Browser profiles are defined in:
- **`config.py`** - Python configuration (lines 143-175)
- **`config.json`** - JSON configuration for MCP launch args

To add a new browser, add it to both files.

---

## 🚀 Usage in Code

```python
from config import BROWSER_PROFILES, get_browser

# Get browser profile
chrome = get_browser("chromium-desktop")
safari_ios = get_browser("webkit-ios")

# Profile details
print(chrome.display_name)  # "Chrome (Desktop)"
print(chrome.engine)        # "chromium"
print(safari_ios.platform)  # "mobile"
```

---

## 📊 Browser Coverage

| Platform | Browsers Available |
|----------|-------------------|
| Desktop | Chrome, Safari, Firefox |
| Mobile (iOS) | Safari |
| Mobile (Android) | Currently uses Chromium with Android viewports |

**Note**: For Android testing, TestGPT uses Chromium browser with Android device emulation (viewport + user agent).
