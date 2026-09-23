import json
from pathlib import Path


SCENARIO_DIRECTORY = Path(__file__).resolve().parent.parent.parent / "scenarios


class ScenarioNotFoundError(Exception):
    """Raised when a requested scenario JSON file does not exist."""
    pass


class ScenarioChoiceError(Exception):
    """Raised when a selected choice_id does not exist on the given node."""
    pass


class ScenarioEngine:

    def list_scenarios(self) -> list:
        scenarios = []

        for file_path in sorted(SCENARIO_DIRECTORY.glob("*.json")):
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            scenarios.append({
                "id": data.get("id", file_path.stem),
                "title": data.get("title", file_path.stem),
                "category": data.get("category", ""),
                "description": data.get("description", ""),
            })

        return scenarios

    def load(self, scenario_id: str) -> dict:
        file_path = SCENARIO_DIRECTORY / f"{scenario_id}.json"

        if not file_path.exists():
            raise ScenarioNotFoundError(
                f"Scenario '{scenario_id}' was not found."
            )

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def get_start_node(self, scenario_id: str) -> dict:
        scenario = self.load(scenario_id)
        node_id = scenario["start_node"]

        return {
            "scenario_id": scenario_id,
            "node_id": node_id,
            "node": scenario["nodes"][node_id]
        }

    def choose(
        self,
        scenario_id: str,
        node_id: str,
        choice_id: str
    ) -> dict:
        scenario = self.load(scenario_id)
        node = scenario["nodes"][node_id]

        try:
            selected_choice = next(
                choice
                for choice in node["choices"]
                if choice["id"] == choice_id
            )
        except StopIteration:
            raise ScenarioChoiceError(
                f"Choice '{choice_id}' is not valid for node '{node_id}'."
            )

        next_node_id = selected_choice["next_node"]
        next_node = scenario["nodes"][next_node_id]

        return {
            "scenario_id": scenario_id,
            "node_id": next_node_id,
            "node": next_node,
            "points": selected_choice.get("points", 0),
            "feedback": selected_choice.get("feedback", ""),
            "is_end": not next_node.get("choices"),
        }
