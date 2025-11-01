"""
Seed database with default configuration templates.

Creates common configuration presets like:
- Regression Suite (multiple browsers and viewports)
- Smoke Tests (quick desktop-only tests)
- Mobile Testing (mobile viewports only)
- Cross-browser (all browsers, standard viewport)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from backend.database import SessionLocal, init_db
from backend.crud import create_config_template, get_config_templates
from backend.schemas import ConfigurationTemplateCreate, ViewportConfig


def seed_default_configs():
    """Create default configuration templates"""
    db = SessionLocal()

    try:
        # Check if configs already exist
        existing = get_config_templates(db, limit=1)
        if existing:
            print("  Configuration templates already exist. Skipping seed.")
            return

        print(" Seeding default configuration templates...")

        # 1. Regression Suite - Comprehensive testing
        regression_config = ConfigurationTemplateCreate(
            name="Regression Suite",
            description="Comprehensive testing across multiple browsers, viewports, and network conditions",
            browsers=["chrome", "firefox", "safari"],
            viewports=[
                ViewportConfig(width=375, height=667, device_name="iPhone SE"),
                ViewportConfig(width=768, height=1024, device_name="iPad"),
                ViewportConfig(width=1920, height=1080, device_name="Desktop"),
            ],
            network_modes=["online", "slow3g"],
            screenshot_on_failure=True,
            video_recording=False,
            parallel_execution=True,
            max_workers=4,
            default_timeout=30000,
        )
        create_config_template(db, regression_config)
        print("   Created: Regression Suite")

        # 2. Smoke Tests - Quick validation
        smoke_config = ConfigurationTemplateCreate(
            name="Smoke Tests",
            description="Quick smoke tests on desktop Chrome only",
            browsers=["chrome"],
            viewports=[
                ViewportConfig(width=1920, height=1080, device_name="Desktop"),
            ],
            network_modes=["online"],
            screenshot_on_failure=True,
            video_recording=False,
            parallel_execution=False,
            max_workers=1,
            default_timeout=15000,
        )
        create_config_template(db, smoke_config)
        print("   Created: Smoke Tests")

        # 3. Mobile Testing - Mobile devices only
        mobile_config = ConfigurationTemplateCreate(
            name="Mobile Testing",
            description="Testing on mobile viewports with different network conditions",
            browsers=["chrome", "safari"],
            viewports=[
                ViewportConfig(width=375, height=667, device_name="iPhone SE"),
                ViewportConfig(width=390, height=844, device_name="iPhone 13 Pro"),
                ViewportConfig(width=360, height=800, device_name="Android"),
            ],
            network_modes=["online", "fast3g", "slow3g"],
            screenshot_on_failure=True,
            video_recording=False,
            parallel_execution=True,
            max_workers=3,
            default_timeout=45000,
        )
        create_config_template(db, mobile_config)
        print("   Created: Mobile Testing")

        # 4. Cross-Browser - All browsers, standard viewport
        cross_browser_config = ConfigurationTemplateCreate(
            name="Cross-Browser",
            description="Test on all major browsers with standard desktop viewport",
            browsers=["chrome", "firefox", "safari", "edge"],
            viewports=[
                ViewportConfig(width=1920, height=1080, device_name="Desktop"),
            ],
            network_modes=["online"],
            screenshot_on_failure=True,
            video_recording=False,
            parallel_execution=True,
            max_workers=4,
            default_timeout=30000,
        )
        create_config_template(db, cross_browser_config)
        print("   Created: Cross-Browser")

        # 5. Performance Testing - Network condition focus
        performance_config = ConfigurationTemplateCreate(
            name="Performance Testing",
            description="Test performance under various network conditions",
            browsers=["chrome"],
            viewports=[
                ViewportConfig(width=1920, height=1080, device_name="Desktop"),
            ],
            network_modes=["online", "fast3g", "slow3g"],
            screenshot_on_failure=True,
            video_recording=True,
            parallel_execution=False,
            max_workers=1,
            default_timeout=60000,
        )
        create_config_template(db, performance_config)
        print("   Created: Performance Testing")

        # 6. Quick Debug - Single config for debugging
        debug_config = ConfigurationTemplateCreate(
            name="Quick Debug",
            description="Single configuration for quick debugging",
            browsers=["chrome"],
            viewports=[
                ViewportConfig(width=1920, height=1080, device_name="Desktop"),
            ],
            network_modes=["online"],
            screenshot_on_failure=True,
            video_recording=True,
            parallel_execution=False,
            max_workers=1,
            default_timeout=120000,
        )
        create_config_template(db, debug_config)
        print("   Created: Quick Debug")

        print("\n Successfully seeded 6 configuration templates!")

    except Exception as e:
        print(f" Error seeding data: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # Initialize database first
    init_db()

    # Seed default configs
    seed_default_configs()
