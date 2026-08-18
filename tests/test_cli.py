import unittest
from unittest.mock import patch
import io
import os
import tempfile
from job_tracker.cli import main

class TestJobTrackerCLI(unittest.TestCase):
    def setUp(self):
        # Setup temporary database path
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_db.close()
        self.patcher = patch.dict(os.environ, {"JOB_TRACKER_DB": self.temp_db.name})
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        if os.path.exists(self.temp_db.name):
            os.remove(self.temp_db.name)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_cli_add_and_list(self, mock_stdout):
        # Run ADD command
        main(["add", "-c", "Google", "-t", "SWE", "-sal", "140000"])
        output = mock_stdout.getvalue()
        self.assertIn("Successfully added application", output)
        self.assertIn("Google", output)

        # Clear stdout buffer
        mock_stdout.seek(0)
        mock_stdout.truncate(0)

        # Run LIST command
        main(["list"])
        output = mock_stdout.getvalue()
        self.assertIn("Google", output)
        self.assertIn("SWE", output)
        self.assertIn("$140,000.00", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_cli_update_and_delete(self, mock_stdout):
        # Add an application to get ID
        from job_tracker.storage import JSONStorage
        from job_tracker.core import JobTracker
        storage = JSONStorage(self.temp_db.name)
        tracker = JobTracker(storage)
        app = tracker.add_application("Apple", "Designer")

        # Update via CLI
        main(["update", app.id, "-c", "Apple Inc.", "-s", "Interviewing"])
        output = mock_stdout.getvalue()
        self.assertIn(f"Successfully updated application ID: {app.id}", output)

        mock_stdout.seek(0)
        mock_stdout.truncate(0)

        # Check list showing the update
        main(["list"])
        output = mock_stdout.getvalue()
        self.assertIn("Apple Inc.", output)
        self.assertIn("Interviewing", output)

        mock_stdout.seek(0)
        mock_stdout.truncate(0)

        # Delete application
        main(["delete", app.id])
        output = mock_stdout.getvalue()
        self.assertIn(f"Successfully deleted application ID: {app.id}", output)

    @patch('sys.stdout', new_callable=io.StringIO)
    def test_cli_stats(self, mock_stdout):
        # Add applications
        main(["add", "-c", "Google", "-t", "SWE", "-sal", "100000"])
        main(["add", "-c", "Meta", "-t", "PM", "-sal", "120000", "-s", "Offered"])

        mock_stdout.seek(0)
        mock_stdout.truncate(0)

        # Run STATS command
        main(["stats"])
        output = mock_stdout.getvalue()
        self.assertIn("Total Applications: 2", output)
        self.assertIn("Average Salary   : $110,000.00", output)
        self.assertIn("Average Offered  : $120,000.00", output)
