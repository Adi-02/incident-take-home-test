import json 
from user_event import UserEvent
from datetime import datetime, timedelta

class FileHandler:
    def __init__(self, schedule_file, override_file, output_file):
        self.schedule_file = schedule_file
        self.override_file = override_file
        self.output_file = output_file

    def read_schedule_file(self):
        schedule_lst = []
        with open(self.schedule_file, 'r') as f:
            schedule_data = json.load(f)
        
        curr_start_time = None
        curr_end_time = None
        for user in schedule_data.get("users"):
            name = user 

            if not curr_start_time:
                curr_start_time = schedule_data.get("handover_start_at")
                curr_start_time = datetime.strptime(curr_start_time, "%Y-%m-%dT%H:%M:%SZ")

            if not curr_end_time:
                handover_days = schedule_data.get("handover_interval_days")
                curr_end_time = curr_start_time + timedelta(days=handover_days)

            new_event = UserEvent(name, curr_start_time, curr_end_time)
            schedule_lst.append(new_event)

            curr_start_time = curr_start_time + timedelta(days=handover_days)
            curr_end_time = curr_end_time + timedelta(days=handover_days)

        return schedule_lst
    
    def read_override_file(self):
        override_lst = []
        with open(self.override_file, 'r') as f:
            override_data = json.load(f)

        for user in override_data:
            name = user.get("user")
            start_time = user.get("start_at")
            start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
            end_time = user.get("end_at")
            end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
            new_override_event = UserEvent(name, start_time_dt, end_time_dt)
            override_lst.append(new_override_event)

        return override_lst
    
    def write_to_output_file(self, schedule_queue):
        output_data = []
        for schedule_event in schedule_queue:
            start_time = schedule_event.start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_time = schedule_event.end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
            final_event = {"name" : schedule_event.name, "start_at" : start_time, "end_at" : end_time}
            output_data.append(final_event)

        with open(self.output_file, "w") as f:
            json.dump(output_data, f, indent=2)
    
    def _validate_input(self, name, start_time, end_time):
        return name, start_time, end_time
    
        
