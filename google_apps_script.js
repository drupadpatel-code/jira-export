/**
 * Google Apps Script for Jira Board Export to Google Sheets
 * 
 * Instructions:
 * 1. Open Google Sheets
 * 2. Go to Extensions > Apps Script
 * 3. Paste this code
 * 4. Replace YOUR_PYTHON_API_URL with your deployed Python API URL
 * 5. Save and run the function fetchJiraData()
 */

// Configuration - Replace with your Python API URL
const PYTHON_API_URL = 'https://YOUR_PYTHON_API_URL/jira/export/json';

/**
 * Main function to fetch Jira data and populate Google Sheet
 * @param {string} boardName - Name of the Jira board (e.g., "Category Scrum")
 */
function fetchJiraData(boardName = 'Category Scrum') {
  try {
    // Get the active sheet
    const sheet = SpreadsheetApp.getActiveSheet();
    
    // Clear existing data
    sheet.clear();
    
    // Fetch data from Python API
    const response = UrlFetchApp.fetch(`${PYTHON_API_URL}?boardName=${encodeURIComponent(boardName)}`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    const result = JSON.parse(response.getContentText());
    
    if (result.error) {
      sheet.getRange(1, 1).setValue('Error: ' + result.error);
      return;
    }
    
    const data = result.data;
    
    if (!data || data.length === 0) {
      sheet.getRange(1, 1).setValue('No data found');
      return;
    }
    
    // Set headers
    const headers = [['Status', 'Count', 'Ticket-ID', 'Ticket Name']];
    sheet.getRange(1, 1, 1, 4).setValues(headers);
    
    // Format header row
    const headerRange = sheet.getRange(1, 1, 1, 4);
    headerRange.setFontWeight('bold');
    headerRange.setBackground('#4285f4');
    headerRange.setFontColor('#ffffff');
    
    // Populate data
    const rows = data.map(item => [
      item.status,
      item.count,
      item.ticketId,
      item.ticketName
    ]);
    
    if (rows.length > 0) {
      sheet.getRange(2, 1, rows.length, 4).setValues(rows);
      
      // Auto-resize columns
      sheet.autoResizeColumns(1, 4);
      
      // Apply alternating row colors
      const dataRange = sheet.getRange(2, 1, rows.length, 4);
      const formats = [];
      for (let i = 0; i < rows.length; i++) {
        formats.push([
          i % 2 === 0 ? '#f8f9fa' : '#ffffff',
          i % 2 === 0 ? '#f8f9fa' : '#ffffff',
          i % 2 === 0 ? '#f8f9fa' : '#ffffff',
          i % 2 === 0 ? '#f8f9fa' : '#ffffff'
        ]);
      }
      dataRange.setBackgrounds(formats);
    }
    
    // Add timestamp
    sheet.getRange(1, 6).setValue('Last Updated: ' + new Date().toLocaleString());
    
    Logger.log(`Successfully imported ${rows.length} rows`);
    
  } catch (error) {
    Logger.log('Error: ' + error.toString());
    SpreadsheetApp.getActiveSheet().getRange(1, 1).setValue('Error: ' + error.toString());
  }
}

/**
 * Function to create a menu in Google Sheets
 */
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('Jira Export')
    .addItem('Fetch Jira Data', 'fetchJiraData')
    .addItem('Fetch with Custom Board Name', 'showBoardNameDialog')
    .addToUi();
}

/**
 * Show dialog to enter board name
 */
function showBoardNameDialog() {
  const ui = SpreadsheetApp.getUi();
  const response = ui.prompt(
    'Enter Jira Board Name',
    'Please enter the board name (e.g., Category Scrum):',
    ui.ButtonSet.OK_CANCEL
  );
  
  if (response.getSelectedButton() === ui.Button.OK) {
    const boardName = response.getResponseText();
    if (boardName) {
      fetchJiraData(boardName);
    }
  }
}

/**
 * Function to set up time-driven trigger (optional)
 * This will automatically refresh data every hour
 */
function createTimeDrivenTrigger() {
  ScriptApp.newTrigger('fetchJiraData')
    .timeBased()
    .everyHours(1)
    .create();
}

/**
 * Function to test the API connection
 */
function testConnection() {
  try {
    const response = UrlFetchApp.fetch(`${PYTHON_API_URL.replace('/json', '')}/health`, {
      method: 'GET'
    });
    
    const result = JSON.parse(response.getContentText());
    Logger.log('Connection test result: ' + JSON.stringify(result));
    
    if (result.status === 'healthy') {
      SpreadsheetApp.getUi().alert('Connection successful!');
    } else {
      SpreadsheetApp.getUi().alert('Connection failed!');
    }
  } catch (error) {
    SpreadsheetApp.getUi().alert('Connection error: ' + error.toString());
  }
}
