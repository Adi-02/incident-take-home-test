import unittest
import json
import tempfile
import os
from datetime import datetime
from file_handler import FileHandler
from user_event import UserEvent


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        # Temporary directory to hold JSON test files
        self.tmpdir = tempfile.TemporaryDirectory()

        # Common test file paths
        self.schedule_file = os.path.join(self.tmpdir.name, "schedule.json")
        self.override_file = os.path.join(self.tmpdir.name, "override.json")
        self.output_file = os.path.join(self.tmpdir.name, "output.json")

        # Default schedule data
        self.schedule_data = {
            "users": ["alice", "bob"],
            "handover_start_at": "2025-11-07T17:00:00Z",
            "handover_interval_days": 7
        }

        # Default override data
        self.override_data = [
            {
                "user": "charlie",
                "start_at": "2025-11-10T17:00:00Z",
                "end_at": "2025-11-10T22:00:00Z"
            }
        ]

        # Write default JSONs
        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule_data, f)

        with open(self.override_file, "w") as f:
            json.dump(self.override_data, f)

        # Initialize FileHandler
        self.handler = FileHandler(
            self.schedule_file, self.override_file, self.output_file
        )

    def tearDown(self):
        self.tmpdir.cleanup()

    # ---------- Helper Tests ----------

    def test_convert_str_to_datetime_valid(self):
        dt = self.handler._convert_str_to_datetime("2025-11-07T17:00:00Z")
        self.assertIsInstance(dt, datetime)
        self.assertEqual(dt.year, 2025)

    def test_convert_str_to_datetime_invalid(self):
        self.assertIsNone(self.handler._convert_str_to_datetime("invalid-date"))

    def test_validate_input_valid(self):
        name, start, end = self.handler._validate_input(
            "bob", "2025-11-07T17:00:00Z", "2025-11-08T17:00:00Z"
        )
        self.assertEqual(name, "bob")
        self.assertLess(start, end)

    def test_validate_input_invalid(self):
        name, start, end = self.handler._validate_input(
            123, "invalid", "2025-11-07T17:00:00Z"
        )
        self.assertIsNone(name)
        self.assertIsNone(start)
        self.assertIsNone(end)

    # ---------- read_schedule_file Tests ----------

    def test_read_schedule_file_generates_correct_events(self):
        events = self.handler.read_schedule_file(
            "2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z"
        )
        self.assertEqual(len(events), 2)
        self.assertIsInstance(events[0], UserEvent)
        self.assertEqual(events[0].name, "alice")
        self.assertEqual(events[1].name, "bob")

    def test_read_schedule_file_truncates_properly(self):
        events = self.handler.read_schedule_file(
            "2025-11-10T17:00:00Z", "2025-11-21T17:00:00Z"
        )
        # Only truncated Alice + Bob shift should appear
        self.assertEqual(len(events), 2)
        self.assertGreaterEqual(events[0].start_time, datetime(2025, 11, 10, 17, 0))
        self.assertLessEqual(events[-1].end_time, datetime(2025, 11, 21, 17, 0))

    def test_read_schedule_file_invalid_interval(self):
        # Overwrite file with invalid interval
        with open(self.schedule_file, "w") as f:
            json.dump({"users": ["a"], "handover_start_at": "2025-11-07T17:00:00Z", "handover_interval_days": 0}, f)
        with self.assertRaises(ValueError):
            self.handler.read_schedule_file("2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z")

    # ---------- read_override_file Tests ----------

    def test_read_override_file_generates_correct_events(self):
        events = self.handler.read_override_file(
            "2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z"
        )
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "charlie")
        self.assertEqual(events[0].start_time, datetime(2025, 11, 10, 17, 0))

    def test_read_override_file_truncates_events(self):
        overrides = [
            {
                "user": "charlie",
                "start_at": "2025-11-06T17:00:00Z",
                "end_at": "2025-11-08T17:00:00Z"
            }
        ]
        with open(self.override_file, "w") as f:
            json.dump(overrides, f)

        events = self.handler.read_override_file(
            "2025-11-07T17:00:00Z", "2025-11-09T17:00:00Z"
        )
        # should truncate to 2025-11-07T17:00:00Z
        self.assertEqual(events[0].start_time, datetime(2025, 11, 7, 17, 0))

    def test_read_override_file_invalid_entry(self):
        with open(self.override_file, "w") as f:
            json.dump([{"user": None, "start_at": "bad", "end_at": "bad"}], f)
        events = self.handler.read_override_file(
            "2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z"
        )
        self.assertEqual(len(events), 0)

    # ---------- write_to_output_file Tests ----------

    def test_write_to_output_file_creates_valid_json(self):
        # Create a fake schedule
        schedule = [
            UserEvent("alice", datetime(2025, 11, 7, 17, 0), datetime(2025, 11, 14, 17, 0))
        ]
        self.handler.write_to_output_file(schedule)
        with open(self.output_file, "r") as f:
            data = json.load(f)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "alice")
        self.assertIn("start_at", data[0])
        self.assertIn("end_at", data[0])


if __name__ == "__main__":
    unittest.main()
