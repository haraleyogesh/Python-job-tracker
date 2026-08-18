from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from datetime import datetime
from typing import Optional, Union

class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEWING = "Interviewing"
    OFFERED = "Offered"
    REJECTED = "Rejected"
    GHOSTED = "Ghosted"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return any(value.lower() == item.value.lower() for item in cls)

    @classmethod
    def get_match(cls, value: str) -> 'ApplicationStatus':
        for item in cls:
            if value.lower() == item.value.lower():
                return item
        raise ValueError(f"'{value}' is not a valid ApplicationStatus")

@dataclass
class JobApplication:
    company: str
    title: str
    id: Optional[str] = None
    status: Union[ApplicationStatus, str] = ApplicationStatus.APPLIED
    date_applied: Optional[str] = None
    salary: Optional[Union[float, int]] = None
    url: str = ""
    notes: str = ""
    last_updated: Optional[str] = None

    def __post_init__(self):
        # Generate an 8-character unique identifier if not provided
        if not self.id:
            self.id = str(uuid.uuid4())[:8]

        # Handle Date fields
        today = datetime.today().strftime("%Y-%m-%d")
        if not self.date_applied:
            self.date_applied = today
        if not self.last_updated:
            self.last_updated = today

        # Validate and convert string status to Enum
        if isinstance(self.status, str):
            try:
                self.status = ApplicationStatus.get_match(self.status)
            except ValueError:
                self.status = ApplicationStatus.APPLIED

        # Sanitize salary to float/int if possible
        if self.salary is not None:
            try:
                if isinstance(self.salary, str) and not self.salary.strip():
                    self.salary = None
                else:
                    # Convert to float or int as appropriate
                    val = float(self.salary)
                    self.salary = int(val) if val.is_integer() else val
            except (ValueError, TypeError):
                self.salary = None

    def to_dict(self) -> dict:
        """Serialize JobApplication to dictionary suitable for JSON storage."""
        data = asdict(self)
        # Ensure status is serialized as its string value
        data['status'] = self.status.value if isinstance(self.status, ApplicationStatus) else self.status
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'JobApplication':
        """Deserialize JobApplication from dictionary."""
        cleaned = dict(data)
        if 'status' in cleaned and cleaned['status']:
            cleaned['status'] = ApplicationStatus.get_match(cleaned['status'])
        return cls(**cleaned)
