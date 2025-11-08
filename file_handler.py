import json 
from user_event import UserEvent
from datetime import datetime, timedelta

class FileHandler:
    def __init__(self, schedule_file : str, override_file : str, output_file : str) -> None:
        self.schedule_file = schedule_file
        self.override_file = override_file
        self.output_file = output_file

    def read_schedule_file(self, start_time_str: str, end_time_str: str) -> list[UserEvent]:
        """
        Read and generate schedule events from schedule.json.
        - Validates and parses start/end time strings.
        - Generates repeated handover events.
        - Truncates them within [start_time, end_time].
        """
        start_time = self._convert_str_to_datetime(start_time_str)
        end_time = self._convert_str_to_datetime(end_time_str)
        if not (start_time and end_time and start_time < end_time):
            raise ValueError("Invalid start or end time range provided.")

        with open(self.schedule_file, "r") as f:
            schedule_data = json.load(f)

        users = schedule_data.get("users", [])
        start_str = schedule_data.get("handover_start_at")
        interval_days = schedule_data.get("handover_interval_days", 0)

        if not users or not start_str or interval_days <= 0:
            raise ValueError("Invalid schedule file: missing required fields.")

        base_start_time = self._convert_str_to_datetime(start_str)
        if base_start_time is None:
            raise ValueError("Invalid handover_start_at format in schedule file.")

        schedule_lst: list[UserEvent] = []
        user_idx = 0
        curr_start_time = base_start_time
        delta = timedelta(days=interval_days)

        # Generate and truncate events within [start_time, end_time]
        while curr_start_time < end_time:
            curr_end_time = curr_start_time + delta
            name = users[user_idx % len(users)]

            # Truncate to fit the range
            truncated_start = max(curr_start_time, start_time)
            truncated_end = min(curr_end_time, end_time)
            if truncated_start < truncated_end:
                schedule_lst.append(UserEvent(name, truncated_start, truncated_end))

            curr_start_time += delta
            user_idx += 1

        return schedule_lst

    def read_override_file(self, start_time_str: str, end_time_str: str) -> list[UserEvent]:
        """
        Read override events from override.json.
        - Validates and parses start/end time strings.
        - Truncates each override to within [start_time, end_time].
        """
        start_time = self._convert_str_to_datetime(start_time_str)
        end_time = self._convert_str_to_datetime(end_time_str)
        if not (start_time and end_time and start_time < end_time):
            raise ValueError("Invalid start or end time range provided.")

        override_lst: list[UserEvent] = []
        with open(self.override_file, "r") as f:
            override_data = json.load(f)

        for user in override_data:
            name = user.get("user")
            start_str = user.get("start_at")
            end_str = user.get("end_at")

            name, start_dt, end_dt = self._validate_input(name, start_str, end_str)
            if not (name and start_dt and end_dt):
                continue

            # Truncate to fit within global [start_time, end_time]
            truncated_start = max(start_dt, start_time)
            truncated_end = min(end_dt, end_time)

            if truncated_start < truncated_end:
                override_lst.append(UserEvent(name, truncated_start, truncated_end))

        return override_lst
    
    def write_to_output_file(self, schedule_queue):
        """
        Write schedule to output json file
        """
        output_data = []
        for schedule_event in schedule_queue:
            output_data.append(schedule_event._to_dict())

        with open(self.output_file, "w") as f:
            json.dump(output_data, f, indent=2)
    
    def _validate_input(self, name : str, start_time : str, end_time : str) -> tuple[str | None, datetime | None, datetime | None]:
        """
        Validate input to make sure:
        name -> string
        start_time -> can be parsed as a valid datetime object
        end_time -> can be parsed as a valid datetime object
        """
        start_time_dt = self._convert_str_to_datetime(start_time)
        end_time_dt = self._convert_str_to_datetime(end_time)
        if not isinstance(name, str) or start_time == None or end_time_dt == None:
            return None,None,None
        return name, start_time_dt, end_time_dt
    
    def _convert_str_to_datetime(self, date_time_str : datetime) -> datetime | None:
        """
        Try convert str to datetime object
        """
        try:
            new_time = datetime.strptime(date_time_str, "%Y-%m-%dT%H:%M:%SZ")
            return new_time
        except ValueError:
            return None
    
        
