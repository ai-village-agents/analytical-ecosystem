import argparse
import csv
import datetime
import os
import re
import sys
from typing import Dict, List, Optional, Tuple

TEMPLATE_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "research_outreach_emails_day429.md")
TRACKER_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "outreach_tracker.csv")

# Keywords used to match templates and tracker rows for the first five institutions.
TARGETS = [
    ("Stanford HAI", "stanford hai"),
    ("MIT CSAIL", "mit csail"),
    ("UC Berkeley CHAI", "chai"),
    ("University of Washington", "university of washington"),
    ("Carnegie Mellon LTI", "carnegie mellon"),
]


def load_templates(path: str) -> Dict[str, Dict[str, str]]:
    """Parse the markdown template file into a mapping keyed by the template header."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Template file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r"## Template \d+: (?P<header>.*?)\n"
        r"\*\*Subject:\*\* (?P<subject>.*?)\n\n"
        r"\*\*Body:\*\*\n(?P<body>.*?)(?:\n---|$)",
        re.DOTALL,
    )

    templates = {}
    for match in pattern.finditer(content):
        header = match.group("header").strip()
        subject = match.group("subject").strip()
        body = match.group("body").strip()
        templates[header] = {"subject": subject, "body": body}

    if not templates:
        raise ValueError("No templates found in the markdown file.")
    return templates


def find_template_by_keyword(templates: Dict[str, Dict[str, str]], keyword: str) -> Tuple[str, Dict[str, str]]:
    """Return the first template whose header contains the keyword (case-insensitive)."""
    keyword_lower = keyword.lower()
    for header, payload in templates.items():
        if keyword_lower in header.lower():
            return header, payload
    raise KeyError(f"No template found matching keyword: {keyword}")


def load_tracker(path: str) -> List[dict]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Tracker CSV not found: {path}")
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    if not rows:
        raise ValueError("Tracker CSV is empty.")
    return rows


def find_tracker_row(rows: List[dict], keyword: str) -> Optional[dict]:
    target = keyword.lower()
    for row in rows:
        if target in row.get("Institution", "").lower():
            return row
    return None


def prompt_yes_no(message: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        choice = input(f"{message} {suffix} ").strip().lower()
        if not choice:
            return default
        if choice in {"y", "yes"}:
            return True
        if choice in {"n", "no"}:
            return False
        print("Please respond with 'y' or 'n'.")


def send_email_stub(institution: str, recipient_email: str, subject: str, body: str) -> None:
    # Stub to represent sending; replace with real email integration if needed.
    print(f"\nSending to {institution} <{recipient_email}>...")
    print(f"Subject: {subject}")
    print("Body preview:")
    print(body)
    print("Status: queued (stub)\n")


def update_tracker(rows: List[dict], row_to_update: dict, sent_date: str) -> None:
    row_to_update["Outreach_Date"] = sent_date
    row_to_update["Response_Received"] = row_to_update.get("Response_Received", "")
    row_to_update["Response_Status"] = row_to_update.get("Response_Status", "")


def write_tracker(path: str, rows: List[dict]) -> None:
    fieldnames = rows[0].keys()
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def process_institution(
    templates: Dict[str, Dict[str, str]],
    tracker_rows: List[dict],
    friendly_name: str,
    keyword: str,
    sent_date: str,
) -> bool:
    try:
        template_header, template = find_template_by_keyword(templates, keyword)
    except KeyError as exc:
        print(f"[ERROR] {exc}")
        return False

    tracker_row = find_tracker_row(tracker_rows, keyword)
    if not tracker_row:
        print(f"[ERROR] No tracker row found for keyword: {keyword}")
        return False

    subject = template["subject"]
    body = template["body"]
    recipient_email = tracker_row.get("Email", "unknown")

    print("\n" + "=" * 60)
    print(f"Preview for {friendly_name} ({template_header})")
    print("-" * 60)
    print(f"To: {recipient_email}")
    print(f"Subject: {subject}")
    print("\nBody:\n" + body)
    print("=" * 60)

    if not prompt_yes_no("Send this email?", default=False):
        print("Skipped.\n")
        return False

    try:
        send_email_stub(template_header, recipient_email, subject, body)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] Failed to send email: {exc}")
        return False

    update_tracker(tracker_rows, tracker_row, sent_date)
    print(f"Recorded send date {sent_date} for {tracker_row.get('Institution')}")
    return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send research outreach emails and update tracker.")
    parser.add_argument("--templates", default=TEMPLATE_PATH_DEFAULT, help="Path to markdown templates.")
    parser.add_argument("--tracker", default=TRACKER_PATH_DEFAULT, help="Path to outreach tracker CSV.")
    parser.add_argument("--date", default=datetime.date.today().isoformat(), help="Send date to record (YYYY-MM-DD).")
    parser.add_argument(
        "--auto-yes",
        action="store_true",
        help="Auto-confirm sending without interactive prompts (use with caution).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.auto_yes:
        # Allow non-interactive runs while still logging actions.
        def auto_yes(_: str, default: bool = False) -> bool:  # type: ignore[override]
            return True

        globals()["prompt_yes_no"] = auto_yes  # type: ignore[assignment]

    try:
        templates = load_templates(args.templates)
        tracker_rows = load_tracker(args.tracker)
    except Exception as exc:  # noqa: BLE001
        print(f"[ERROR] {exc}")
        sys.exit(1)

    any_sent = False
    for friendly_name, keyword in TARGETS:
        sent = process_institution(templates, tracker_rows, friendly_name, keyword, args.date)
        any_sent = any_sent or sent

    if any_sent:
        try:
            write_tracker(args.tracker, tracker_rows)
            print(f"\nTracker updated at {args.tracker}")
        except Exception as exc:  # noqa: BLE001
            print(f"[ERROR] Failed to write tracker: {exc}")
            sys.exit(1)
    else:
        print("\nNo emails sent; tracker not modified.")


if __name__ == "__main__":
    main()
