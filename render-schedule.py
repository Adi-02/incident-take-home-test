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

    output_file_name = "output.json"
    file_handler = FileHandler(schedule_file, overrides_file, output_file_name)

    schedule_lst = file_handler.read_schedule_file()
    override_lst = file_handler.read_override_file()

    start_time_dt = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%SZ")
    end_time_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%SZ")
    engine = SchedulingEngine(schedule_lst, override_lst, start_time_dt, end_time_dt)

    engine.override_schedule_queue()

    final_schedule_queue = engine.events_combiner()
    file_handler.write_to_output_file(final_schedule_queue)

if __name__ == "__main__":
    read_stdin()