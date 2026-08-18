from typing import List, Optional, Any
from datetime import datetime
from job_tracker.models import JobApplication, ApplicationStatus
from job_tracker.storage import JSONStorage

class JobTracker:
    def __init__(self, storage: JSONStorage):
        self.storage = storage

    def add_application(
        self,
        company: str,
        title: str,
        status: str = "Applied",
        salary: Optional[float] = None,
        url: str = "",
        notes: str = "",
        date_applied: Optional[str] = None
    ) -> JobApplication:
        """Adds a new job application and saves it."""
        apps = self.storage.load_all()

        new_app = JobApplication(
            company=company,
            title=title,
            status=status,
            salary=salary,
            url=url,
            notes=notes,
            date_applied=date_applied
        )

        apps.append(new_app)
        self.storage.save_all(apps)
        return new_app

    def get_application(self, app_id: str) -> Optional[JobApplication]:
        """Gets a job application by ID."""
        apps = self.storage.load_all()
        for app in apps:
            if app.id == app_id:
                return app
        return None

    def list_applications(
        self,
        status: Optional[str] = None,
        sort_by: Optional[str] = None,
        desc: bool = False
    ) -> List[JobApplication]:
        """Lists all job applications with optional status filter and sorting."""
        apps = self.storage.load_all()

        # Filter by status if provided
        if status:
            try:
                target_status = ApplicationStatus.get_match(status)
                apps = [app for app in apps if app.status == target_status]
            except ValueError:
                # If invalid status, return empty list
                return []

        # Sort if requested
        if sort_by:
            valid_sort_keys = ["company", "title", "status", "date_applied", "salary", "last_updated"]
            if sort_by in valid_sort_keys:
                def get_sort_val(app: JobApplication) -> Any:
                    val = getattr(app, sort_by)
                    if val is None:
                        # Return lower-bound value for proper sorting
                        return -1 if sort_by == "salary" else ""
                    if isinstance(val, ApplicationStatus):
                        return val.value
                    return val

                apps.sort(key=get_sort_val, reverse=desc)

        return apps

    def update_application(self, app_id: str, **kwargs) -> Optional[JobApplication]:
        """Updates specific fields of an application."""
        apps = self.storage.load_all()
        target_app = None

        for app in apps:
            if app.id == app_id:
                target_app = app
                break

        if not target_app:
            return None

        # Update allowed fields
        allowed_fields = ["company", "title", "status", "salary", "url", "notes", "date_applied"]
        updated_any = False

        for key, val in kwargs.items():
            if key in allowed_fields and val is not None:
                # Handle status specifically
                if key == "status":
                    try:
                        val = ApplicationStatus.get_match(val)
                    except ValueError:
                        continue  # Skip invalid status update
                setattr(target_app, key, val)
                updated_any = True

        if updated_any:
            target_app.last_updated = datetime.today().strftime("%Y-%m-%d")
            # If we changed some fields, post_init logic might be useful, let's run it again
            target_app.__post_init__()
            self.storage.save_all(apps)

        return target_app

    def delete_application(self, app_id: str) -> bool:
        """Deletes an application by ID."""
        apps = self.storage.load_all()
        initial_len = len(apps)

        apps = [app for app in apps if app.id != app_id]

        if len(apps) < initial_len:
            self.storage.save_all(apps)
            return True
        return False
