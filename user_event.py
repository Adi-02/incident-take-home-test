from datetime import datetime

class UserEvent:
    def __init__(self, name : str, start_time : datetime, end_time : datetime) -> None:
        self.name = name 
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self) -> str:
        """
        Returns a clear string representation of the event for debugging.
        """
        return f"UserEvent(name={self.name}, start_time={self.start_time}, end_time={self.end_time})"
    
    def __eq__(self, other: object) -> bool:
        """
        Compare two UserEvent objects for equality based on name and time range.
        """
        if not isinstance(other, UserEvent):
            return False
        return (self.name == other.name and self.start_time == other.start_time and self.end_time == other.end_time)
    
    def _to_dict(self) -> dict[str, object]:
        """
        Convert the event into a dictionary representation.
        """
        return {"name" : self.name, "start_at" : self.start_time.strftime("%Y-%m-%dT%H:%M:%SZ"), "end_at" : self.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")}