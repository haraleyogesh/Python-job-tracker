import unittest
from datetime import datetime
from job_tracker.models import JobApplication, ApplicationStatus

class TestJobApplicationModel(unittest.TestCase):

    def test_default_initialization(self):
        """Test that a JobApplication initializes with correct defaults."""
        app = JobApplication(company="Google", title="Software Engineer")
        
        self.assertEqual(app.company, "Google")
        self.assertEqual(app.title, "Software Engineer")
        self.assertIsNotNone(app.id)
        self.assertEqual(len(app.id), 8)
        self.assertEqual(app.status, ApplicationStatus.APPLIED)
        
        today_str = datetime.today().strftime("%Y-%m-%d")
        self.assertEqual(app.date_applied, today_str)
        self.assertEqual(app.last_updated, today_str)
        self.assertIsNone(app.salary)
        self.assertEqual(app.url, "")
        self.assertEqual(app.notes, "")

    def test_status_case_insensitivity_and_matching(self):
        """Test that string status matches the enum correctly regardless of case."""
        app1 = JobApplication(company="Meta", title="Manager", status="interviewing")
        self.assertEqual(app1.status, ApplicationStatus.INTERVIEWING)

        app2 = JobApplication(company="Meta", title="Manager", status="OFFERED")
        self.assertEqual(app2.status, ApplicationStatus.OFFERED)

        # Test invalid status fallback
        app3 = JobApplication(company="Meta", title="Manager", status="NotAStatus")
        self.assertEqual(app3.status, ApplicationStatus.APPLIED)

    def test_salary_sanitization(self):
        """Test that salary values are converted to appropriate numerical types."""
        app1 = JobApplication(company="Apple", title="Analyst", salary=120000)
        self.assertEqual(app1.salary, 120000)

        app2 = JobApplication(company="Apple", title="Analyst", salary="130000.50")
        self.assertEqual(app2.salary, 130000.5)

        app3 = JobApplication(company="Apple", title="Analyst", salary="invalid")
        self.assertIsNone(app3.salary)

        app4 = JobApplication(company="Apple", title="Analyst", salary="")
        self.assertIsNone(app4.salary)

    def test_to_dict_and_from_dict(self):
        """Test serialization and deserialization routines."""
        original = JobApplication(
            company="Netflix",
            title="Senior Engineer",
            id="test-id",
            status=ApplicationStatus.OFFERED,
            date_applied="2026-01-01",
            salary=150000,
            url="https://netflix.jobs",
            notes="Ready to sign",
            last_updated="2026-01-02"
        )
        
        serialized = original.to_dict()
        
        self.assertEqual(serialized["company"], "Netflix")
        self.assertEqual(serialized["title"], "Senior Engineer")
        self.assertEqual(serialized["id"], "test-id")
        self.assertEqual(serialized["status"], "Offered")
        self.assertEqual(serialized["date_applied"], "2026-01-01")
        self.assertEqual(serialized["salary"], 150000)
        self.assertEqual(serialized["url"], "https://netflix.jobs")
        self.assertEqual(serialized["notes"], "Ready to sign")
        self.assertEqual(serialized["last_updated"], "2026-01-02")
        
        deserialized = JobApplication.from_dict(serialized)
        
        self.assertEqual(deserialized.company, original.company)
        self.assertEqual(deserialized.title, original.title)
        self.assertEqual(deserialized.id, original.id)
        self.assertEqual(deserialized.status, original.status)
        self.assertEqual(deserialized.date_applied, original.date_applied)
        self.assertEqual(deserialized.salary, original.salary)
        self.assertEqual(deserialized.url, original.url)
        self.assertEqual(deserialized.notes, original.notes)
        self.assertEqual(deserialized.last_updated, original.last_updated)

if __name__ == '__main__':
    unittest.main()
