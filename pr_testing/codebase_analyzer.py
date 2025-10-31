"""
Codebase Analyzer for PR Testing.

Analyzes repository structure to understand:
- Technology stack
- Project type (frontend, backend, fullstack)
- Key files and configurations
- Testing commands
- Build instructions
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import httpx


class CodebaseAnalyzer:
    """
    Analyzes codebase structure from GitHub repository.

    Extracts information from:
    - README.md
    - package.json / package-lock.json
    - requirements.txt / pyproject.toml
    - Dockerfile / docker-compose.yml
    - Configuration files
    """

    def __init__(self):
        """Initialize codebase analyzer."""
        pass

    async def fetch_file_from_github(
        self,
        owner: str,
        repo: str,
        branch: str,
        file_path: str,
        github_token: Optional[str] = None
    ) -> Optional[str]:
        """
        Fetch a file from GitHub repository.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch name
            file_path: Path to file
            github_token: GitHub token for authentication

        Returns:
            File content as string, or None if not found
        """
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": branch}

        headers = {
            "Accept": "application/vnd.github.v3.raw",
            "User-Agent": "TestGPT-PR-Tester"
        }

        if github_token:
            headers["Authorization"] = f"token {github_token}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                if response.status_code == 200:
                    return response.text
                return None

        except Exception as e:
            print(f"   ℹ️  Could not fetch {file_path}: {e}")
            return None

    def analyze_readme(self, readme_content: str) -> Dict[str, Any]:
        """
        Analyze README.md to extract project information.

        Args:
            readme_content: README.md file content

        Returns:
            Dict with extracted information
        """
        if not readme_content:
            return {}

        analysis = {
            "project_description": "",
            "tech_stack": [],
            "installation_steps": [],
            "environment_variables": [],
            "run_commands": [],
            "test_commands": [],
            "build_commands": [],
            "sections": {}
        }

        lines = readme_content.split("\n")

        current_section = None
        current_code_block = []
        in_code_block = False

        for line in lines:
            # Detect sections (# Header)
            if line.startswith("#"):
                section_name = line.lstrip("#").strip()
                current_section = section_name.lower()
                analysis["sections"][current_section] = []

            # Detect code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                if not in_code_block and current_code_block:
                    # End of code block - analyze commands
                    self._extract_commands_from_code_block(current_code_block, analysis)
                    current_code_block = []
                continue

            if in_code_block:
                current_code_block.append(line)

            # Store content in sections
            if current_section and not in_code_block:
                analysis["sections"][current_section].append(line)

        # Extract project description (first paragraph)
        for section_lines in analysis["sections"].values():
            text = " ".join(section_lines).strip()
            if text and len(text) > 20:
                analysis["project_description"] = text[:500]  # First 500 chars
                break

        # Detect tech stack from content
        tech_keywords = {
            "Next.js": ["next.js", "nextjs", "next dev"],
            "React": ["react", "create-react-app", "react app"],
            "Vue": ["vue", "vue-cli", "nuxt"],
            "Angular": ["angular", "@angular"],
            "FastAPI": ["fastapi", "uvicorn"],
            "Express": ["express", "express.js"],
            "Django": ["django", "manage.py"],
            "Flask": ["flask"],
            "TypeScript": ["typescript", ".ts", ".tsx"],
            "Python": ["python", ".py", "pip install"],
            "Node.js": ["node", "npm", "yarn"],
            "Docker": ["docker", "docker-compose"],
            "PostgreSQL": ["postgres", "postgresql"],
            "MongoDB": ["mongodb", "mongo"],
            "Redis": ["redis"],
        }

        readme_lower = readme_content.lower()
        for tech, keywords in tech_keywords.items():
            if any(keyword in readme_lower for keyword in keywords):
                analysis["tech_stack"].append(tech)

        return analysis

    def _extract_commands_from_code_block(self, code_block: List[str], analysis: Dict[str, Any]):
        """
        Extract commands from a code block.

        Args:
            code_block: Lines in code block
            analysis: Analysis dict to update
        """
        for line in code_block:
            line = line.strip()

            # Installation commands
            if any(cmd in line for cmd in ["npm install", "yarn install", "pip install", "poetry install"]):
                analysis["installation_steps"].append(line)

            # Run commands
            if any(cmd in line for cmd in ["npm run", "npm start", "yarn dev", "yarn start", "python", "uvicorn", "gunicorn"]):
                analysis["run_commands"].append(line)

            # Test commands
            if any(cmd in line for cmd in ["npm test", "yarn test", "pytest", "jest", "vitest"]):
                analysis["test_commands"].append(line)

            # Build commands
            if any(cmd in line for cmd in ["npm run build", "yarn build", "docker build"]):
                analysis["build_commands"].append(line)

            # Environment variables
            if "=" in line and any(prefix in line for prefix in ["export ", "ENV ", "NEXT_PUBLIC_", "REACT_APP_"]):
                env_var = line.split("=")[0].strip().replace("export ", "").replace("ENV ", "")
                analysis["environment_variables"].append(env_var)

    def analyze_package_json(self, package_json_content: str) -> Dict[str, Any]:
        """
        Analyze package.json for Node.js projects.

        Args:
            package_json_content: package.json file content

        Returns:
            Dict with project information
        """
        if not package_json_content:
            return {}

        try:
            package_data = json.loads(package_json_content)

            analysis = {
                "name": package_data.get("name", ""),
                "version": package_data.get("version", ""),
                "description": package_data.get("description", ""),
                "scripts": package_data.get("scripts", {}),
                "dependencies": list(package_data.get("dependencies", {}).keys()),
                "dev_dependencies": list(package_data.get("devDependencies", {}).keys()),
                "engines": package_data.get("engines", {}),
            }

            # Detect framework from dependencies
            deps = analysis["dependencies"]
            if "next" in deps:
                analysis["framework"] = "Next.js"
            elif "react" in deps and "react-scripts" in deps:
                analysis["framework"] = "Create React App"
            elif "react" in deps:
                analysis["framework"] = "React"
            elif "vue" in deps:
                analysis["framework"] = "Vue"
            elif "@angular/core" in deps:
                analysis["framework"] = "Angular"
            elif "express" in deps:
                analysis["framework"] = "Express"
            else:
                analysis["framework"] = "Node.js"

            # Extract common scripts
            scripts = analysis["scripts"]
            analysis["dev_command"] = scripts.get("dev") or scripts.get("start") or "npm start"
            analysis["build_command"] = scripts.get("build", "npm run build")
            analysis["test_command"] = scripts.get("test", "npm test")

            return analysis

        except json.JSONDecodeError:
            return {"error": "Invalid package.json"}

    def analyze_requirements_txt(self, requirements_content: str) -> Dict[str, Any]:
        """
        Analyze requirements.txt for Python projects.

        Args:
            requirements_content: requirements.txt file content

        Returns:
            Dict with project information
        """
        if not requirements_content:
            return {}

        lines = requirements_content.strip().split("\n")
        dependencies = []

        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                # Extract package name (before version specifier)
                pkg_name = re.split(r'[>=<\[]', line)[0].strip()
                dependencies.append(pkg_name)

        analysis = {
            "dependencies": dependencies,
            "install_command": "pip install -r requirements.txt"
        }

        # Detect framework
        if "fastapi" in dependencies:
            analysis["framework"] = "FastAPI"
            analysis["run_command"] = "uvicorn main:app --reload"
        elif "flask" in dependencies:
            analysis["framework"] = "Flask"
            analysis["run_command"] = "python app.py"
        elif "django" in dependencies:
            analysis["framework"] = "Django"
            analysis["run_command"] = "python manage.py runserver"
        else:
            analysis["framework"] = "Python"

        # Check for testing frameworks
        if "pytest" in dependencies:
            analysis["test_command"] = "pytest"
        elif "unittest" in dependencies:
            analysis["test_command"] = "python -m unittest"

        return analysis

    async def analyze_repository(
        self,
        owner: str,
        repo: str,
        branch: str,
        github_token: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze complete repository structure.

        This is the main entry point for codebase analysis.

        Args:
            owner: Repository owner
            repo: Repository name
            branch: Branch to analyze
            github_token: GitHub token

        Returns:
            Complete codebase analysis
        """
        print(f"\n📚 Analyzing codebase structure...")

        analysis = {
            "repository": f"{owner}/{repo}",
            "branch": branch,
            "readme": {},
            "package_json": {},
            "requirements_txt": {},
            "project_type": "unknown",
            "tech_stack": [],
            "recommended_commands": {}
        }

        # Fetch and analyze README
        readme_content = await self.fetch_file_from_github(owner, repo, branch, "README.md", github_token)
        if readme_content:
            print(f"   ✅ Found README.md")
            analysis["readme"] = self.analyze_readme(readme_content)
            analysis["tech_stack"].extend(analysis["readme"].get("tech_stack", []))

        # Fetch and analyze package.json
        package_json_content = await self.fetch_file_from_github(owner, repo, branch, "package.json", github_token)
        if package_json_content:
            print(f"   ✅ Found package.json")
            analysis["package_json"] = self.analyze_package_json(package_json_content)
            analysis["project_type"] = "frontend" if "next" in analysis["package_json"].get("dependencies", []) else "fullstack"

            if analysis["package_json"].get("framework"):
                analysis["tech_stack"].append(analysis["package_json"]["framework"])

        # Fetch and analyze requirements.txt
        requirements_content = await self.fetch_file_from_github(owner, repo, branch, "requirements.txt", github_token)
        if requirements_content:
            print(f"   ✅ Found requirements.txt")
            analysis["requirements_txt"] = self.analyze_requirements_txt(requirements_content)

            if analysis["project_type"] == "unknown":
                analysis["project_type"] = "backend"

            if analysis["requirements_txt"].get("framework"):
                analysis["tech_stack"].append(analysis["requirements_txt"]["framework"])

        # Determine project type
        if analysis["package_json"] and analysis["requirements_txt"]:
            analysis["project_type"] = "fullstack"
        elif analysis["package_json"]:
            analysis["project_type"] = "frontend"
        elif analysis["requirements_txt"]:
            analysis["project_type"] = "backend"

        # Build recommended commands
        if analysis["package_json"]:
            analysis["recommended_commands"]["install"] = "npm install"
            analysis["recommended_commands"]["dev"] = analysis["package_json"].get("dev_command", "npm start")
            analysis["recommended_commands"]["build"] = analysis["package_json"].get("build_command", "npm run build")
            analysis["recommended_commands"]["test"] = analysis["package_json"].get("test_command", "npm test")

        if analysis["requirements_txt"]:
            analysis["recommended_commands"]["install"] = "pip install -r requirements.txt"
            analysis["recommended_commands"]["run"] = analysis["requirements_txt"].get("run_command", "python app.py")
            analysis["recommended_commands"]["test"] = analysis["requirements_txt"].get("test_command", "pytest")

        # Remove duplicates from tech stack
        analysis["tech_stack"] = list(set(analysis["tech_stack"]))

        print(f"   📋 Project Type: {analysis['project_type']}")
        print(f"   🛠️  Tech Stack: {', '.join(analysis['tech_stack']) if analysis['tech_stack'] else 'Unknown'}")

        return analysis

    def get_test_focus_areas(self, pr_files: List[Dict[str, Any]], codebase_analysis: Dict[str, Any]) -> List[str]:
        """
        Determine what areas to focus on for testing based on changed files.

        Args:
            pr_files: List of files changed in PR
            codebase_analysis: Codebase analysis result

        Returns:
            List of focus areas for testing
        """
        focus_areas = []

        # Categorize changed files
        ui_files = []
        api_files = []
        db_files = []
        config_files = []
        test_files = []

        for file_info in pr_files:
            filename = file_info["filename"]

            # UI components
            if any(ext in filename for ext in [".tsx", ".jsx", ".vue", ".svelte", "components/"]):
                ui_files.append(filename)

            # API/Backend
            if any(pattern in filename for pattern in ["api/", "routes/", "endpoints/", "views.py", "controllers/"]):
                api_files.append(filename)

            # Database
            if any(pattern in filename for pattern in ["models/", "schema", "migrations/", "db/"]):
                db_files.append(filename)

            # Config
            if any(ext in filename for ext in [".config", ".json", ".yml", ".yaml", ".env"]):
                config_files.append(filename)

            # Tests
            if any(pattern in filename for pattern in ["test", "spec", "__tests__"]):
                test_files.append(filename)

        # Build focus areas
        if ui_files:
            focus_areas.append(f"UI Components ({len(ui_files)} files changed)")

        if api_files:
            focus_areas.append(f"API Endpoints ({len(api_files)} files changed)")

        if db_files:
            focus_areas.append(f"Database Schema ({len(db_files)} files changed)")

        if config_files:
            focus_areas.append(f"Configuration ({len(config_files)} files changed)")

        return focus_areas if focus_areas else ["General functionality"]
