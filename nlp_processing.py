import re
from datetime import datetime as dt

def remove_greetings(text):
    greetings = ['hi', 'hello', 'hey', 'hi bot', 'hello bot', 'hey bot', 'how are you', 'good morning', 'bot']
    for greet in greetings:
        text = re.sub(rf"\b{re.escape(greet)}\b[,.\s]*", "", text, flags=re.IGNORECASE)
    return text.strip()

def clean_task_name(text):
    patterns = [
        r"\b(i have to|i need to|i gotta|i should|i must|i will|gotta)\b\s*",
        r"\b(please|kindly)\b\s*",
    ]
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    return text.strip().capitalize()

def extract_task_details(text):
    text = remove_greetings(text)

    pattern = r"(.*?)(?:by|before|on)\s*(\d{1,2}-\d{1,2}-\d{4}(?: at \d{1,2}(?::\d{2})?\s*(?:am|pm)?)?)"
    matches = re.findall(pattern, text, re.IGNORECASE)

    tasks = []
    for match in matches:
        task_text = clean_task_name(match[0].strip().strip(",.:;"))
        date_str = match[1].strip()

        try:
            if "at" in date_str:
                date_part, time_part = date_str.split("at")
                date = dt.strptime(date_part.strip(), "%d-%m-%Y").date()

                # Support both 3pm and 15:00 formats
                time_part = time_part.strip().lower()
                if "am" in time_part or "pm" in time_part:
                    time = dt.strptime(time_part, "%I%p").time()
                else:
                    time = dt.strptime(time_part, "%H:%M").time()

                tasks.append({"task": task_text, "date": date, "time": time})
            else:
                deadline = dt.strptime(date_str, '%d-%m-%Y').date()
                tasks.append({"task": task_text, "deadline": deadline})
        except ValueError as e:
            print(f"Skipping task due to parsing error: {e}")

    return tasks

def extract_reschedule_details(text):
    date_match = re.search(r"reschedule tasks on (\d{1,2}-\d{1,2}-\d{4})", text, re.IGNORECASE)
    time_match = re.search(r"to (\d{1,2})\s*(?:am|pm)?\s*(?:-|to)?\s*(\d{1,2})\s*(am|pm)?", text, re.IGNORECASE)

    reschedule_date = None
    new_start_hour = 14
    new_end_hour = 17

    if date_match:
        try:
            reschedule_date = dt.strptime(date_match.group(1), "%d-%m-%Y").date()
        except:
            pass

    if time_match:
        start_hour = int(time_match.group(1))
        end_hour = int(time_match.group(2))
        am_pm = time_match.group(3)

        if am_pm == "pm":
            if start_hour < 12:
                start_hour += 12
            if end_hour < 12:
                end_hour += 12

        new_start_hour = start_hour
        new_end_hour = end_hour

    return reschedule_date, new_start_hour, new_end_hour
