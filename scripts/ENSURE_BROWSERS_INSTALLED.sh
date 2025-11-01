#!/bin/bash
# ==============================================================================
# TestGPT Browser Installation & Verification Script
# ==============================================================================
# This script ensures all browsers (Chromium, WebKit, Firefox) are properly
# installed and configured for both standard Playwright and MCP usage.
#
# Run this script anytime you encounter "browser not installed" errors.
# ==============================================================================

set -e  # Exit on error

echo "=========================================================================="
echo "🔧 TestGPT Browser Installation & Verification"
echo "=========================================================================="
echo ""

PLAYWRIGHT_CACHE="$HOME/Library/Caches/ms-playwright"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ==============================================================================
# Step 1: Install all Playwright browsers
# ==============================================================================

echo "📦 Step 1: Installing all Playwright browsers..."
echo "   This may take a few minutes if browsers need to be downloaded."
echo ""

npx playwright install chromium webkit firefox 2>&1 | grep -v "^$" || true

echo ""
echo -e "${GREEN}✅ Browser installation complete${NC}"
echo ""

# ==============================================================================
# Step 2: Find latest browser versions
# ==============================================================================

echo "🔍 Step 2: Detecting installed browser versions..."
echo ""

# Find latest chromium
CHROMIUM_LATEST=$(ls -t "$PLAYWRIGHT_CACHE" | grep "^chromium-[0-9]" | head -1)
WEBKIT_LATEST=$(ls -t "$PLAYWRIGHT_CACHE" | grep "^webkit-[0-9]" | head -1)
FIREFOX_LATEST=$(ls -t "$PLAYWRIGHT_CACHE" | grep "^firefox-[0-9]" | head -1)

echo "   Chromium: $CHROMIUM_LATEST"
echo "   WebKit:   $WEBKIT_LATEST"
echo "   Firefox:  $FIREFOX_LATEST"
echo ""

# ==============================================================================
# Step 3: Verify browser binaries exist
# ==============================================================================

echo "✓  Step 3: Verifying browser binaries..."
echo ""

# Check Chromium
if [ -d "$PLAYWRIGHT_CACHE/$CHROMIUM_LATEST/chrome-mac/Chromium.app" ]; then
    echo -e "   ${GREEN}✅ Chromium binary found${NC}"
else
    echo -e "   ${RED}❌ Chromium binary NOT found${NC}"
    exit 1
fi

# Check WebKit
if [ -d "$PLAYWRIGHT_CACHE/$WEBKIT_LATEST/Playwright.app" ]; then
    echo -e "   ${GREEN}✅ WebKit binary found${NC}"
else
    echo -e "   ${RED}❌ WebKit binary NOT found${NC}"
    exit 1
fi

# Check Firefox
if [ -d "$PLAYWRIGHT_CACHE/$FIREFOX_LATEST/firefox" ]; then
    echo -e "   ${GREEN}✅ Firefox binary found${NC}"
else
    echo -e "   ${RED}❌ Firefox binary NOT found${NC}"
    exit 1
fi

echo ""

# ==============================================================================
# Step 4: Fix MCP browser symlinks
# ==============================================================================

echo "🔗 Step 4: Setting up MCP browser symlinks..."
echo ""

cd "$PLAYWRIGHT_CACHE"

# Remove broken mcp-webkit if it's a directory (not symlink)
if [ -d "mcp-webkit" ] && [ ! -L "mcp-webkit" ]; then
    echo "   Removing broken mcp-webkit directory..."
    rm -rf mcp-webkit
fi

# Create mcp-webkit symlink
if [ -L "mcp-webkit" ]; then
    echo "   mcp-webkit symlink already exists"
else
    ln -s "$WEBKIT_LATEST" mcp-webkit
    echo -e "   ${GREEN}✅ Created mcp-webkit → $WEBKIT_LATEST${NC}"
fi

# Note: mcp-chromium and mcp-chrome are user data directories, not browser binaries
# They are created automatically by MCP and should not be symlinks

echo ""

# ==============================================================================
# Step 5: Create .links directory for Playwright
# ==============================================================================

echo "📂 Step 5: Setting up Playwright browser links..."
echo ""

cd "$PLAYWRIGHT_CACHE"
mkdir -p .links

# Create links for Playwright's browser detection
if [ ! -e ".links/chromium-$(cd $CHROMIUM_LATEST && pwd)" ]; then
    ln -sf "../$CHROMIUM_LATEST" .links/chromium 2>/dev/null || true
fi

if [ ! -e ".links/webkit-$(cd $WEBKIT_LATEST && pwd)" ]; then
    ln -sf "../$WEBKIT_LATEST" .links/webkit 2>/dev/null || true
fi

if [ ! -e ".links/firefox-$(cd $FIREFOX_LATEST && pwd)" ]; then
    ln -sf "../$FIREFOX_LATEST" .links/firefox 2>/dev/null || true
fi

echo -e "   ${GREEN}✅ Browser links configured${NC}"
echo ""

# ==============================================================================
# Step 6: Verify everything works
# ==============================================================================

echo "🧪 Step 6: Verifying browser installations..."
echo ""

# Test Chromium
if [ -x "$PLAYWRIGHT_CACHE/$CHROMIUM_LATEST/chrome-mac/Chromium.app/Contents/MacOS/Chromium" ]; then
    echo -e "   ${GREEN}✅ Chromium executable is valid${NC}"
else
    echo -e "   ${YELLOW}⚠️  Chromium executable not found at expected location${NC}"
fi

# Test WebKit
if [ -x "$PLAYWRIGHT_CACHE/$WEBKIT_LATEST/Playwright.app/Contents/MacOS/Playwright" ]; then
    echo -e "   ${GREEN}✅ WebKit executable is valid${NC}"
else
    echo -e "   ${YELLOW}⚠️  WebKit executable not found at expected location${NC}"
fi

# Test Firefox
if [ -d "$PLAYWRIGHT_CACHE/$FIREFOX_LATEST/firefox/Firefox.app" ] || [ -d "$PLAYWRIGHT_CACHE/$FIREFOX_LATEST/firefox/firefox" ]; then
    echo -e "   ${GREEN}✅ Firefox installation is valid${NC}"
else
    echo -e "   ${YELLOW}⚠️  Firefox installation not found at expected location${NC}"
fi

echo ""

# ==============================================================================
# Step 7: Display summary
# ==============================================================================

echo "=========================================================================="
echo "✅ BROWSER SETUP COMPLETE"
echo "=========================================================================="
echo ""
echo "Installed browsers:"
echo "  • Chromium: $PLAYWRIGHT_CACHE/$CHROMIUM_LATEST"
echo "  • WebKit:   $PLAYWRIGHT_CACHE/$WEBKIT_LATEST"
echo "  • Firefox:  $PLAYWRIGHT_CACHE/$FIREFOX_LATEST"
echo ""
echo "MCP Configuration:"
echo "  • mcp-webkit → $WEBKIT_LATEST (symlink)"
echo "  • mcp-chromium (user data directory)"
echo "  • mcp-chrome (user data directory)"
echo ""
echo "You should no longer see 'browser not installed' errors!"
echo ""
echo "If you still encounter issues, run:"
echo "  ./scripts/ENSURE_BROWSERS_INSTALLED.sh"
echo ""
echo "=========================================================================="
