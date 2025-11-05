import json 
from user_event import UserEvent
from datetime import datetime, timedelta

class FileHandler:
    def __init__(self, schedule_file : str, override_file : str, output_file : str) -> None:
        self.schedule_file = schedule_file
        self.override_file = override_file
        self.output_file = output_file

    def read_schedule_file(self) -> list[UserEvent]:
        """
        Read schedule file and return a list of schedule events
        """
        with open(self.schedule_file, "r") as f:
            schedule_data = json.load(f)

        users = schedule_data.get("users", [])
        start_str = schedule_data.get("handover_start_at")
        interval_days = schedule_data.get("handover_interval_days", 0)

        if not users or not start_str or interval_days <= 0:
            raise ValueError("Invalid schedule file: missing required fields.")

        curr_start_time = self._convert_str_to_datetime(start_str)

        schedule_lst: list[UserEvent] = []
        for name in users:
            curr_end_time = curr_start_time + timedelta(days=interval_days)
            schedule_lst.append(UserEvent(name, curr_start_time, curr_end_time))

            curr_start_time = curr_end_time

        return schedule_lst
    
    def read_override_file(self) -> list[UserEvent]:
        """
        Read override file and return a list of override events
        """
        override_lst = []
        with open(self.override_file, 'r') as f:
            override_data = json.load(f)

        for user in override_data:
            name = user.get("user")
            start_time = user.get("start_at")
            end_time = user.get("end_at")
            name, start_time_dt, end_time_dt = self._validate_input(name, start_time, end_time)
            if name == None or start_time_dt == None or end_time_dt == None:
                continue
            new_override_event = UserEvent(name, start_time_dt, end_time_dt)
            override_lst.append(new_override_event)

        return override_lst
    
    def write_to_output_file(self, schedule_queue):
        """
        Write schedule to output json file
        """
        output_data = []
        for schedule_event in schedule_queue:
            start_time = schedule_event.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = schedule_event.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            final_event = {"name" : schedule_event.name, "start_at" : start_time, "end_at" : end_time}
            output_data.append(final_event)

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
            new_time = date_time_str.strptime("%Y-%m-%dT%H:%M:%SZ")
            return new_time
        except ValueError:
            return None
    
        
