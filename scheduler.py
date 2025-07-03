from datetime import datetime as dt, timedelta
import datetime
from ml_model import predict_duration

# Define preferred working hours
WORK_START = 9
WORK_END = 18

def get_time_slots_for_day(date, occupied_slots, hours_needed):
    """
    Finds available hourly slots for a given day until the required hours are filled.
    """
    slots = []
    current_hour = WORK_START

    while current_hour < WORK_END and hours_needed > 0:
        time_str = f"{date} {current_hour:02d}:00"
        if time_str not in occupied_slots:
            slots.append((date, current_hour))
            occupied_slots.add(time_str)
            hours_needed -= 1
        current_hour += 1

    return slots, occupied_slots


def distribute_task(task_name, deadline, duration_hours, occupied_slots):
    """
    Distributes a task's predicted hours across available days up to the deadline.
    """
    schedule = []
    today = datetime.date.today()

    if isinstance(deadline, str):
        deadline = dt.strptime(deadline, "%Y-%m-%d").date()

    total_days = (deadline - today).days
    if total_days <= 0:
        total_days = 1

    hours_remaining = duration_hours

    for i in range(total_days):
        current_date = today + timedelta(days=i)
        date_str = current_date.strftime("%Y-%m-%d")

        slots_needed = min(hours_remaining, duration_hours // total_days + 1)
        slots, occupied_slots = get_time_slots_for_day(date_str, occupied_slots, slots_needed)

        for date, hour in slots:
            schedule.append({
                "task": task_name,
                "date": dt.strptime(date, "%Y-%m-%d").strftime("%b %d, %Y"),
                "start_time": f"{hour:02d}:00",
                "end_time": f"{hour + 1:02d}:00"
            })

        hours_remaining -= len(slots)
        if hours_remaining <= 0:
            break

    return schedule, occupied_slots


def generate_schedule(tasks):
    full_schedule = []
    occupied_slots = set()

    for task_obj in tasks:
        task = task_obj.get("task", "Unnamed Task")

        # --- Time-bound task ---
        if "date" in task_obj and "time" in task_obj:
            date = task_obj["date"]
            time = task_obj["time"]
            start_hour = time.hour
            end_hour = start_hour + 1
            date_str = date.strftime("%Y-%m-%d")

            time_str = f"{date_str} {start_hour:02d}:00"
            if time_str not in occupied_slots:
                full_schedule.append({
                    "task": task.capitalize(),
                    "date": date.strftime("%b %d, %Y"),
                    "start_time": f"{start_hour:02d}:00",
                    "end_time": f"{end_hour:02d}:00"
                })
                occupied_slots.add(time_str)
            continue

        # --- Flexible task ---
        deadline = task_obj.get("deadline")
        try:
            deadline_obj = deadline if isinstance(deadline, datetime.date) else dt.strptime(deadline, "%Y-%m-%d").date()
        except Exception as e:
            print(f"Skipping task due to invalid deadline: {task}, Error: {e}")
            continue

        predicted_duration = predict_duration(task)
        task_schedule, occupied_slots = distribute_task(task, deadline_obj, predicted_duration, occupied_slots)
        full_schedule.extend(task_schedule)

    return full_schedule


def reschedule_schedule_on_date(tasks, reschedule_date, start_hour=14, end_hour=17):
    updated_schedule = []
    custom_slots = [(h, h + 1) for h in range(start_hour, end_hour)]
    reschedule_str = reschedule_date.strftime("%b %d, %Y")

    # Go through each scheduled task
    for task in tasks:
        task_name = task["task"]
        task_date = task.get("date")

        if not task_date:
            continue

        # Match the displayed schedule date format (e.g., Apr 12, 2025)
        try:
            task_dt = dt.strptime(task_date, "%b %d, %Y").date()
        except Exception as e:
            continue

        if task_dt == reschedule_date:
            for slot in custom_slots:
                start_time = f"{slot[0]:02}:00"
                end_time = f"{slot[1]:02}:00"
                updated_schedule.append({
                    "task": task_name,
                    "date": reschedule_str,
                    "start_time": start_time,
                    "end_time": end_time
                })

    return updated_schedule if updated_schedule else [{
        "task": "No tasks matched the reschedule date.",
        "start_time": "", "end_time": "", "date": ""
    }]
