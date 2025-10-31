"""
Persistence layer for TestGPT.

Stores and retrieves scenarios, test plans, and run artifacts.
Simple JSON file-based storage for now (can be upgraded to DB later).
"""

import json
import os
from datetime import datetime
from typing import List, Optional
from pathlib import Path
from models import ScenarioDefinition, RunArtifact, TestPlan
from dataclasses import asdict


class PersistenceLayer:
    """
    Handles storage and retrieval of scenarios and run artifacts.

    Uses JSON file storage by default, organized by:
    - scenarios/: Saved scenario definitions
    - runs/: Run artifacts
    - plans/: Test plans
    """

    def __init__(self, storage_dir: str = "./testgpt_data"):
        """
        Initialize persistence layer.

        Args:
            storage_dir: Base directory for storage
        """
        self.storage_dir = Path(storage_dir)
        self.scenarios_dir = self.storage_dir / "scenarios"
        self.runs_dir = self.storage_dir / "runs"
        self.plans_dir = self.storage_dir / "plans"

        # Create directories if they don't exist
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        self.runs_dir.mkdir(parents=True, exist_ok=True)
        self.plans_dir.mkdir(parents=True, exist_ok=True)

    # ========================================================================
    # SCENARIO PERSISTENCE
    # ========================================================================

    def save_scenario(self, scenario: ScenarioDefinition) -> bool:
        """
        Save a scenario definition.

        Args:
            scenario: ScenarioDefinition to save

        Returns:
            True if successful
        """
        try:
            file_path = self.scenarios_dir / f"{scenario.scenario_id}.json"

            # Convert to dict with datetime serialization
            scenario_dict = self._serialize_dataclass(scenario)

            with open(file_path, 'w') as f:
                json.dump(scenario_dict, f, indent=2, default=str)

            print(f"💾 Saved scenario: {scenario.scenario_id}")
            return True

        except Exception as e:
            print(f"❌ Error saving scenario: {str(e)}")
            return False

    def load_scenario(self, scenario_id: str) -> Optional[ScenarioDefinition]:
        """
        Load a scenario definition by ID.

        Args:
            scenario_id: ID of scenario to load

        Returns:
            ScenarioDefinition if found, None otherwise
        """
        try:
            file_path = self.scenarios_dir / f"{scenario_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r') as f:
                scenario_dict = json.load(f)

            # Note: Full deserialization would require reconstructing dataclass
            # For now, return as dict (can be upgraded)
            return scenario_dict

        except Exception as e:
            print(f"❌ Error loading scenario: {str(e)}")
            return None

    def find_scenarios_by_name(self, name_pattern: str) -> List[str]:
        """
        Find scenario IDs matching a name pattern.

        Args:
            name_pattern: Pattern to match (case-insensitive)

        Returns:
            List of matching scenario IDs
        """
        matching_ids = []
        pattern_lower = name_pattern.lower()

        try:
            for file_path in self.scenarios_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    scenario_dict = json.load(f)

                scenario_name = scenario_dict.get("scenario_name", "").lower()

                if pattern_lower in scenario_name:
                    matching_ids.append(scenario_dict.get("scenario_id"))

        except Exception as e:
            print(f"❌ Error searching scenarios: {str(e)}")

        return matching_ids

    def find_scenarios_by_url(self, url_pattern: str) -> List[str]:
        """
        Find scenario IDs matching a URL pattern.

        Args:
            url_pattern: URL pattern to match

        Returns:
            List of matching scenario IDs
        """
        matching_ids = []
        pattern_lower = url_pattern.lower()

        try:
            for file_path in self.scenarios_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    scenario_dict = json.load(f)

                target_url = scenario_dict.get("target_url", "").lower()

                if pattern_lower in target_url:
                    matching_ids.append(scenario_dict.get("scenario_id"))

        except Exception as e:
            print(f"❌ Error searching scenarios: {str(e)}")

        return matching_ids

    def list_all_scenarios(self) -> List[dict]:
        """
        List all saved scenarios.

        Returns:
            List of scenario summary dicts
        """
        scenarios = []

        try:
            for file_path in self.scenarios_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    scenario_dict = json.load(f)

                scenarios.append({
                    "scenario_id": scenario_dict.get("scenario_id"),
                    "scenario_name": scenario_dict.get("scenario_name"),
                    "target_url": scenario_dict.get("target_url"),
                    "created_at": scenario_dict.get("created_at"),
                    "tags": scenario_dict.get("tags", [])
                })

        except Exception as e:
            print(f"❌ Error listing scenarios: {str(e)}")

        return scenarios

    # ========================================================================
    # RUN ARTIFACT PERSISTENCE
    # ========================================================================

    def save_run_artifact(self, run_artifact: RunArtifact) -> bool:
        """
        Save a run artifact.

        Args:
            run_artifact: RunArtifact to save

        Returns:
            True if successful
        """
        try:
            file_path = self.runs_dir / f"{run_artifact.run_id}.json"

            # Convert to dict with datetime serialization
            artifact_dict = self._serialize_dataclass(run_artifact)

            with open(file_path, 'w') as f:
                json.dump(artifact_dict, f, indent=2, default=str)

            print(f"💾 Saved run artifact: {run_artifact.run_id}")
            return True

        except Exception as e:
            print(f"❌ Error saving run artifact: {str(e)}")
            return False

    def load_run_artifact(self, run_id: str) -> Optional[dict]:
        """
        Load a run artifact by ID.

        Args:
            run_id: ID of run to load

        Returns:
            Run artifact dict if found, None otherwise
        """
        try:
            file_path = self.runs_dir / f"{run_id}.json"

            if not file_path.exists():
                return None

            with open(file_path, 'r') as f:
                artifact_dict = json.load(f)

            return artifact_dict

        except Exception as e:
            print(f"❌ Error loading run artifact: {str(e)}")
            return None

    def get_latest_run_for_scenario(self, scenario_id: str) -> Optional[dict]:
        """
        Get the most recent run for a scenario.

        Args:
            scenario_id: Scenario ID

        Returns:
            Latest run artifact dict if found, None otherwise
        """
        try:
            matching_runs = []

            for file_path in self.runs_dir.glob("*.json"):
                with open(file_path, 'r') as f:
                    artifact_dict = json.load(f)

                if artifact_dict.get("scenario_id") == scenario_id:
                    matching_runs.append(artifact_dict)

            if not matching_runs:
                return None

            # Sort by completed_at timestamp
            matching_runs.sort(
                key=lambda r: r.get("completed_at", ""),
                reverse=True
            )

            return matching_runs[0]

        except Exception as e:
            print(f"❌ Error finding latest run: {str(e)}")
            return None

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def _serialize_dataclass(self, obj):
        """
        Recursively serialize a dataclass to dict.

        Handles nested dataclasses, lists, enums, and datetime objects.
        """
        if hasattr(obj, '__dataclass_fields__'):
            # It's a dataclass
            result = {}
            for field_name, field_value in asdict(obj).items():
                result[field_name] = self._serialize_value(field_value)
            return result
        else:
            return self._serialize_value(obj)

    def _serialize_value(self, value):
        """Serialize a single value."""
        if isinstance(value, datetime):
            return value.isoformat()
        elif isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif hasattr(value, 'value'):  # Enum
            return value.value
        elif hasattr(value, '__dataclass_fields__'):  # Nested dataclass
            return self._serialize_dataclass(value)
        else:
            return value

    def update_scenario_last_run(self, scenario_id: str, run_timestamp: datetime) -> bool:
        """
        Update the last_run_at timestamp for a scenario.

        Args:
            scenario_id: ID of scenario to update
            run_timestamp: Timestamp of the run

        Returns:
            True if successful
        """
        try:
            scenario_dict = self.load_scenario(scenario_id)

            if not scenario_dict:
                return False

            scenario_dict["last_run_at"] = run_timestamp.isoformat()

            file_path = self.scenarios_dir / f"{scenario_id}.json"
            with open(file_path, 'w') as f:
                json.dump(scenario_dict, f, indent=2)

            return True

        except Exception as e:
            print(f"❌ Error updating scenario: {str(e)}")
            return False
