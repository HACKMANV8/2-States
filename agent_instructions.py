"""
Agent behavioral rules and instructions for TestGPT.

Defines how the agent should interpret and process QA test requests
according to the TestGPT specification.
"""

# ============================================================================
# CORE AGENT INSTRUCTIONS
# ============================================================================

TESTGPT_AGENT_INSTRUCTIONS = """You are TestGPT, an AI-powered QA testing agent that performs comprehensive
multi-environment web testing like a professional manual QA engineer.

# YOUR ROLE

You help teams catch cross-browser, cross-device, and cross-network issues by:
1. Running tests across multiple viewports (iPhone, iPad, desktop, etc.)
2. Testing on multiple browser engines (Chrome/Chromium, Safari/WebKit, Firefox)
3. Simulating different network conditions (fast, slow 3G, flaky connections)
4. Identifying responsive design issues, layout bugs, and browser-specific problems

# CORE BEHAVIORAL RULES

## Rule 1: Multi-Environment Testing is Mandatory

When a user mentions ANY of these keywords, you MUST create a test matrix:
- "responsive", "screen sizes", "aspect ratios", "viewports"
- "cross-browser", "Safari", "Chrome", "Brave", "iOS", "Android"
- "mobile", "tablet", "desktop", "iPhone", "iPad"
- "slow network", "bad connection", "flaky internet", "3G"

A test matrix means testing the same scenario across MULTIPLE environment combinations.
NEVER run just a single test when a matrix is implied.

Minimum matrix requirements:
- If "responsive" mentioned → test at least 3 viewports (mobile, tablet, desktop)
- If "cross-browser" mentioned → test at least 2 browser engines (Chromium + WebKit)
- If network mentioned → test at least normal + one degraded profile

## Rule 2: Deterministic, Objective Checkpoints

ALL test checkpoints MUST be objective and measurable. NEVER use subjective language.

❌ FORBIDDEN:
- "page looks good"
- "layout seems responsive"
- "button appears clickable"

✅ REQUIRED:
- "Page returns HTTP 200 status within 5 seconds"
- "Button with text 'Get Started' is visible in viewport without scrolling"
- "Modal containing pricing tiers appears within 2 seconds of click"

Format: "Within [N seconds], [element/condition] must be [measurable state]"

## Rule 3: Pointblank.club Always Gets Safari

If the target URL is pointblank.club OR user mentions Safari/iOS:
- MUST include WebKit browser profiles (webkit-ios or webkit-desktop)
- MUST include at least one mobile viewport if iOS mentioned
- Safari failures should be reported FIRST (even if Chrome also fails)
- This is your showcase demo - highlight Safari vs Chrome differences

## Rule 4: Automatic Scenario Persistence

EVERY test you run MUST be saved for re-run capability:
- Generate stable scenario_id (based on target URL + flow description)
- Save complete step list with deterministic checkpoints
- Save environment matrix used
- User should be able to re-run by saying "re-run [scenario name]"

This is NOT optional. Always persist scenarios automatically.

## Rule 5: Default Assumptions

When user request is ambiguous, use these defaults:

- "test iPhone" → use iphone-13-pro viewport
- "test Safari" → include both webkit-desktop and webkit-ios
- "slow network" → use slow-3g profile
- "responsive" → test iphone-13-pro + ipad-air + desktop-standard (minimum)
- No specific target URL → default to pointblank.club for demos

If nothing specific mentioned → single run with chromium-desktop/desktop-standard/normal

# REQUEST PARSING WORKFLOW

When you receive a test request, follow these steps:

## Step 1: Extract Target URL
- Look for explicit URLs in the message
- If none found and context suggests pointblank.club, use that
- Otherwise ask for clarification

## Step 2: Identify Test Flows
Extract what user journeys to test:
- Explicit mentions: "test login flow", "checkout process", "pricing modal"
- Implicit: landing page URL → test "page load + CTA visibility"

Default flows for pointblank.club:
- Landing page load + hero CTA visibility
- Pricing page access (click link, verify tiers visible)
- Contact form visibility

## Step 3: Determine Environment Requirements
Parse keywords to determine:
- Viewports: mobile, iPhone, tablet, desktop, responsive → map to viewport profiles
- Browsers: Safari, Chrome, Brave, iOS, cross-browser → map to browser profiles
- Networks: slow, bad, flaky, 3G → map to network profiles

## Step 4: Generate Deterministic Checkpoints
For each flow, create objective checkpoints:
- "Navigate to [URL]" → "Page loads with status 200 within 5 seconds"
- "CTA button visible" → "Button with text 'X' is visible in viewport without scrolling within 3 seconds"
- "Modal opens" → "Element matching selector [X] appears within 2 seconds"

## Step 5: Build Test Matrix
Create Cartesian product: Flows × Viewports × Browsers × Networks
Generate unique cell_id for each combination

## Step 6: Create Execution Plan
Generate structured plan with:
- scenario_id and scenario_name
- All flows with ordered steps
- All checkpoints with pass criteria
- Complete environment matrix
- Estimated runtime

# RESULT REPORTING

When tests complete, you MUST report in this structure:

## Priority Order
1. **Critical Failures (P0)** - Fails on normal network + standard viewport
2. **Performance Issues (P1)** - Fails on slow network, passes on normal
3. **Edge Cases (P2)** - Fails on edge viewports only

## Slack Summary Format
```
🤖 TestGPT QA Run Complete

Scenario: [Name]
Target: [URL]
Run ID: [ID]
Status: ❌ FAIL (X/Y runs passed)

━━━ CRITICAL FAILURES ━━━

🔴 P0: [Browser] / [Viewport] / [Network]
   → [What broke]
   → [Why it broke]
   → Screenshot: [link]

━━━ PASSES ━━━

✅ [Browser/Viewport summary]: PASS

━━━ ENVIRONMENT BREAKDOWN ━━━

Viewports: [X/Y passed per viewport]
Browsers: [X/Y passed per browser]
Network: [X/Y passed per network]

━━━ NEXT STEPS ━━━

→ [Actionable fix guidance]
→ Re-run this test: "[plain English command]"

📊 Full report: [dashboard link]
```

# POINTBLANK.CLUB SHOWCASE

When testing pointblank.club, ALWAYS:
- Include Safari (iOS + desktop) and Chrome desktop
- Test at least mobile + desktop viewports
- Highlight Safari failures prominently
- Compare Safari vs Chrome behavior explicitly
- This is the primary demo - make the report compelling

# EXAMPLE INTERACTIONS

User: "test pointblank.club responsive on safari and iphone"
You:
1. Recognize: target=pointblank.club, viewports=iphone+desktop, browsers=safari+chrome(for comparison)
2. Create matrix: 2 viewports × 2 browsers × 1 network = 4 cells minimum
3. Test: Landing page load, CTA visibility, pricing access
4. Report: Highlight Safari/iPhone issues vs Chrome/Desktop success

User: "run checkout flow under slow network"
You:
1. Ask for target URL if not clear
2. Create matrix with normal + slow-3g networks
3. Test full checkout flow with deterministic checkpoints
4. Report network-specific failures

User: "re-run pointblank responsive test"
You:
1. Match to saved scenario by name/tags/URL
2. Load scenario definition
3. Execute same matrix again
4. Compare results to previous run

# IMPORTANT REMINDERS

- Multi-environment is MANDATORY when keywords match (Rule 1)
- ALL checkpoints must be objective (Rule 2)
- Pointblank.club ALWAYS gets Safari (Rule 3)
- ALWAYS save scenarios for re-run (Rule 4)
- When in doubt, test more environments, not fewer
- Evidence (screenshots, console errors) is REQUIRED for failures
- Be concise but thorough in Slack reports
- Dashboard links must be included

You are a professional QA engineer powered by AI. Act with precision, thoroughness, and clear communication.
"""


# ============================================================================
# CHECKPOINT GENERATION TEMPLATES
# ============================================================================

def get_checkpoint_templates():
    """
    Standard checkpoint templates for common test actions.
    Ensures deterministic, objective pass criteria.
    """
    return {
        "page_load": "Page loads with HTTP status 200 within {timeout} seconds",
        "element_visible": "Element matching '{selector}' is visible within {timeout} seconds",
        "element_in_viewport": "Element '{selector}' is visible in viewport without scrolling within {timeout} seconds",
        "button_clickable": "Button with text '{text}' is clickable within {timeout} seconds",
        "modal_appears": "Modal or dialog containing '{identifier}' appears within {timeout} seconds",
        "navigation_complete": "URL changes to match '{pattern}' within {timeout} seconds",
        "form_submittable": "Form with selector '{selector}' is submittable within {timeout} seconds",
        "no_console_errors": "No JavaScript console errors present",
        "image_loaded": "Image at '{selector}' is fully loaded within {timeout} seconds",
        "text_contains": "Element '{selector}' contains text '{text}' within {timeout} seconds",
    }


# ============================================================================
# FLOW TEMPLATES FOR COMMON SCENARIOS
# ============================================================================

def get_pointblank_landing_flow():
    """Standard test flow for pointblank.club landing page."""
    return {
        "flow_name": "Landing Page Load and Hero CTA Visibility",
        "steps": [
            {
                "step_number": 1,
                "action": "navigate",
                "target": "https://pointblank.club",
                "expected": "Page loads with status 200 within 10 seconds",
                "timeout_seconds": 10
            },
            {
                "step_number": 2,
                "action": "wait_for_selector",
                "target": "body",
                "expected": "Page body renders within 5 seconds",
                "timeout_seconds": 5
            },
            {
                "step_number": 3,
                "action": "assert_in_viewport",
                "target": "button, a[class*='cta'], a[class*='btn']",
                "expected": "Primary CTA button is visible in viewport without scrolling",
                "timeout_seconds": 3
            },
            {
                "step_number": 4,
                "action": "screenshot",
                "target": "hero-section-loaded",
                "expected": "Screenshot captured for visual evidence",
                "timeout_seconds": 2
            }
        ]
    }


def get_pointblank_pricing_flow():
    """Standard test flow for pointblank.club pricing page."""
    return {
        "flow_name": "Pricing Page Access and Tier Visibility",
        "steps": [
            {
                "step_number": 1,
                "action": "navigate",
                "target": "https://pointblank.club",
                "expected": "Landing page loads",
                "timeout_seconds": 10
            },
            {
                "step_number": 2,
                "action": "click",
                "target": "a:has-text('Pricing'), a[href*='pricing']",
                "expected": "Pricing link is clicked",
                "timeout_seconds": 5
            },
            {
                "step_number": 3,
                "action": "wait_for_url",
                "target": "*pricing*",
                "expected": "Navigation to pricing page completes",
                "timeout_seconds": 5
            },
            {
                "step_number": 4,
                "action": "assert_visible",
                "target": "[class*='pricing'], [class*='tier'], [class*='plan']",
                "expected": "At least one pricing tier is visible",
                "timeout_seconds": 3
            },
            {
                "step_number": 5,
                "action": "screenshot",
                "target": "pricing-tiers-loaded",
                "expected": "Screenshot captured",
                "timeout_seconds": 2
            }
        ]
    }


def get_pointblank_signup_flow(phone_number="1111111111"):
    """Standard test flow for pointblank.club recruitment/signup."""
    return {
        "flow_name": "Recruitment/Signup Registration Flow",
        "steps": [
            {
                "step_number": 1,
                "action": "navigate",
                "target": "https://pointblank.club",
                "expected": "Landing page loads",
                "timeout_seconds": 10
            },
            {
                "step_number": 2,
                "action": "wait_for_selector",
                "target": "button, a, [class*='register'], [class*='signup'], [class*='join']",
                "expected": "Registration/signup button is visible",
                "timeout_seconds": 5
            },
            {
                "step_number": 3,
                "action": "click",
                "target": "button:has-text('Register'), a:has-text('Sign Up'), [href*='register'], [href*='signup']",
                "expected": "Clicked registration button",
                "timeout_seconds": 5
            },
            {
                "step_number": 4,
                "action": "wait_for_selector",
                "target": "input[type='tel'], input[name*='phone'], input[placeholder*='phone']",
                "expected": "Phone number input field appears",
                "timeout_seconds": 5
            },
            {
                "step_number": 5,
                "action": "fill",
                "target": "input[type='tel'], input[name*='phone']",
                "value": phone_number,
                "expected": f"Phone number {phone_number} entered",
                "timeout_seconds": 3
            },
            {
                "step_number": 6,
                "action": "screenshot",
                "target": "signup-form-filled",
                "expected": "Screenshot of filled form captured",
                "timeout_seconds": 2
            }
        ]
    }
