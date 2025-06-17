

def save_notification(notification, db):
    """
    Save a notification to the database.
    
    Args:
        notification (dict): The notification data to save.
        db: The database connection object.
    """
    try:
        db.notifications.insert_one(notification)
    except Exception as e:
        print(f"Error saving notification: {e}")