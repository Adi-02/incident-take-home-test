import unittest
from datetime import datetime, timedelta
from scheduling_engine import SchedulingEngine
from user_event import UserEvent


class TestSchedulingEngine(unittest.TestCase):
    def setUp(self):
        self.t = lambda y, m, d, h=0: datetime(y, m, d, h)
        self.empty_engine = SchedulingEngine([], [])

    # ----------------------------------------------------------------------
    # Utility and helper methods
    # ----------------------------------------------------------------------

    def test_append_if_valid_adds_valid_event(self):
        e = UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 7, 18))
        events = []
        self.empty_engine._append_if_valid(events, e)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "alice")

    def test_append_if_valid_ignores_invalid_event(self):
        e = UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 7, 17))
        events = []
        self.empty_engine._append_if_valid(events, e)
        self.assertEqual(len(events), 0)

    # ----------------------------------------------------------------------
    # Pre-schedule and partial overlap tests
    # ----------------------------------------------------------------------

    def test_handle_pre_schedule_overrides_before_first_schedule(self):
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 9, 10), self.t(2025, 11, 10, 10))]
        eng = SchedulingEngine(s, o)
        final = []
        p2 = eng._handle_pre_schedule_overrides(final)
        self.assertEqual(p2, 1)
        self.assertEqual(final[0].name, "alice")

    def test_handle_partial_overlap_before_first_schedule(self):
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 10, 10), self.t(2025, 11, 10, 18))]
        eng = SchedulingEngine(s, o)
        final = []
        p2 = eng._handle_partial_overlap_before_first_schedule(final, 0)
        self.assertEqual(final[0].end_time, self.t(2025, 11, 10, 17))
        self.assertEqual(o[0].start_time, self.t(2025, 11, 10, 17))
        self.assertEqual(p2, 0)

    # ----------------------------------------------------------------------
    # Merge main schedule tests
    # ----------------------------------------------------------------------

    def test_merge_main_schedule_override_fully_inside_schedule(self):
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 12, 17), self.t(2025, 11, 13, 17))]
        eng = SchedulingEngine(s, o)
        final = []
        eng._merge_main_schedule(final, 0, 0)
        self.assertEqual(len(final), 3)
        self.assertEqual([e.name for e in final], ["bob", "alice", "bob"])

    def test_merge_main_schedule_skips_empty_events(self):
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 10, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 10, 18), self.t(2025, 11, 10, 18))]
        eng = SchedulingEngine(s, o)
        final = []
        p1, p2 = eng._merge_main_schedule(final, 0, 0)
        self.assertEqual(len(final), 0)
        self.assertIsInstance(p1, int)
        self.assertIsInstance(p2, int)

    # ----------------------------------------------------------------------
    # Append remaining tests
    # ----------------------------------------------------------------------

    def test_append_remaining_adds_leftovers(self):
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 18, 17), self.t(2025, 11, 19, 17))]
        eng = SchedulingEngine(s, o)
        final = []
        eng._append_remaining(final, 0, 0)
        self.assertEqual(len(final), 2)
        self.assertEqual(set(e.name for e in final), {"bob", "alice"})

    # ----------------------------------------------------------------------
    # Full override_schedule_queue Integration Tests
    # ----------------------------------------------------------------------

    def test_override_schedule_queue_no_overlap(self):
        s = [UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 15, 17), self.t(2025, 11, 16, 17))]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        self.assertEqual(users, ["bob", "alice"])

    def test_override_schedule_queue_with_overlap(self):
        s = [
            UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17)),
            UserEvent("charlie", self.t(2025, 11, 14, 17), self.t(2025, 11, 21, 17)),
        ]
        o = [UserEvent("alice", self.t(2025, 11, 10, 17), self.t(2025, 11, 10, 22))]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        self.assertIn("alice", users)
        self.assertIn("bob", users)

    def test_override_schedule_queue_multiple_overrides(self):
        s = [UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17))]
        o = [
            UserEvent("alice", self.t(2025, 11, 8, 17), self.t(2025, 11, 8, 19)),
            UserEvent("charlie", self.t(2025, 11, 9, 17), self.t(2025, 11, 9, 22)),
        ]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        self.assertIn("alice", users)
        self.assertIn("charlie", users)

    # ----------------------------------------------------------------------
    # Edge and large tests
    # ----------------------------------------------------------------------

    def test_override_spans_entire_multiple_schedules(self):
        s = [
            UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17)),
            UserEvent("bob", self.t(2025, 11, 14, 17), self.t(2025, 11, 21, 17)),
            UserEvent("charlie", self.t(2025, 11, 21, 17), self.t(2025, 11, 28, 17))
        ]
        o = [UserEvent("david", self.t(2025, 11, 7, 17), self.t(2025, 11, 28, 17))]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        # Expect override covers all schedules (after merge)
        self.assertEqual(users, ["david"])

    def test_events_combiner_merges_consecutive_same_user(self):
        s = [
            UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 8, 17)),
            UserEvent("alice", self.t(2025, 11, 8, 17), self.t(2025, 11, 9, 17)),
            UserEvent("bob", self.t(2025, 11, 9, 17), self.t(2025, 11, 10, 17))
        ]
        eng = SchedulingEngine([], [])
        eng.final_schedule = s
        merged = eng.events_combiner()
        self.assertEqual(len(merged), 2)
        self.assertEqual(merged[0].name, "alice")
        self.assertEqual(merged[0].end_time, self.t(2025, 11, 9, 17))

    def test_events_combiner_handles_empty_final_schedule(self):
        eng = SchedulingEngine([], [])
        merged = eng.events_combiner()
        self.assertEqual(merged, [])


if __name__ == "__main__":
    unittest.main()
