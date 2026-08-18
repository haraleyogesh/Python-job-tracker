# Job Application Tracker

A clean, production-grade command-line interface (CLI) application written in Python to track, manage, and analyze your job search. It utilizes a clean project architecture, is written entirely in the Python standard library for zero-dependency portability, and includes a comprehensive test suite.

---

## Features

- **Track Essential Fields**: Keep record of Company, Position Title, Application Status, Salary, Job Description URL, and custom Notes.
- **Application Status Options**: Track applications through stages: `Applied`, `Interviewing`, `Offered`, `Rejected`, `Ghosted`.
- **Flexible Listing**: List job applications in a clean terminal table with options to filter by status and sort by company, title, status, date applied, salary, or last updated.
- **Statistics Dashboard**: Analyze your job search progress with application status rates and salary analytics (Min, Max, Average overall and for offers).
- **Local Persistence**: Saves all records to a local JSON file (`job_applications.json`), making backups and modifications easy.

---

## Project Structure

```
.
├── job_tracker/
│   ├── __init__.py
│   ├── models.py      # Dataclasses & Enums (JobApplication, ApplicationStatus)
│   ├── storage.py     # Data Persistence Layer (JSONStorage)
│   ├── core.py        # Business Logic & CRUD Operations (JobTracker)
│   └── cli.py         # CLI Controller (Argparse commands)
├── tests/
│   ├── __init__.py
│   ├── test_models.py # Unit tests for models.py
│   ├── test_storage.py# Unit tests for storage.py
│   ├── test_core.py   # Unit tests for core.py (CRUD & statistics)
│   └── test_cli.py    # Integration/CLI tests
├── .gitignore
├── README.md
├── requirements.txt
└── main.py            # CLI entry point
```

---

## Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/haraleyogesh/Python-job-tracker.git
   cd Python-job-tracker
   ```

2. **Set up a Virtual Environment**:
   ```bash
   python -m venv venv
   # On Windows (PowerShell/CMD):
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   Although the core application runs entirely on Python's standard library, `pytest` is included for dev testing:
   ```bash
   pip install -r requirements.txt
   ```

---

## Running the CLI Application

Execute commands via `python main.py`.

### 1. Add a Job Application
Add a new application with the `--company` / `-c` and `--title` / `-t` parameters (required). Other details are optional.
```bash
python main.py add -c Google -t "Software Engineer" -sal 140000 -u "https://google.com/jobs" -n "Referral from John"
```

### 2. List Applications
Display your applications in a formatted table.
```bash
python main.py list
```

**Filter by status:**
```bash
python main.py list -s Interviewing
```

**Sort results:**
Sort by fields such as `salary`, `company`, `title`, `status`, `date_applied`, or `last_updated` using `--sort` (optionally `--desc` for descending order).
```bash
python main.py list --sort salary --desc
```

### 3. Update an Application
Modify details of an application using its 8-character unique ID.
```bash
python main.py update 2ad22f7e -s Offered -sal 155000 -n "Negotiating offer details"
```

### 4. Delete an Application
Remove a job application permanently.
```bash
python main.py delete 2ad22f7e
```

### 5. Statistics Dashboard
Show metrics, status breakdown percentages, and salary statistics.
```bash
python main.py stats
```
*Output Example:*
```text
========================================
     JOB APPLICATION TRACKER DASHBOARD
========================================
Total Applications: 5
----------------------------------------
Applications by Status:
  - Applied        :   2 (40.0%)
  - Interviewing   :   1 (20.0%)
  - Offered        :   1 (20.0%)
  - Rejected       :   1 (20.0%)
  - Ghosted        :   0 (0.0%)
----------------------------------------
Salary Overview:
  - Min Salary       : $90,000.00
  - Max Salary       : $155,000.00
  - Average Salary   : $122,500.00
----------------------------------------
Offered Salary Overview:
  - Min Offered      : $155,000.00
  - Max Offered      : $155,000.00
  - Average Offered  : $155,000.00
========================================
```

---

## Running Tests

To run the complete test suite (unit and integration tests), run:
```bash
python -m unittest discover -s tests
```
Or, if you installed `pytest`:
```bash
pytest tests/
```
