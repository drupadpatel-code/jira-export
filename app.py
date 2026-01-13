from flask import Flask, Response, request, jsonify
from flask_cors import CORS
import requests
from datetime import datetime, timedelta, timezone

import csv
import io
import os
import base64

app = Flask(__name__)
CORS(app)  # Allow Google Apps Script calls

# =========================
# Environment configuration
# =========================
JIRA_BASE_URL = os.getenv("JIRA_BASE_URL")
JIRA_USERNAME = os.getenv("JIRA_USERNAME")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")

REQUIRED_VARS = ["JIRA_BASE_URL", "JIRA_USERNAME", "JIRA_API_TOKEN"]


def validate_env():
    missing = [v for v in REQUIRED_VARS if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")


def get_auth_header():
    """
    Generate Basic Auth header for Jira API
    (No secrets are stored in code)
    """
    validate_env()
    auth_string = f"{JIRA_USERNAME}:{JIRA_API_TOKEN}"
    encoded = base64.b64encode(auth_string.encode()).decode()
    return {
        "Authorization": f"Basic {encoded}",
        "Accept": "application/json"
    }


# =========================
# Jira API helpers
# =========================
def get_board_by_name(board_name):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board"
    params = {"name": board_name}
    response = requests.get(url, headers=get_auth_header(), params=params)
    response.raise_for_status()
    return response.json()


def get_board_sprints(board_id):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/board/{board_id}/sprint"
    params = {"state": "active"}
    response = requests.get(url, headers=get_auth_header(), params=params)
    response.raise_for_status()
    return response.json()


def get_sprint_issues(sprint_id):
    url = f"{JIRA_BASE_URL}/rest/agile/1.0/sprint/{sprint_id}/issue"
    params = {"maxResults": 1000}
    response = requests.get(url, headers=get_auth_header(), params=params)
    response.raise_for_status()
    return response.json()


def parse_date(date_str):
    if not date_str:
        return None

    try:
        # Normalize Jira timezone format
        if date_str.endswith('Z'):
            date_str = date_str.replace('Z', '+00:00')

        dt = datetime.fromisoformat(date_str)

        # Ensure timezone-aware
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt
    except Exception:
        return None


def find_current_month_sprint(sprints):
    now = datetime.now(timezone.utc)

    for sprint in sprints.get("values", []):
        start = parse_date(sprint.get("startDate"))
        end = parse_date(sprint.get("endDate"))
        if start and end and start <= now <= end:
            return sprint.get("id")
    return sprints.get("values", [{}])[0].get("id")


# =========================
# CSV generation
# =========================
def generate_csv(issues):
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Status", "Count", "Ticket ID", "Ticket Name"])

    status_map = {}
    for issue in issues:
        status = issue["fields"]["status"]["name"]
        status_map.setdefault(status, []).append(issue)

    for status, tickets in status_map.items():
        for issue in tickets:
            writer.writerow([
                status,
                len(tickets),
                issue["key"],
                issue["fields"]["summary"]
            ])

    return output.getvalue()


# =========================
# Routes
# =========================
@app.route("/health", methods=["GET"])
def health():
    return {"status": "healthy"}, 200


@app.route("/jira/export", methods=["GET"])
def export_csv():
    board_name = request.args.get("boardName")
    if not board_name:
        return {"error": "boardName parameter is required"}, 400

    try:
        board = get_board_by_name(board_name)["values"][0]
        sprints = get_board_sprints(board["id"])
        sprint_id = find_current_month_sprint(sprints)
        issues = get_sprint_issues(sprint_id)["issues"]

        csv_data = generate_csv(issues)

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=jira_issues.csv"}
        )

    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/jira/export/json", methods=["GET"])
def export_json():
    board_name = request.args.get("boardName")
    if not board_name:
        return {"error": "boardName parameter is required"}, 400

    try:
        board = get_board_by_name(board_name)["values"][0]
        sprints = get_board_sprints(board["id"])
        sprint_id = find_current_month_sprint(sprints)
        issues = get_sprint_issues(sprint_id)["issues"]

        result = []
        status_map = {}

        for issue in issues:
            status = issue["fields"]["status"]["name"]
            status_map.setdefault(status, []).append({
                "ticketId": issue["key"],
                "ticketName": issue["fields"]["summary"]
            })

        for status, tickets in status_map.items():
            for t in tickets:
                result.append({
                    "status": status,
                    "count": len(tickets),
                    "ticketId": t["ticketId"],
                    "ticketName": t["ticketName"]
                })

        return {"data": result}

    except Exception as e:
        return {"error": str(e)}, 500


# =========================
# App entry point
# =========================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
