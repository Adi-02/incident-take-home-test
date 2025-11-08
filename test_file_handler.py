import unittest
import json
import tempfile
import os
from datetime import datetime
from file_handler import FileHandler
from user_event import UserEvent


class TestFileHandler(unittest.TestCase):

    def setUp(self):
        """
        Create temporary JSON files for schedule, override, and output.
        Each test uses default schedule and override data written to these files.
        Initializes FileHandler with the generated paths.
        """
        self.tmpdir = tempfile.TemporaryDirectory()
        self.schedule_file = os.path.join(self.tmpdir.name, "schedule.json")
        self.override_file = os.path.join(self.tmpdir.name, "override.json")
        self.output_file = os.path.join(self.tmpdir.name, "output.json")

        self.schedule_data = {"users": ["alice", "bob"], "handover_start_at": "2025-11-07T17:00:00Z", "handover_interval_days": 7}
        self.override_data = [{"user": "charlie","start_at": "2025-11-10T17:00:00Z","end_at": "2025-11-10T22:00:00Z"}]

        with open(self.schedule_file, "w") as f:
            json.dump(self.schedule_data, f)
        with open(self.override_file, "w") as f:
            json.dump(self.override_data, f)

        self.handler = FileHandler(self.schedule_file, self.override_file, self.output_file)


    def tearDown(self):
        self.tmpdir.cleanup()

    def _get_dt(self, y : int, m : int, d : int, h : int) -> datetime:
        """
        Get date time object 
        """
        return datetime(y, m, d, h)

    def test_read_schedule_file_generates_valid_events(self):
        """
        Testing schedule generation and truncation within range.
        """
        result = self.handler.read_schedule_file("2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z")
        expected = [UserEvent("alice", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17)),
                    UserEvent("bob", self._get_dt(2025,11,14,17), self._get_dt(2025,11,21,17))]
        self.assertListEqual(expected, result)

    def test_read_schedule_file_invalid_date_range_raises(self):
        """
        Testing invalid date range raises ValueError.
        """
        with self.assertRaises(ValueError):
            self.handler.read_schedule_file("2025-11-10T17:00:00Z", "2025-11-07T17:00:00Z")

    def test_read_override_file_truncates_correctly(self):
        """
        Testing override reading and truncation within range.
        """
        result = self.handler.read_override_file("2025-11-07T17:00:00Z", "2025-11-21T17:00:00Z")
        expected = [UserEvent("charlie", self._get_dt(2025,11,10,17), self._get_dt(2025,11,10,22))]
        self.assertListEqual(expected, result)

    def test_read_override_file_invalid_range_raises(self):
        """
        Testing invalid override time range raises ValueError.
        """
        with self.assertRaises(ValueError):
            self.handler.read_override_file("2025-11-10T17:00:00Z", "2025-11-07T17:00:00Z")

    def test_write_to_output_file_creates_valid_json(self):
        """
        Testing writing schedule queue to output file.
        """
        schedule_queue = [UserEvent("alice", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17)),
                          UserEvent("bob", self._get_dt(2025,11,14,17), self._get_dt(2025,11,21,17))]
        self.handler.write_to_output_file(schedule_queue)

        with open(self.output_file, "r") as f:
            data = json.load(f)

        expected = [{"name": "alice", "start_at": self._get_dt(2025,11,7,17), "end_at": self._get_dt(2025,11,14,17)},
                    {"name": "bob", "start_at": self._get_dt(2025,11,14,17), "end_at": self._get_dt(2025,11,21,17)}]

        for i, d in enumerate(data):
            self.assertEqual(d["user"], expected[i]["name"])


if __name__ == "__main__":
    unittest.main()
