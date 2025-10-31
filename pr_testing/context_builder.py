"""
PR Context Builder for Test Generation.

Builds comprehensive context documents for the testing agent including:
- PR description and acceptance criteria
- Changed files analysis
- Codebase structure insights
- Test scenarios derived from PR changes
"""

from typing import Dict, Any, List
import re


class PRContextBuilder:
    """
    Builds test context from PR information.

    Creates structured context documents that help the testing agent
    understand what to test and why.
    """

    def __init__(self):
        """Initialize context builder."""
        pass

    def extract_acceptance_criteria(self, pr_description: str, linked_issues: List[Dict[str, Any]]) -> List[str]:
        """
        Extract acceptance criteria from PR description and linked issues.

        Looks for:
        - Checkbox lists in markdown
        - "Acceptance Criteria" sections
        - "Requirements" sections
        - Issue descriptions

        Args:
            pr_description: PR description text
            linked_issues: List of linked issues

        Returns:
            List of acceptance criteria
        """
        criteria = []

        # Extract from PR description
        if pr_description:
            # Look for checkbox lists
            checkbox_pattern = r'-\s*\[[ x]\]\s*(.+)'
            checkboxes = re.findall(checkbox_pattern, pr_description, re.MULTILINE)
            criteria.extend(checkboxes)

            # Look for "Acceptance Criteria" section
            ac_pattern = r'(?:Acceptance Criteria|Requirements|Testing|Checklist)[\s:]*\n+((?:[-*]\s+.+\n*)+)'
            ac_match = re.search(ac_pattern, pr_description, re.IGNORECASE)
            if ac_match:
                ac_items = re.findall(r'[-*]\s+(.+)', ac_match.group(1))
                criteria.extend(ac_items)

        # Extract from linked issues
        for issue in linked_issues:
            issue_body = issue.get("body", "")
            if issue_body:
                # Extract checkboxes from issues
                checkboxes = re.findall(r'-\s*\[[ x]\]\s*(.+)', issue_body, re.MULTILINE)
                criteria.extend(checkboxes)

        # Remove duplicates and clean up
        criteria = list(set([c.strip() for c in criteria if c.strip()]))

        return criteria

    def categorize_changed_files(self, pr_files: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """
        Categorize changed files by type.

        Args:
            pr_files: List of changed files from GitHub

        Returns:
            Dict with files categorized by type
        """
        categories = {
            "ui_components": [],
            "pages": [],
            "api_routes": [],
            "backend_logic": [],
            "database": [],
            "styles": [],
            "tests": [],
            "config": [],
            "other": []
        }

        for file_info in pr_files:
            filename = file_info["filename"]
            status = file_info["status"]

            # UI Components
            if any(pattern in filename.lower() for pattern in ["components/", "component"]):
                categories["ui_components"].append(f"{filename} ({status})")

            # Pages/Routes
            elif any(pattern in filename.lower() for pattern in ["pages/", "app/", "views/", "routes/"]):
                if not any(ext in filename.lower() for ext in [".css", ".scss", ".test", ".spec"]):
                    categories["pages"].append(f"{filename} ({status})")

            # API routes
            elif any(pattern in filename.lower() for pattern in ["api/", "endpoints/", "controllers/"]):
                categories["api_routes"].append(f"{filename} ({status})")

            # Backend logic
            elif any(pattern in filename.lower() for pattern in ["services/", "utils/", "helpers/", "lib/"]):
                categories["backend_logic"].append(f"{filename} ({status})")

            # Database
            elif any(pattern in filename.lower() for pattern in ["models/", "schema", "migrations/", "db/"]):
                categories["database"].append(f"{filename} ({status})")

            # Styles
            elif any(ext in filename.lower() for ext in [".css", ".scss", ".sass", ".less", ".styled"]):
                categories["styles"].append(f"{filename} ({status})")

            # Tests
            elif any(pattern in filename.lower() for pattern in ["test", "spec", "__tests__"]):
                categories["tests"].append(f"{filename} ({status})")

            # Config
            elif any(ext in filename.lower() for ext in [".json", ".yml", ".yaml", ".config", ".env"]):
                categories["config"].append(f"{filename} ({status})")

            # Other
            else:
                categories["other"].append(f"{filename} ({status})")

        # Remove empty categories
        return {k: v for k, v in categories.items() if v}

    def generate_test_scenarios(
        self,
        pr_context: Dict[str, Any],
        codebase_analysis: Dict[str, Any],
        deployment_url: str
    ) -> List[Dict[str, Any]]:
        """
        Generate test scenarios based on PR changes.

        Args:
            pr_context: Full PR context
            codebase_analysis: Codebase analysis
            deployment_url: Deployment URL to test

        Returns:
            List of test scenarios
        """
        scenarios = []

        pr_metadata = pr_context.get("metadata", {})
        pr_files = pr_context.get("files", [])
        linked_issues = pr_context.get("linked_issues", [])

        # Extract acceptance criteria
        acceptance_criteria = self.extract_acceptance_criteria(
            pr_metadata.get("description", ""),
            linked_issues
        )

        # Categorize changed files
        file_categories = self.categorize_changed_files(pr_files)

        # Scenario 1: Basic functionality test
        scenarios.append({
            "name": "Basic Functionality Check",
            "priority": "critical",
            "description": "Verify that the main features affected by this PR are working",
            "steps": [
                f"Navigate to {deployment_url}",
                "Verify the page loads without errors",
                "Check that no console errors are present",
                "Verify all main UI elements are visible and interactive"
            ],
            "acceptance_criteria": acceptance_criteria[:3] if acceptance_criteria else []
        })

        # Scenario 2: UI component testing (if UI files changed)
        if file_categories.get("ui_components") or file_categories.get("pages"):
            scenarios.append({
                "name": "UI Component Testing",
                "priority": "high",
                "description": "Test modified UI components and pages",
                "steps": [
                    f"Navigate to {deployment_url}",
                    "Locate and interact with modified UI components",
                    "Verify visual rendering matches expectations",
                    "Test component interactivity (clicks, forms, etc.)",
                    "Check responsive behavior on different viewports"
                ],
                "affected_files": (file_categories.get("ui_components", []) + file_categories.get("pages", []))[:5]
            })

        # Scenario 3: API testing (if API files changed)
        if file_categories.get("api_routes"):
            scenarios.append({
                "name": "API Functionality Testing",
                "priority": "high",
                "description": "Test modified API endpoints",
                "steps": [
                    "Verify API endpoints are accessible",
                    "Test request/response formats",
                    "Check error handling",
                    "Verify data validation"
                ],
                "affected_files": file_categories.get("api_routes", [])[:5]
            })

        # Scenario 4: Visual regression (if styles changed)
        if file_categories.get("styles"):
            scenarios.append({
                "name": "Visual Regression Check",
                "priority": "medium",
                "description": "Verify styling changes don't break layout",
                "steps": [
                    f"Navigate to {deployment_url}",
                    "Check overall page layout",
                    "Verify spacing and alignment",
                    "Test on multiple viewports",
                    "Check for any visual glitches"
                ],
                "affected_files": file_categories.get("styles", [])[:5]
            })

        # Scenario 5: Cross-browser compatibility
        scenarios.append({
            "name": "Cross-Browser Compatibility",
            "priority": "medium",
            "description": "Verify changes work across different browsers",
            "steps": [
                "Test on Chrome/Chromium",
                "Test on Safari/WebKit",
                "Test on Firefox",
                "Verify consistent behavior across browsers"
            ]
        })

        # Scenario 6: Acceptance criteria verification
        if acceptance_criteria:
            scenarios.append({
                "name": "Acceptance Criteria Verification",
                "priority": "critical",
                "description": "Verify all acceptance criteria are met",
                "steps": acceptance_criteria,
                "source": "PR description and linked issues"
            })

        return scenarios

    def build_context_document(
        self,
        pr_context: Dict[str, Any],
        codebase_analysis: Dict[str, Any],
        deployment_info: Dict[str, Any]
    ) -> str:
        """
        Build comprehensive context document for the testing agent.

        This is the main entry point that creates a complete test context.

        Args:
            pr_context: Full PR context from GitHubService
            codebase_analysis: Codebase analysis from CodebaseAnalyzer
            deployment_info: Deployment info from DeploymentDetector

        Returns:
            Formatted context document string
        """
        print("\n📝 Building test context document...")

        pr_metadata = pr_context.get("metadata", {})
        pr_files = pr_context.get("files", [])
        linked_issues = pr_context.get("linked_issues", [])

        deployment_url = deployment_info.get("deployment_url", "")

        # Extract key information
        acceptance_criteria = self.extract_acceptance_criteria(
            pr_metadata.get("description", ""),
            linked_issues
        )

        file_categories = self.categorize_changed_files(pr_files)

        test_scenarios = self.generate_test_scenarios(
            pr_context,
            codebase_analysis,
            deployment_url
        )

        # Build context document
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append("PR TESTING CONTEXT")
        lines.append("=" * 80)
        lines.append("")

        # PR Information
        lines.append("## PR INFORMATION")
        lines.append(f"**Title:** {pr_metadata.get('title', 'N/A')}")
        lines.append(f"**Author:** {pr_metadata.get('author', 'N/A')}")
        lines.append(f"**Branch:** {pr_metadata.get('head_branch', 'N/A')} → {pr_metadata.get('base_branch', 'N/A')}")
        lines.append(f"**State:** {pr_metadata.get('state', 'N/A')}")
        lines.append(f"**Labels:** {', '.join(pr_metadata.get('labels', [])) or 'None'}")
        lines.append("")

        # PR Description
        lines.append("## PR DESCRIPTION")
        description = pr_metadata.get("description", "No description provided")
        lines.append(description[:1000])  # Limit to 1000 chars
        lines.append("")

        # Acceptance Criteria
        if acceptance_criteria:
            lines.append("## ACCEPTANCE CRITERIA")
            for i, criterion in enumerate(acceptance_criteria, 1):
                lines.append(f"{i}. {criterion}")
            lines.append("")

        # Changed Files Summary
        lines.append("## CHANGED FILES")
        lines.append(f"**Total files changed:** {len(pr_files)}")
        lines.append("")

        for category, files in file_categories.items():
            category_display = category.replace("_", " ").title()
            lines.append(f"**{category_display}:** ({len(files)} files)")
            for file in files[:5]:  # Limit to 5 files per category
                lines.append(f"  - {file}")
            if len(files) > 5:
                lines.append(f"  ... and {len(files) - 5} more")
            lines.append("")

        # Codebase Context
        lines.append("## CODEBASE CONTEXT")
        lines.append(f"**Project Type:** {codebase_analysis.get('project_type', 'Unknown')}")
        lines.append(f"**Tech Stack:** {', '.join(codebase_analysis.get('tech_stack', [])) or 'Unknown'}")
        lines.append("")

        if codebase_analysis.get("readme", {}).get("project_description"):
            lines.append("**Project Description:**")
            lines.append(codebase_analysis["readme"]["project_description"][:500])
            lines.append("")

        # Deployment Information
        lines.append("## DEPLOYMENT INFORMATION")
        lines.append(f"**Deployment URL:** {deployment_url}")

        if deployment_info.get("validation"):
            validation = deployment_info["validation"]
            lines.append(f"**Status:** {'✅ Accessible' if validation.get('accessible') else '❌ Not Accessible'}")
            if validation.get("status_code"):
                lines.append(f"**HTTP Status:** {validation['status_code']}")
            if validation.get("response_time_ms"):
                lines.append(f"**Response Time:** {validation['response_time_ms']}ms")
        lines.append("")

        # Test Scenarios
        lines.append("## TEST SCENARIOS")
        for i, scenario in enumerate(test_scenarios, 1):
            lines.append(f"### Scenario {i}: {scenario['name']}")
            lines.append(f"**Priority:** {scenario['priority']}")
            lines.append(f"**Description:** {scenario['description']}")
            lines.append("**Steps:**")
            for step_num, step in enumerate(scenario.get('steps', []), 1):
                lines.append(f"  {step_num}. {step}")

            if scenario.get("acceptance_criteria"):
                lines.append("**Acceptance Criteria:**")
                for criterion in scenario["acceptance_criteria"]:
                    lines.append(f"  - {criterion}")

            if scenario.get("affected_files"):
                lines.append("**Affected Files:**")
                for file in scenario["affected_files"][:3]:
                    lines.append(f"  - {file}")

            lines.append("")

        # Testing Instructions
        lines.append("## TESTING INSTRUCTIONS")
        lines.append("1. Start by navigating to the deployment URL")
        lines.append("2. Execute each test scenario in priority order")
        lines.append("3. Document any failures or unexpected behavior")
        lines.append("4. Take screenshots of visual issues")
        lines.append("5. Check console for errors")
        lines.append("6. Test across multiple browsers if applicable")
        lines.append("7. Verify all acceptance criteria are met")
        lines.append("")

        lines.append("=" * 80)

        context_doc = "\n".join(lines)

        print(f"   ✅ Context document built ({len(context_doc)} characters)")
        print(f"   📋 Scenarios generated: {len(test_scenarios)}")
        print(f"   ✓  Acceptance criteria: {len(acceptance_criteria)}")

        return context_doc

    def build_agent_instructions(
        self,
        context_document: str,
        test_scenarios: List[Dict[str, Any]],
        deployment_url: str
    ) -> str:
        """
        Build specific instructions for the Playwright testing agent.

        Args:
            context_document: Full context document
            test_scenarios: Generated test scenarios
            deployment_url: Deployment URL

        Returns:
            Agent instructions string
        """
        instructions = []

        instructions.append(f"You are testing a GitHub Pull Request deployment at: {deployment_url}")
        instructions.append("")
        instructions.append("Your task is to:")
        instructions.append("1. Navigate to the deployment URL")
        instructions.append("2. Execute the test scenarios outlined below")
        instructions.append("3. Verify all acceptance criteria are met")
        instructions.append("4. Report any failures, errors, or issues found")
        instructions.append("5. Take screenshots of any visual problems")
        instructions.append("")

        instructions.append("TEST SCENARIOS TO EXECUTE:")
        instructions.append("")

        for i, scenario in enumerate(test_scenarios, 1):
            instructions.append(f"Scenario {i}: {scenario['name']} (Priority: {scenario['priority']})")
            instructions.append(f"Description: {scenario['description']}")
            instructions.append("Steps:")
            for step in scenario.get('steps', []):
                instructions.append(f"  - {step}")
            instructions.append("")

        instructions.append("IMPORTANT GUIDELINES:")
        instructions.append("- Be thorough but efficient")
        instructions.append("- Document all failures clearly")
        instructions.append("- Check for console errors")
        instructions.append("- Verify visual elements are rendered correctly")
        instructions.append("- Test interactive elements (buttons, forms, links)")
        instructions.append("- Report success or failure for each scenario")
        instructions.append("")

        instructions.append("After testing, provide a summary including:")
        instructions.append("- Total scenarios tested")
        instructions.append("- Pass/fail count")
        instructions.append("- List of failures with details")
        instructions.append("- Any recommendations or concerns")

        return "\n".join(instructions)
