"""
Installation Verification Script

Run this script to verify that all dependencies for backend API testing
are correctly installed.

Usage:
    python verify_installation.py
"""

import sys
import importlib
from typing import List, Tuple


def check_module(module_name: str, package_name: str = None) -> bool:
    """
    Check if a Python module is installed.

    Args:
        module_name: Name of the module to import
        package_name: Display name (if different from module name)

    Returns:
        True if module is installed, False otherwise
    """
    if package_name is None:
        package_name = module_name

    try:
        mod = importlib.import_module(module_name)
        version = getattr(mod, '__version__', 'unknown')
        print(f"  ✓ {package_name:20s} (version: {version})")
        return True
    except ImportError:
        print(f"  ✗ {package_name:20s} NOT INSTALLED")
        return False


def verify_installation() -> Tuple[List[str], List[str]]:
    """
    Verify all required packages are installed.

    Returns:
        Tuple of (installed_packages, missing_packages)
    """
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        Backend API Testing - Installation Verification              ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
    """)

    print(f"Python version: {sys.version.split()[0]}")
    print(f"Python path: {sys.executable}\n")

    # Core dependencies
    print("Core Dependencies:")
    print("-" * 70)
    core_packages = [
        ("agno", None),
        ("mcp", None),
        ("anthropic", None),
        ("dotenv", "python-dotenv"),
    ]

    # Backend API testing dependencies
    print("\nBackend API Testing Dependencies:")
    print("-" * 70)
    backend_packages = [
        ("fastapi", None),
        ("uvicorn", None),
        ("fastmcp", None),
        ("httpx", None),
        ("pytest", None),
        ("pytest_asyncio", "pytest-asyncio"),
    ]

    # Optional dependencies
    print("\nOptional Dependencies:")
    print("-" * 70)
    optional_packages = [
        ("slack_bolt", "slack-bolt"),
        ("streamlit", None),
        ("filetype", None),
    ]

    installed = []
    missing = []

    # Check all packages
    for packages_list in [core_packages, backend_packages, optional_packages]:
        for module_name, package_name in packages_list:
            if check_module(module_name, package_name or module_name):
                installed.append(package_name or module_name)
            else:
                missing.append(package_name or module_name)

    return installed, missing


def check_environment():
    """Check for required environment variables."""
    import os

    print("\nEnvironment Variables:")
    print("-" * 70)

    env_vars = {
        "ANTHROPIC_API_KEY": "Required for Agno agents",
        "SLACK_BOT_TOKEN": "Optional - for Slack bot",
        "SLACK_APP_TOKEN": "Optional - for Slack bot",
    }

    for var_name, description in env_vars.items():
        value = os.getenv(var_name)
        if value:
            # Show partial value for security
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✓ {var_name:20s} = {masked} ({description})")
        else:
            required = "Required" in description
            symbol = "✗" if required else "○"
            print(f"  {symbol} {var_name:20s} NOT SET ({description})")


def check_file_structure():
    """Check if required files and directories exist."""
    from pathlib import Path

    print("\nFile Structure:")
    print("-" * 70)

    base_dir = Path(__file__).parent

    required_files = [
        "backend_api/sample_api.py",
        "backend_api/fastmcp_wrapper.py",
        "backend_api/server_launcher.py",
        "backend_api/__init__.py",
        "06_backend_api_testing_agent.py",
        "tests/test_backend_api.py",
        "requirements.txt",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} MISSING")
            all_exist = False

    return all_exist


def main():
    """Main verification function."""
    # Check packages
    installed, missing = verify_installation()

    # Check environment
    check_environment()

    # Check files
    files_ok = check_file_structure()

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    print(f"Installed packages: {len(installed)}")
    print(f"Missing packages:   {len(missing)}")

    if missing:
        print("\nMissing packages:")
        for package in missing:
            print(f"  - {package}")
        print("\nTo install missing packages:")
        print("  pip install -r requirements.txt")
        print("\nOr install individually:")
        print(f"  pip install {' '.join(missing)}")

    if not files_ok:
        print("\n⚠️  Some required files are missing!")
        print("Please ensure you have all the backend API testing files.")

    # Final status
    print("\n" + "=" * 70)
    if not missing and files_ok:
        print("✅ ALL CHECKS PASSED - Ready to use backend API testing!")
        print("\nNext steps:")
        print("  1. Set ANTHROPIC_API_KEY in .env file")
        print("  2. Run: python 06_backend_api_testing_agent.py")
        print("  3. Or run tests: pytest tests/test_backend_api.py -v")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - Please fix the issues above")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
