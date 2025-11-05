import argparse
from file_handler import FileHandler
from scheduling_engine import SchedulingEngine
from datetime import datetime

def read_stdin():
    # Parse input arguments
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

    # File Handler
    output_file_name = "output.json"
    file_handler = FileHandler(schedule_file, overrides_file, output_file_name)
    schedule_lst = file_handler.read_schedule_file(start_time, end_time)
    override_lst = file_handler.read_override_file(start_time, end_time)

    # Scheduling Engine
    engine = SchedulingEngine(schedule_lst, override_lst)
    engine.override_schedule_queue()
    final_schedule_queue = engine.events_combiner()

    # Write to output json
    file_handler.write_to_output_file(final_schedule_queue)

if __name__ == "__main__":
    read_stdin()