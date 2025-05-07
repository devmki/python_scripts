"""
This script reads an ICS file containing waste collection events 
and filters them to find events for today and tomorrow.
"""
import datetime
from icalendar import Calendar

def get_events_for_today_and_tomorrow(ics_file_path):
    """
    Reads an ICS file and returns events for today and tomorrow.
    """
    # Get today's and tomorrow's dates
    today = datetime.date.today()
    tomorrow = today + datetime.timedelta(days=1)

    # Read the ICS file
    with open(ics_file_path, 'r', encoding='utf-8') as file:
        calendar = Calendar.from_ical(file.read())

    # Find events for today and tomorrow
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            event_start = component.get('DTSTART').dt
            if event_start in   [today, tomorrow]:
                summary = component.get('SUMMARY').to_ical().decode('utf-8')
                # Filter summary to keep only specific keywords
                for keyword in ["Papier", "Restmüll", "Biomüll", "Gelber Sack"]:
                    if keyword in summary:
                        events.append({
                            'summary': keyword,
                            'start': event_start,
                            'end': component.get('DTEND').dt
                        })
                        break

    return events
