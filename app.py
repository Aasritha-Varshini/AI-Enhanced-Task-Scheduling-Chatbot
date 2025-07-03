from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import os
import json

from scheduler import generate_schedule, reschedule_schedule_on_date
from nlp_processing import extract_task_details, extract_reschedule_details

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

GOOGLE_CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile'
]
REDIRECT_URI = 'http://localhost:5000/oauth2callback'

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login')
def login():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt='consent', include_granted_scopes='true')
    return redirect(auth_url)


@app.route('/oauth2callback')
def oauth2callback():
    flow = Flow.from_client_secrets_file(
        GOOGLE_CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }
    user_info_service = build('oauth2', 'v2', credentials=credentials)
    user_info = user_info_service.userinfo().get().execute()
    session['user'] = {
        'name': user_info.get('name', 'User'),
        'email': user_info.get('email')
    }
    return redirect(url_for('dashboard'))


@app.route('/temporary_login')
def temporary_login():
    session['user'] = {
        'name': 'Guest',
        'email': None
    }
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    user = session.get('user')
    if not user:
        return redirect(url_for('index'))
    if user['name'] == 'Guest':
        return render_template('chatbot.html', user=user)
    else:
        return render_template('dashboard.html', user=user)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/fetch_events')
def fetch_events():
    credentials_data = session.get('credentials')
    if not credentials_data:
        return jsonify([])

    creds = Credentials(
        token=credentials_data['token'],
        refresh_token=credentials_data['refresh_token'],
        token_uri=credentials_data['token_uri'],
        client_id=credentials_data['client_id'],
        client_secret=credentials_data['client_secret'],
        scopes=credentials_data['scopes']
    )

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.utcnow()
    one_week_later = now + timedelta(weeks=1)

    try:
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now.isoformat() + 'Z',
            timeMax=one_week_later.isoformat() + 'Z',
            maxResults=20,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        formatted_events = [{
            'summary': e.get('summary', 'No Title'),
            'start': e['start'].get('dateTime', e['start'].get('date')),
            'end': e['end'].get('dateTime', e['end'].get('date'))
        } for e in events]

        return jsonify(formatted_events)

    except Exception as e:
        print("Error fetching events:", str(e))
        return jsonify([])


@app.route("/guest_schedule", methods=["POST"])
def guest_schedule():
    data = request.get_json()
    text = data.get("text", "")

    if "reschedule" in text.lower():
        try:
            reschedule_date, start_hour, end_hour = extract_reschedule_details(text)

            with open("previous_schedule.json", "r") as f:
                existing_schedule = json.load(f)

            # Match scheduled tasks by actual schedule date (not just deadline)
            schedule = reschedule_schedule_on_date(existing_schedule, reschedule_date, start_hour, end_hour)
            return jsonify(schedule)
        except Exception as e:
            print("Error in rescheduling:", e)
            return jsonify([{"task": f"An error occurred while generating the schedule: {str(e)}", "start_time": "", "end_time": "", "date": ""}])
    else:
        tasks = extract_task_details(text)
        if not tasks:
            return jsonify([{"task": "I couldn't find any valid tasks in your input.", "start_time": "", "end_time": "", "date": ""}])

        schedule = generate_schedule(tasks)

        # Save both tasks and their generated schedule
        with open("previous_tasks.json", "w") as f:
            json.dump(tasks, f, default=str)
        with open("previous_schedule.json", "w") as f:
            json.dump(schedule, f, default=str)

        return jsonify(schedule)


if __name__ == '__main__':
    app.run(debug=True)
