# Jira Board Export - Python Version

This is a Python Flask application that exports Jira board issues to CSV/JSON format, designed to work with Google Apps Script for Google Sheets integration.

## Features

- Fetches Jira board issues from the current month's sprint
- Exports data as CSV (downloadable) or JSON (for Google Apps Script)
- Filters issues by current month's sprint automatically
- CORS enabled for Google Apps Script integration

## Prerequisites

- Python 3.8 or higher
- Jira API token
- Jira board access

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Set environment variables or modify the default values in `app.py`:

```bash
export JIRA_BASE_URL=https://blackbuck.atlassian.net
export JIRA_USERNAME=your-email@blackbuck.com
export JIRA_API_TOKEN=your-api-token
export PORT=8080
```

Or create a `.env` file (recommended for local development):
```
JIRA_BASE_URL=https://blackbuck.atlassian.net
JIRA_USERNAME=drupad.patel@blackbuck.com
JIRA_API_TOKEN=your-api-token
PORT=8080
```

## Running Locally

```bash
python app.py
```

Or with gunicorn (production):
```bash
gunicorn -w 4 -b 0.0.0.0:8080 app:app
```

## API Endpoints

### 1. Export CSV
```
GET /jira/export?boardName=Category%20Scrum
```
Returns a downloadable CSV file.

### 2. Export JSON (for Google Apps Script)
```
GET /jira/export/json?boardName=Category%20Scrum
```
Returns JSON data that can be consumed by Google Apps Script.

### 3. Health Check
```
GET /health
```
Returns API health status.

## Deployment Options

### Option 1: Google Cloud Run (Recommended)

1. Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]
```

2. Build and deploy:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jira-export
gcloud run deploy jira-export --image gcr.io/YOUR_PROJECT_ID/jira-export --platform managed
```

### Option 2: Heroku

1. Create `Procfile`:
```
web: gunicorn -w 4 -b 0.0.0.0:$PORT app:app
```

2. Deploy:
```bash
heroku create your-app-name
heroku config:set JIRA_BASE_URL=your-url
heroku config:set JIRA_USERNAME=your-username
heroku config:set JIRA_API_TOKEN=your-token
git push heroku main
```

### Option 3: Railway

1. Connect your repository to Railway
2. Set environment variables in Railway dashboard
3. Railway will auto-detect and deploy

### Option 4: Render

1. Connect your repository to Render
2. Set environment variables
3. Use gunicorn as start command: `gunicorn -w 4 -b 0.0.0.0:$PORT app:app`

## Google Apps Script Setup

1. Open Google Sheets
2. Go to Extensions > Apps Script
3. Copy the code from `google_apps_script.js`
4. Replace `YOUR_PYTHON_API_URL` with your deployed API URL
5. Save and run `fetchJiraData()` function
6. A menu "Jira Export" will appear in your Google Sheets

## Usage in Google Sheets

1. Click on "Jira Export" menu
2. Select "Fetch Jira Data" (uses default board name)
3. Or select "Fetch with Custom Board Name" to specify a different board
4. Data will be automatically populated in the sheet

## CSV Format

The exported CSV contains:
- Status: Issue status
- Count: Number of issues with this status
- Ticket-ID: Jira ticket key (e.g., PROJ-123)
- Ticket Name: Issue summary/title

## Error Handling

The API returns appropriate HTTP status codes:
- 200: Success
- 400: Missing or invalid parameters
- 404: Board or sprint not found
- 500: Server error

## Security Notes

- Never commit API tokens to version control
- Use environment variables for sensitive data
- Consider using Google Cloud Secret Manager for production
- Enable HTTPS in production deployments
