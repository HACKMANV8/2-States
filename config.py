"""
Configuration catalogs for TestGPT.

Defines standard viewport, browser, and network profiles
according to the TestGPT specification.
"""

from typing import List
from models import ViewportProfile, BrowserProfile, NetworkProfile


# ============================================================================
# VIEWPORT PROFILES CATALOG
# ============================================================================

VIEWPORT_PROFILES = {
    "iphone-se": ViewportProfile(
        name="iphone-se",
        width=375,
        height=667,
        device_class="Budget iOS",
        description="Smallest modern iPhone; catches bottom nav cutoff, narrow column overflow",
        device_scale_factor=2.0,
        is_mobile=True
    ),

    "iphone-13-pro": ViewportProfile(
        name="iphone-13-pro",
        width=390,
        height=844,
        device_class="Standard iOS",
        description="Most common iPhone viewport; baseline for iOS testing",
        device_scale_factor=3.0,
        is_mobile=True
    ),

    "iphone-13-pro-landscape": ViewportProfile(
        name="iphone-13-pro-landscape",
        width=844,
        height=390,
        device_class="iOS landscape",
        description="Catches horizontal layout breakage, header collapse issues",
        device_scale_factor=3.0,
        is_mobile=True
    ),

    "android-small": ViewportProfile(
        name="android-small",
        width=360,
        height=640,
        device_class="Cheap Android",
        description="Common low-end Android; smallest practical mobile viewport",
        device_scale_factor=2.0,
        is_mobile=True
    ),

    "android-medium": ViewportProfile(
        name="android-medium",
        width=412,
        height=915,
        device_class="Mid-range Android",
        description="Galaxy S-class; catches Android-specific rendering quirks",
        device_scale_factor=2.5,
        is_mobile=True
    ),

    "ipad-air": ViewportProfile(
        name="ipad-air",
        width=820,
        height=1180,
        device_class="Tablet portrait",
        description="Tablet breakpoint; often forgotten in responsive design",
        device_scale_factor=2.0,
        is_mobile=False
    ),

    "ipad-air-landscape": ViewportProfile(
        name="ipad-air-landscape",
        width=1180,
        height=820,
        device_class="Tablet landscape",
        description="Horizontal tablet; catches weird mid-size layout bugs",
        device_scale_factor=2.0,
        is_mobile=False
    ),

    "desktop-standard": ViewportProfile(
        name="desktop-standard",
        width=1920,
        height=1080,
        device_class="Desktop baseline",
        description="Most common desktop resolution; developer default",
        device_scale_factor=1.0,
        is_mobile=False
    ),

    "desktop-ultrawide": ViewportProfile(
        name="desktop-ultrawide",
        width=2560,
        height=1440,
        device_class="Large desktop",
        description="Catches max-width issues, ultra-wide layout stretch",
        device_scale_factor=1.0,
        is_mobile=False
    ),

    "desktop-narrow": ViewportProfile(
        name="desktop-narrow",
        width=1366,
        height=768,
        device_class="Laptop / small desktop",
        description="Older laptop resolution; still ~15% of users",
        device_scale_factor=1.0,
        is_mobile=False
    ),
}


# ============================================================================
# BROWSER PROFILES CATALOG
# ============================================================================

BROWSER_PROFILES = {
    "chromium-desktop": BrowserProfile(
        name="chromium-desktop",
        engine="chromium",
        display_name="Chrome (Desktop)",
        platform="desktop",
        user_agent_type="desktop"
    ),

    "webkit-desktop": BrowserProfile(
        name="webkit-desktop",
        engine="webkit",
        display_name="Safari (macOS)",
        platform="desktop",
        user_agent_type="desktop"
    ),

    "webkit-ios": BrowserProfile(
        name="webkit-ios",
        engine="webkit",
        display_name="Safari (iOS)",
        platform="mobile",
        user_agent_type="mobile"
    ),

    "firefox-desktop": BrowserProfile(
        name="firefox-desktop",
        engine="firefox",
        display_name="Firefox (Desktop)",
        platform="desktop",
        user_agent_type="desktop"
    ),
}


# ============================================================================
# NETWORK PROFILES CATALOG
# ============================================================================

NETWORK_PROFILES = {
    "normal": NetworkProfile(
        name="normal",
        display_name="Good Broadband",
        latency_ms=50,
        download_kbps=10000,
        upload_kbps=5000,
        packet_loss_percent=0.0,
        description="Baseline; no throttling. Any failure here is critical."
    ),

    "slow-3g": NetworkProfile(
        name="slow-3g",
        display_name="Slow 3G",
        latency_ms=400,
        download_kbps=400,
        upload_kbps=400,
        packet_loss_percent=0.0,
        description="Slow mobile connection. Catches spinners that never resolve, lazy-load images stuck, hero content timeout."
    ),

    "flaky-edge": NetworkProfile(
        name="flaky-edge",
        display_name="Flaky/Unstable Connection",
        latency_ms=200,  # Variable 200-800ms in practice
        download_kbps=1000,
        upload_kbps=500,
        packet_loss_percent=2.0,
        description="Unstable/packet-lossy. Catches button clicks that don't register, form submissions that fail silently, WebSocket disconnects."
    ),
}


# ============================================================================
# SELECTION HELPERS
# ============================================================================

def get_viewport(name: str) -> ViewportProfile:
    """Get viewport profile by name."""
    if name not in VIEWPORT_PROFILES:
        raise ValueError(f"Unknown viewport profile: {name}")
    return VIEWPORT_PROFILES[name]


def get_browser(name: str) -> BrowserProfile:
    """Get browser profile by name."""
    if name not in BROWSER_PROFILES:
        raise ValueError(f"Unknown browser profile: {name}")
    return BROWSER_PROFILES[name]


def get_network(name: str) -> NetworkProfile:
    """Get network profile by name."""
    if name not in NETWORK_PROFILES:
        raise ValueError(f"Unknown network profile: {name}")
    return NETWORK_PROFILES[name]


def select_viewports_for_keywords(keywords: List[str]) -> List[str]:
    """
    Select appropriate viewports based on user keywords.

    Rules from specification TODO 2.
    """
    keywords_lower = [k.lower() for k in keywords]
    selected = set()

    # Check for specific mentions
    if any(k in keywords_lower for k in ["mobile"]):
        selected.add("iphone-13-pro")
        selected.add("android-medium")

    if any(k in keywords_lower for k in ["iphone", "ios"]):
        selected.add("iphone-13-pro")
        if any(k in keywords_lower for k in ["cheap", "budget", "small"]):
            selected.add("iphone-se")

    if any(k in keywords_lower for k in ["android"]):
        selected.add("android-medium")
        if any(k in keywords_lower for k in ["cheap", "budget", "low-end", "small"]):
            selected.add("android-small")

    if any(k in keywords_lower for k in ["tablet", "ipad"]):
        selected.add("ipad-air")

    if any(k in keywords_lower for k in ["desktop"]):
        selected.add("desktop-standard")

    if any(k in keywords_lower for k in ["responsive", "screen sizes", "aspect ratios"]):
        # Minimum 3-point coverage
        selected.add("iphone-13-pro")
        selected.add("ipad-air")
        selected.add("desktop-standard")

    if any(k in keywords_lower for k in ["comprehensive"]):
        # All viewports
        return list(VIEWPORT_PROFILES.keys())

    # Default if nothing specified
    if not selected:
        selected.add("desktop-standard")

    return list(selected)


def select_browsers_for_keywords(keywords: List[str], target_url: str = "") -> List[str]:
    """
    Select appropriate browsers based on user keywords and target URL.

    Rules from specification TODO 3.
    """
    keywords_lower = [k.lower() for k in keywords]
    selected = set()

    # Pointblank.club ALWAYS gets Safari (RULE 4)
    if "pointblank.club" in target_url.lower():
        selected.add("webkit-ios")
        selected.add("webkit-desktop")
        selected.add("chromium-desktop")  # For comparison
        return list(selected)

    # Check for specific browser mentions
    if any(k in keywords_lower for k in ["safari", "webkit", "ios", "iphone", "ipad"]):
        selected.add("webkit-desktop")
        if any(k in keywords_lower for k in ["ios", "iphone", "mobile"]):
            selected.add("webkit-ios")

    if any(k in keywords_lower for k in ["brave", "chrome", "chromium"]):
        selected.add("chromium-desktop")

    if any(k in keywords_lower for k in ["firefox"]):
        selected.add("firefox-desktop")

    if any(k in keywords_lower for k in ["cross-browser"]):
        selected.add("chromium-desktop")
        selected.add("webkit-desktop")

    # Default if nothing specified
    if not selected:
        selected.add("chromium-desktop")

    return list(selected)


def select_networks_for_keywords(keywords: List[str]) -> List[str]:
    """
    Select appropriate network profiles based on user keywords.

    Rules from specification TODO 4.
    """
    keywords_lower = [k.lower() for k in keywords]
    selected = set()

    # Always include normal
    selected.add("normal")

    # Check for degraded network mentions
    if any(k in keywords_lower for k in ["bad network", "slow network", "poor connection", "slow", "3g"]):
        selected.add("slow-3g")

    if any(k in keywords_lower for k in ["flaky", "unstable", "edge case", "packet loss"]):
        selected.add("flaky-edge")

    if any(k in keywords_lower for k in ["network conditions", "under load"]):
        selected.add("slow-3g")

    return list(selected)
