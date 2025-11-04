import argparse
from file_handler import FileHandler
from scheduling_engine import SchedulingEngine
from datetime import datetime

def read_stdin():
    parser = argparse.ArgumentParser(description="Render schedule with overrides")

    parser.add_argument("--schedule", required=True)
    parser.add_argument("--overrides", required=True)
    parser.add_argument("--from", dest="from_time", required=True)
    parser.add_argument("--until", required=True)

    args = parser.parse_args()

    schedule_file = args.schedule
    overrides_file = args.overrides
    start_time = args.from_time 
    end_time = args.until

    # print(f"Schedule File: {schedule_file}, Overrides File: {overrides_file}, Start Time: {start_time}, End Time: {end_time}")
    output_file_name = "output.json"
    file_handler = FileHandler(schedule_file, overrides_file, output_file_name)

    schedule_lst = file_handler.read_schedule_file()
    override_lst = file_handler.read_override_file()

    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
    engine = SchedulingEngine(schedule_lst, override_lst, start_time_dt, end_time_dt)

    engine.override_schedule_queue()
    

    final_schedule_queue = engine.final_schedule
    file_handler.write_to_output_file(final_schedule_queue)

    # # You can parse the datetimes if you want:
    # start = datetime.fromisoformat(args.from_time.replace("Z", "+00:00"))
    # end = datetime.fromisoformat(args.until.replace("Z", "+00:00"))
    # print(f"Parsed start: {start}, end: {end}")

if __name__ == "__main__":
    read_stdin()