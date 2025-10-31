# Viewport Testing Issue & Solution

## 🔴 Critical Issue Discovered

The Playwright MCP server's `browser_resize` tool **does not work for responsive testing**.

### Why It's Broken:

Looking at the MCP tool execution logs:
```js
DEBUG ### Ran Playwright code
```js
await page.setViewportSize({ width: 1920, height: 1080 });
```
```

The `browser_resize` tool uses `page.setViewportSize()` which resizes the viewport **AFTER** the page object already exists. This is the exact problem we were trying to avoid!

### What Happens:

1. ✅ Agent navigates to `about:blank`
2. ✅ Agent calls `browser_resize(width=1920, height=1080)`
3. ❌ MCP server executes: `await page.setViewportSize({ width: 1920, height: 1080 });`
4. ❌ This resizes EXISTING page, doesn't create new context
5. ✅ Agent navigates to target URL
6. ❌ Page loads with wrong CSS media queries already fired
7. ❌ Content "cuts out" and doesn't re-flow properly

### Evidence from Your Screenshot:

The screenshot you shared shows pointblank.club loaded with:
- Viewport appears resized
- Content is cut off at edges
- Layout doesn't respond properly to viewport dimensions
- This confirms `page.setViewportSize()` doesn't trigger responsive re-layout

## 💡 The Proper Solution

### Option 1: Launch MCP Server with Correct Viewport (RECOMMENDED)

Launch the Playwright MCP server with the `--viewport-size` or `--device` argument:

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--viewport-size=390x844"  // For iPhone 13 Pro
      ]
    }
  }
}
```

Or for device emulation:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--device=iPhone 13 Pro"
      ]
    }
  }
}
```

**Pros:**
- ✅ Page renders correctly from first load
- ✅ CSS media queries fire correctly
- ✅ JavaScript viewport detection works
- ✅ True responsive behavior

**Cons:**
- ❌ Need to restart MCP server to test different viewports
- ❌ Can't test multiple viewports in single test run
- ❌ Requires reconfiguring MCP server for each viewport

### Option 2: Launch Multiple MCP Servers (BEST for Multi-Viewport)

For true multi-environment testing, launch separate MCP server instances for each viewport:

```json
{
  "mcpServers": {
    "playwright-iphone": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--device=iPhone 13 Pro",
        "--port=8901"
      ]
    },
    "playwright-ipad": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--device=iPad Air",
        "--port=8902"
      ]
    },
    "playwright-desktop": {
      "command": "npx",
      "args": [
        "@playwright/mcp@latest",
        "--viewport-size=1920x1080",
        "--port=8903"
      ]
    }
  }
}
```

Then in TestGPT, connect to the appropriate MCP server based on viewport being tested.

**Pros:**
- ✅ True multi-viewport testing
- ✅ Each viewport has correct device emulation
- ✅ No browser_resize needed
- ✅ Proper responsive behavior

**Cons:**
- ❌ More complex setup
- ❌ Multiple MCP processes running
- ❌ Requires code changes to switch MCP connections

### Option 3: Use Playwright's Browser Context API Directly

If Playwright MCP adds a tool to create new browser contexts with viewport settings, we could use:

```javascript
// Hypothetical future tool
browser_create_context({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3.0,
  isMobile: true,
  hasTouch: true
})
```

Then navigate within that context. This would work correctly.

**Status:** Not currently available in Playwright MCP

## 🛠️ Current Workaround (Temporary)

For now, TestGPT is configured to:

1. ⚠️  **Skip `browser_resize` entirely** - it's broken
2. ✅ Navigate directly to target URL
3. ✅ Test at whatever viewport the browser launched with
4. 📝 Log clear warnings that viewport testing is limited

The agent now receives these instructions:
```
CRITICAL VIEWPORT ISSUE - browser_resize IS BROKEN:
⚠️  The browser_resize tool is BROKEN - it uses page.setViewportSize()
⚠️  DO NOT use browser_resize - it will cause content to "cut out"

WHAT TO DO INSTEAD:
Navigate directly to target URL and test at default viewport.
We'll fix proper multi-viewport testing in future iteration.
```

## 📋 Action Items

### Immediate (For You):
1. **Try Option 1**: Add `--viewport-size=1920x1080` or `--device=iPhone 13 Pro` to your MCP server launch config
2. **Test**: Run a test and verify page renders correctly without "cutting out"
3. **Share results**: Let me know if this fixes the responsive issue

### Future (TestGPT Enhancement):
1. **Implement Option 2**: Support multiple MCP server connections
2. **Viewport-specific MCP connections**: Map each viewport profile to dedicated MCP server
3. **Dynamic MCP launching**: Programmatically launch MCP servers with correct viewport args
4. **Connection pooling**: Manage multiple MCP connections efficiently

## 🔗 References

- [Playwright MCP Args Documentation](https://github.com/microsoft/playwright-mcp#configuration)
- [Playwright Device Emulation](https://playwright.dev/docs/emulation)
- [Why setViewportSize Doesn't Work](https://github.com/microsoft/playwright/issues/1086#issuecomment-592287228)

## 💾 Log Files

All debug logs are now saved to:
- `logs/testgpt-debug-YYYYMMDD-HHMMSS.log` (timestamped)
- `logs/latest.log` (symlink to most recent)

These logs include:
- Full instructions sent to agent
- Complete agent responses
- All tool calls and results
- Detailed error traces

## ✅ Next Steps

1. Update your MCP server configuration with viewport args
2. Run a test
3. Check `logs/latest.log` for full execution details
4. Share the log file if issues persist

The viewport issue is now understood and documented. Proper fix requires MCP server configuration changes, not code changes in the agent.
