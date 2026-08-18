import argparse
import sys
import os
from job_tracker.models import ApplicationStatus
from job_tracker.storage import JSONStorage
from job_tracker.core import JobTracker

def print_table(headers, rows):
    if not rows:
        print("No job applications found.")
        return

    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val if val is not None else "")))

    # Format templates
    fmt = " | ".join(f"{{:<{w}}}" for w in widths)
    sep = "-+-".join("-" * w for w in widths)

    # Print table
    print(fmt.format(*headers))
    print(sep)
    for row in rows:
        print(fmt.format(*(str(val if val is not None else "") for val in row)))

def get_db_path() -> str:
    return os.environ.get("JOB_TRACKER_DB", "job_applications.json")

def main(args=None):
    parser = argparse.ArgumentParser(
        description="Job Application Tracker CLI - track and manage your job search."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add Command
    add_parser = subparsers.add_parser("add", help="Add a new job application")
    add_parser.add_argument("-c", "--company", required=True, help="Company name")
    add_parser.add_argument("-t", "--title", required=True, help="Job title")
    add_parser.add_argument("-s", "--status", default="Applied", choices=[s.value for s in ApplicationStatus], help="Application status (default: Applied)")
    add_parser.add_argument("-sal", "--salary", type=float, help="Salary (numerical)")
    add_parser.add_argument("-u", "--url", default="", help="Job posting URL")
    add_parser.add_argument("-n", "--notes", default="", help="Notes/Comments")
    add_parser.add_argument("-d", "--date", help="Date applied (YYYY-MM-DD, default: today)")

    # List Command
    list_parser = subparsers.add_parser("list", help="List job applications")
    list_parser.add_argument("-s", "--status", choices=[s.value for s in ApplicationStatus], help="Filter by status")
    list_parser.add_argument("--sort", choices=["company", "title", "status", "date_applied", "salary", "last_updated"], help="Field to sort by")
    list_parser.add_argument("--desc", action="store_true", help="Sort in descending order")

    # Update Command
    update_parser = subparsers.add_parser("update", help="Update an existing job application")
    update_parser.add_argument("id", help="8-character unique application ID")
    update_parser.add_argument("-c", "--company", help="Update company name")
    update_parser.add_argument("-t", "--title", help="Update job title")
    update_parser.add_argument("-s", "--status", choices=[s.value for s in ApplicationStatus], help="Update application status")
    update_parser.add_argument("-sal", "--salary", type=float, help="Update salary")
    update_parser.add_argument("-u", "--url", help="Update job posting URL")
    update_parser.add_argument("-n", "--notes", help="Update notes")
    update_parser.add_argument("-d", "--date", help="Update date applied (YYYY-MM-DD)")

    # Delete Command
    delete_parser = subparsers.add_parser("delete", help="Delete a job application")
    delete_parser.add_argument("id", help="8-character unique application ID")

    # Stats Command
    subparsers.add_parser("stats", help="Show application statistics and dashboard")

    parsed_args = parser.parse_args(args)

    # Initialize components
    db_path = get_db_path()
    storage = JSONStorage(db_path)
    tracker = JobTracker(storage)

    if parsed_args.command == "add":
        app = tracker.add_application(
            company=parsed_args.company,
            title=parsed_args.title,
            status=parsed_args.status,
            salary=parsed_args.salary,
            url=parsed_args.url,
            notes=parsed_args.notes,
            date_applied=parsed_args.date
        )
        print(f"Successfully added application: {app.title} at {app.company} (ID: {app.id})")

    elif parsed_args.command == "list":
        apps = tracker.list_applications(
            status=parsed_args.status,
            sort_by=parsed_args.sort,
            desc=parsed_args.desc
        )

        headers = ["ID", "Company", "Title", "Status", "Date Applied", "Salary", "Last Updated"]
        rows = []
        for app in apps:
            salary_str = f"${app.salary:,.2f}" if app.salary is not None else "N/A"
            rows.append([
                app.id,
                app.company,
                app.title,
                app.status.value,
                app.date_applied,
                salary_str,
                app.last_updated
            ])
        print_table(headers, rows)

    elif parsed_args.command == "update":
        # Build kwargs for only provided/non-None args
        update_fields = {}
        if parsed_args.company is not None:
            update_fields["company"] = parsed_args.company
        if parsed_args.title is not None:
            update_fields["title"] = parsed_args.title
        if parsed_args.status is not None:
            update_fields["status"] = parsed_args.status
        if parsed_args.salary is not None:
            update_fields["salary"] = parsed_args.salary
        if parsed_args.url is not None:
            update_fields["url"] = parsed_args.url
        if parsed_args.notes is not None:
            update_fields["notes"] = parsed_args.notes
        if parsed_args.date is not None:
            update_fields["date_applied"] = parsed_args.date

        if not update_fields:
            print("No update arguments provided. Use options (e.g. -c, -t, -s) to specify changes.")
            return

        app = tracker.update_application(parsed_args.id, **update_fields)
        if app:
            print(f"Successfully updated application ID: {app.id}")
        else:
            print(f"Error: Job application with ID '{parsed_args.id}' not found.")

    elif parsed_args.command == "delete":
        success = tracker.delete_application(parsed_args.id)
        if success:
            print(f"Successfully deleted application ID: {parsed_args.id}")
        else:
            print(f"Error: Job application with ID '{parsed_args.id}' not found.")

    elif parsed_args.command == "stats":
        stats = tracker.get_statistics()
        print("=" * 40)
        print("     JOB APPLICATION TRACKER DASHBOARD")
        print("=" * 40)
        print(f"Total Applications: {stats['total']}")
        print("-" * 40)
        print("Applications by Status:")
        for status, count in stats["by_status"].items():
            pct = stats["percentages"][status]
            print(f"  - {status:<15}: {count:>3} ({pct:.1f}%)")
        print("-" * 40)
        print("Salary Overview:")
        sal_min = f"${stats['salary']['min']:,.2f}" if stats['salary']['min'] is not None else "N/A"
        sal_max = f"${stats['salary']['max']:,.2f}" if stats['salary']['max'] is not None else "N/A"
        sal_avg = f"${stats['salary']['avg']:,.2f}" if stats['salary']['avg'] is not None else "N/A"
        print(f"  - Min Salary       : {sal_min}")
        print(f"  - Max Salary       : {sal_max}")
        print(f"  - Average Salary   : {sal_avg}")
        print("-" * 40)
        print("Offered Salary Overview:")
        off_min = f"${stats['offered_salary']['min']:,.2f}" if stats['offered_salary']['min'] is not None else "N/A"
        off_max = f"${stats['offered_salary']['max']:,.2f}" if stats['offered_salary']['max'] is not None else "N/A"
        off_avg = f"${stats['offered_salary']['avg']:,.2f}" if stats['offered_salary']['avg'] is not None else "N/A"
        print(f"  - Min Offered      : {off_min}")
        print(f"  - Max Offered      : {off_max}")
        print(f"  - Average Offered  : {off_avg}")
        print("=" * 40)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
