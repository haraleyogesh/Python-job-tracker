import json
import os
from typing import List
from job_tracker.models import JobApplication

class JSONStorage:
    def __init__(self, filepath: str = "job_applications.json"):
        self.filepath = filepath

    def load_all(self) -> List[JobApplication]:
        """Loads all job applications from the JSON file."""
        if not os.path.exists(self.filepath):
            return []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                if not isinstance(data, list):
                    return []
                return [JobApplication.from_dict(item) for item in data]
        except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
            # Return empty list if the file is empty or corrupted
            return []

    def save_all(self, applications: List[JobApplication]) -> None:
        """Saves all job applications to the JSON file."""
        parent_dir = os.path.dirname(self.filepath)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir, exist_ok=True)

        data = [app.to_dict() for app in applications]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
