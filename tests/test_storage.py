import unittest
import os
import tempfile
from job_tracker.models import JobApplication
from job_tracker.storage import JSONStorage

class TestJSONStorage(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for storage testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()  # Close so JSONStorage can write/read it
        self.storage = JSONStorage(self.temp_file.name)

    def tearDown(self):
        # Clean up temporary file
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_load_non_existent_file(self):
        """Test loading from a file that doesn't exist yet returns empty list."""
        non_existent_storage = JSONStorage("does_not_exist_12345.json")
        self.assertEqual(non_existent_storage.load_all(), [])

    def test_save_and_load_applications(self):
        """Test saving and loading multiple applications."""
        apps = [
            JobApplication(company="Google", title="SWE", salary=100000),
            JobApplication(company="Meta", title="PM", salary=120000, notes="Referral")
        ]
        self.storage.save_all(apps)

        loaded_apps = self.storage.load_all()
        self.assertEqual(len(loaded_apps), 2)
        self.assertEqual(loaded_apps[0].company, "Google")
        self.assertEqual(loaded_apps[0].title, "SWE")
        self.assertEqual(loaded_apps[0].salary, 100000)
        self.assertEqual(loaded_apps[1].company, "Meta")
        self.assertEqual(loaded_apps[1].notes, "Referral")
        self.assertEqual(loaded_apps[1].salary, 120000)

    def test_corrupted_json_handling(self):
        """Test that corrupted JSON files return an empty list rather than crashing."""
        with open(self.temp_file.name, "w", encoding="utf-8") as f:
            f.write("invalid json data {")

        self.assertEqual(self.storage.load_all(), [])
