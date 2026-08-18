import unittest
import tempfile
import os
from job_tracker.models import JobApplication, ApplicationStatus
from job_tracker.storage import JSONStorage
from job_tracker.core import JobTracker

class TestJobTrackerCore(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.temp_file.close()
        self.storage = JSONStorage(self.temp_file.name)
        self.tracker = JobTracker(self.storage)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_add_and_get_application(self):
        """Test adding and retrieving applications."""
        app = self.tracker.add_application(
            company="Google",
            title="SWE",
            status="applied",
            salary=120000,
            url="https://google.com/jobs",
            notes="Requires preparation"
        )

        self.assertEqual(app.company, "Google")
        self.assertEqual(app.title, "SWE")
        self.assertEqual(app.status, ApplicationStatus.APPLIED)
        self.assertEqual(app.salary, 120000)
        self.assertEqual(app.url, "https://google.com/jobs")
        self.assertEqual(app.notes, "Requires preparation")

        fetched = self.tracker.get_application(app.id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.company, "Google")
        self.assertEqual(fetched.id, app.id)

    def test_list_applications_filtering_and_sorting(self):
        """Test listing, filtering by status, and sorting by attributes."""
        self.tracker.add_application("Apple", "Designer", "interviewing", salary=90000)
        self.tracker.add_application("Microsoft", "Developer", "applied", salary=110000)
        self.tracker.add_application("Netflix", "Manager", "interviewing", salary=150000)

        # Test basic list
        all_apps = self.tracker.list_applications()
        self.assertEqual(len(all_apps), 3)

        # Test status filtering
        interviewing = self.tracker.list_applications(status="interviewing")
        self.assertEqual(len(interviewing), 2)
        self.assertTrue(all(app.status == ApplicationStatus.INTERVIEWING for app in interviewing))

        # Test sorting by salary ascending
        sorted_salary = self.tracker.list_applications(sort_by="salary")
        self.assertEqual(sorted_salary[0].company, "Apple")      # 90k
        self.assertEqual(sorted_salary[1].company, "Microsoft")  # 110k
        self.assertEqual(sorted_salary[2].company, "Netflix")    # 150k

        # Test sorting by salary descending
        sorted_salary_desc = self.tracker.list_applications(sort_by="salary", desc=True)
        self.assertEqual(sorted_salary_desc[0].company, "Netflix")    # 150k
        self.assertEqual(sorted_salary_desc[1].company, "Microsoft")  # 110k
        self.assertEqual(sorted_salary_desc[2].company, "Apple")      # 90k

    def test_update_application(self):
        """Test updating application details."""
        app = self.tracker.add_application("Amazon", "SDE", salary=95000)

        updated = self.tracker.update_application(
            app.id,
            company="Amazon Web Services",
            status="offered",
            salary=130000,
            notes="Offer received!"
        )

        self.assertIsNotNone(updated)
        self.assertEqual(updated.company, "Amazon Web Services")
        self.assertEqual(updated.status, ApplicationStatus.OFFERED)
        self.assertEqual(updated.salary, 130000)
        self.assertEqual(updated.notes, "Offer received!")

        # Verify persistence
        fetched = self.tracker.get_application(app.id)
        self.assertEqual(fetched.company, "Amazon Web Services")

    def test_delete_application(self):
        """Test deleting applications."""
        app1 = self.tracker.add_application("Google", "SWE")
        app2 = self.tracker.add_application("Apple", "Designer")

        self.assertEqual(len(self.tracker.list_applications()), 2)

        deleted = self.tracker.delete_application(app1.id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.tracker.list_applications()), 1)
        self.assertIsNone(self.tracker.get_application(app1.id))

        # Delete invalid ID
        deleted_invalid = self.tracker.delete_application("non-existent-id")
        self.assertFalse(deleted_invalid)

    def test_statistics(self):
        """Test calculation of statistics."""
        # Stats on empty database
        stats = self.tracker.get_statistics()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["salary"]["total_counted"], 0)

        # Add applications with varying details
        self.tracker.add_application("Company A", "Role A", "applied", salary=100000)
        self.tracker.add_application("Company B", "Role B", "interviewing", salary=120000)
        self.tracker.add_application("Company C", "Role C", "offered", salary=150000)
        self.tracker.add_application("Company D", "Role D", "rejected") # No salary
        self.tracker.add_application("Company E", "Role E", "offered", salary=170000)

        stats = self.tracker.get_statistics()
        self.assertEqual(stats["total"], 5)
        self.assertEqual(stats["by_status"]["Applied"], 1)
        self.assertEqual(stats["by_status"]["Interviewing"], 1)
        self.assertEqual(stats["by_status"]["Offered"], 2)
        self.assertEqual(stats["by_status"]["Rejected"], 1)

        # Percentages (out of 5)
        self.assertEqual(stats["percentages"]["Applied"], 20.0)
        self.assertEqual(stats["percentages"]["Offered"], 40.0)

        # Salary stats (4 with salary)
        self.assertEqual(stats["salary"]["total_counted"], 4)
        self.assertEqual(stats["salary"]["min"], 100000)
        self.assertEqual(stats["salary"]["max"], 170000)
        self.assertEqual(stats["salary"]["avg"], 135000.0)  # (100+120+150+170)/4 = 135

        # Offered salary stats (2 with salary)
        self.assertEqual(stats["offered_salary"]["total_counted"], 2)
        self.assertEqual(stats["offered_salary"]["min"], 150000)
        self.assertEqual(stats["offered_salary"]["max"], 170000)
        self.assertEqual(stats["offered_salary"]["avg"], 160000.0)
