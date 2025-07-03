import os
import datetime
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from flask import session

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
flow = Flow.from_client_secrets_file(
    'credentials.json',
    scopes=SCOPES,
    redirect_uri='http://127.0.0.1:5000/oauth2callback'
)

def get_credentials():
    if 'credentials' not in session:
        return None
    return Credentials(**session['credentials'])

def get_calendar_tasks(creds):
    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    tasks = []
    for event in events:
        tasks.append({
            'summary': event.get('summary'),
            'start': event['start'].get('dateTime', event['start'].get('date'))
        })
    return tasks
