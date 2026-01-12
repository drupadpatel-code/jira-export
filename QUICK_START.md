# Quick Start Guide

## Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Environment Variables

Create a `.env` file or export these variables:

```bash
export JIRA_BASE_URL=https://blackbuck.atlassian.net
export JIRA_USERNAME=your-email@blackbuck.com
export JIRA_API_TOKEN=your-api-token
export PORT=8080
```

Or modify the default values in `app.py` (lines 12-14).

## Step 3: Run Locally

```bash
python app.py
```

The API will be available at `http://localhost:8080`

## Step 4: Test the API

```bash
# Test CSV export
curl "http://localhost:8080/jira/export?boardName=Category%20Scrum" -o jira_issues.csv

# Test JSON export (for Google Apps Script)
curl "http://localhost:8080/jira/export/json?boardName=Category%20Scrum"
```

## Step 5: Deploy to Cloud

### Google Cloud Run (Recommended)

1. Build and push:
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/jira-export
```

2. Deploy:
```bash
gcloud run deploy jira-export \
  --image gcr.io/YOUR_PROJECT_ID/jira-export \
  --platform managed \
  --set-env-vars JIRA_BASE_URL=https://blackbuck.atlassian.net \
  --set-env-vars JIRA_USERNAME=your-email@blackbuck.com \
  --set-secrets JIRA_API_TOKEN=your-secret-name:latest
```

3. Get the URL from the deployment output

### Heroku

1. Create app:
```bash
heroku create your-app-name
```

2. Set config:
```bash
heroku config:set JIRA_BASE_URL=https://blackbuck.atlassian.net
heroku config:set JIRA_USERNAME=your-email@blackbuck.com
heroku config:set JIRA_API_TOKEN=your-token
```

3. Deploy:
```bash
git push heroku main
```

## Step 6: Setup Google Apps Script

1. Open Google Sheets
2. Go to **Extensions > Apps Script**
3. Delete the default code
4. Copy and paste the entire content from `google_apps_script.js`
5. Replace `YOUR_PYTHON_API_URL` on line 10 with your deployed API URL
   - Example: `https://your-app-name.herokuapp.com`
   - Example: `https://jira-export-xxxxx.run.app`
6. Click **Save** (💾 icon)
7. Click **Run** (▶️ icon) and select `fetchJiraData`
8. Authorize the script when prompted
9. Refresh your Google Sheet - you should see a new menu "Jira Export"

## Step 7: Use in Google Sheets

1. Click on **Jira Export** menu (top menu bar)
2. Select **Fetch Jira Data** (uses default board name "Category Scrum")
3. Or select **Fetch with Custom Board Name** to enter a different board name
4. Data will automatically populate in your sheet!

## Troubleshooting

### API Connection Issues
- Check that your Python API is running and accessible
- Verify the URL in Google Apps Script matches your deployed URL
- Test the API directly in a browser: `https://your-api-url/jira/export/json?boardName=Category%20Scrum`

### Authentication Issues
- Verify your Jira API token is correct
- Check that your Jira username has access to the board
- Ensure the board name matches exactly (case-sensitive)

### No Data Returned
- Verify the board name is correct
- Check that there's an active sprint for the current month
- Test the API endpoint directly to see error messages

## Security Best Practices

1. **Never commit API tokens to Git**
   - Use environment variables
   - Use secret management services (Google Secret Manager, Heroku Config Vars)

2. **Use HTTPS in production**
   - All cloud platforms provide HTTPS by default

3. **Restrict API access** (optional)
   - Add API key authentication
   - Use IP whitelisting if needed

## Support

For issues or questions, check:
- Jira API documentation: https://developer.atlassian.com/cloud/jira/software/rest/
- Google Apps Script documentation: https://developers.google.com/apps-script
