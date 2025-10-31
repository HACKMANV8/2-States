# Device Emulation Best Practices for TestGPT

## The Problem: Viewport Resizing Doesn't Work

When testing responsive websites, you might think this works:

```javascript
// ❌ WRONG - Breaks responsive behavior
const page = await browser.newPage();
await page.goto('https://example.com');  // Page loads at default size (1280x720)
await page.setViewportSize({width: 390, height: 844});  // Resize after load
// Result: Content "cuts out" - media queries already fired, layout already set
```

**Why this fails:**
1. Page loads at default viewport (e.g., 1280×720)
2. CSS media queries execute for desktop size
3. JavaScript viewport-detection code runs for desktop
4. Layout is set for desktop
5. Window is resized, but content doesn't re-flow properly
6. Content appears "cut out" or misaligned

## The Solution: Device Emulation from START

### For Standard Mobile Devices (iPhone, iPad)

Use Playwright's built-in device descriptors:

```javascript
// ✅ CORRECT - For iPhone 13 Pro
const device = playwright.devices['iPhone 13 Pro'];
const context = await browser.newContext({
  ...device,
  // Optional: Add network throttling
  // offline: false,
  // downlink: 1.5,  // Mbps
  // latency: 40     // ms
});
const page = await context.newPage();
await page.goto('https://example.com');
// Result: Page renders correctly as iPhone from initial load
```

```javascript
// ✅ CORRECT - For iPad Air
const device = playwright.devices['iPad Air'];
const context = await browser.newContext({...device});
const page = await context.newPage();
await page.goto('https://example.com');
```

**What this includes:**
- Correct viewport size
- Device pixel ratio (DPR)
- Mobile user agent
- Touch event support
- Proper viewport meta tag handling
- Mobile-specific browser behaviors

### For Custom Mobile Dimensions

```javascript
// ✅ CORRECT - Custom mobile viewport
const context = await browser.newContext({
  viewport: { width: 375, height: 667 },  // iPhone SE size
  deviceScaleFactor: 2.0,
  isMobile: true,
  hasTouch: true,
  userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
});
const page = await context.newPage();
await page.goto('https://example.com');
```

### For Desktop Testing

```javascript
// ✅ CORRECT - Desktop viewport
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  deviceScaleFactor: 1.0
});
const page = await context.newPage();
await page.goto('https://example.com');
```

## How TestGPT Uses This

TestGPT's autonomous agent now receives explicit instructions based on the test configuration:

### For iPhone Tests:
```
CRITICAL DEVICE EMULATION:
- MUST use playwright.devices['iPhone 13 Pro'] or similar device descriptor
- Use proper Playwright device emulation, NOT just viewport.setViewportSize()
- Device MUST have: touch events, mobile user agent, correct DPR
- Launch browser with device context from the START (before navigation)
- DO NOT resize window after page load - that breaks responsive behavior
- Page must render at target dimensions from initial load

CORRECT PLAYWRIGHT DEVICE EMULATION PATTERN:
For iPhone testing, use Playwright's built-in device:

// CORRECT - Device emulation from START:
const device = playwright.devices['iPhone 13 Pro'];
const context = await browser.newContext({
  ...device,
  // Network throttling if needed
});
const page = await context.newPage();
await page.goto('URL'); // Page renders correctly from initial load

// WRONG - Don't do this:
await page.setViewportSize({width: 390, height: 844}); // ❌ Breaks responsive behavior
```

## Testing Responsive Behavior Properly

### ✅ DO: Set dimensions before page load
```javascript
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3.0,
  isMobile: true
});
const page = await context.newPage();
await page.goto('https://example.com');
// Page renders correctly from start
```

### ❌ DON'T: Resize after page load
```javascript
const page = await browser.newPage();
await page.goto('https://example.com');
await page.setViewportSize({width: 390, height: 844});
// Page won't respond properly
```

### ✅ DO: Test multiple viewports with separate contexts
```javascript
// Test iPhone
const iPhoneContext = await browser.newContext({...playwright.devices['iPhone 13 Pro']});
const iPhonePage = await iPhoneContext.newPage();
await iPhonePage.goto('https://example.com');

// Test iPad
const iPadContext = await browser.newContext({...playwright.devices['iPad Air']});
const iPadPage = await iPadContext.newPage();
await iPadPage.goto('https://example.com');

// Test Desktop
const desktopContext = await browser.newContext({viewport: {width: 1920, height: 1080}});
const desktopPage = await desktopContext.newPage();
await desktopPage.goto('https://example.com');
```

## Available Playwright Devices

Common devices available in `playwright.devices`:
- `'iPhone 13 Pro'`
- `'iPhone 13 Pro Max'`
- `'iPhone 12'`
- `'iPhone SE'`
- `'iPad Air'`
- `'iPad Pro'`
- `'Pixel 5'`
- `'Galaxy S8'`
- `'Desktop Chrome'`
- `'Desktop Firefox'`
- `'Desktop Safari'`

## Network Throttling

Combine device emulation with network conditions:

```javascript
const context = await browser.newContext({
  ...playwright.devices['iPhone 13 Pro'],
  offline: false,
  // Simulate Slow 3G
  downloadThroughput: (500 * 1024) / 8,  // 500 Kbps in bytes/sec
  uploadThroughput: (500 * 1024) / 8,
  latency: 400  // 400ms latency
});
```

## Key Takeaways

1. **Set device context BEFORE page load** - Not after
2. **Use playwright.devices** for standard devices - They include all necessary configs
3. **Don't resize after load** - Breaks responsive behavior
4. **Each viewport needs new context** - Don't reuse contexts for different sizes
5. **Include all device properties** - viewport + DPR + mobile flag + user agent + touch

## References

- [Playwright Device Emulation Docs](https://playwright.dev/docs/emulation)
- [Playwright Device Descriptors](https://github.com/microsoft/playwright/blob/main/packages/playwright-core/src/server/deviceDescriptorsSource.json)
- [Network Throttling](https://playwright.dev/docs/network#network-mocking)
