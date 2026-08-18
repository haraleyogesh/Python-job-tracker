# Job Application Tracker

A clean, production-grade command-line interface (CLI) application in Python to track and analyze your job applications.

## Features
- Track companies, positions, dates applied, salaries, URLs, and custom notes.
- Manage application status (Applied, Interviewing, Offered, Rejected, Ghosted).
- CLI for fast interactions (CRUD).
- Analytical reports (success rates, total applications, charts/stats).
- Persistent JSON-based local database.

## Architecture
This project uses clean architecture separating storage, model representation, business logic, and CLI controls.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/haraleyogesh/Python-job-tracker.git
   cd Python-job-tracker
   ```
2. Setup virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
