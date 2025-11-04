class UserEvent:
    def __init__(self, name, start_time, end_time):
        self.name = name 
        self.start_time = start_time
        self.end_time = end_time

    def __repr__(self):
        """
        Nice printing method
        """
        return f"UserEvent(name={self.name}, start_time={self.start_time}, end_time={self.end_time})"