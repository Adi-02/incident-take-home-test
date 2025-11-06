from datetime import datetime

class UserEvent:
    def __init__(self, name : str, start_time : datetime, end_time : datetime) -> None:
        self.name = name 
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        """
        Returns a clear string representation of the event for debugging
        """
        return f"UserEvent(name={self.name}, start_time={self.start_time}, end_time={self.end_time})"