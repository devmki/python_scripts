from datetime import datetime
from .database import get_birthdays, update_age_if_birthday
from .push_notification import send_push_message

def check_and_send_birthdays(api_key, mode='send'):
    """Check the database for today's birthdays and send push messages."""
    today = datetime.now().strftime("%d.%m.%Y")
    birthdays = get_birthdays()
    birthday_list = []
    for birthday in birthdays:
        name, date, age = birthday[1], birthday[2], birthday[3]
        if date[:-5] == today[:-5]:
            message = ''
            appendage = 'th'
            if str(age) == '-1':
                message = f"Today is {name}'s birthday!"
                appendage = ''
            elif str(age).endswith('1'):
                appendage = 'st'
            elif str(age).endswith('2'):
                appendage = 'nd'
            elif str(age).endswith('3'):
                appendage = 'rd'
                
            if appendage != '':
                message = f"Today is {name}'s {age}{appendage} birthday!"
            
            if mode == 'send':
                send_push_message(api_key, "Birthday Reminder", message)
            else:
                birthday_list.append(message)
    if mode != 'send':
        return birthday_list
