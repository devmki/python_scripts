from pushbullet import Pushbullet

def send_push_message(api_key, title, message):
    """Send a push message using Pushbullet."""
    try:
        print(f"Debug: Initializing Pushbullet with API key: {api_key}")
        pb = Pushbullet(api_key)
        print(f"Debug: Sending push message with title: '{title}' and message: '{message}'")
        push = pb.push_note(title, message)
        print(f"Debug: Push sent successfully: {push}")
    except Exception as e:
        print(f"Error sending push message: {e}")