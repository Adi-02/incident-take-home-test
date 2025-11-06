import unittest
from datetime import datetime, timedelta
from scheduling_engine import SchedulingEngine
from user_event import UserEvent


class TestSchedulingEngine(unittest.TestCase):
    def setUp(self):
        self.t = lambda y, m, d, h=0: datetime(y, m, d, h)
        self.empty_engine = SchedulingEngine([], [])

    def test_append_if_valid_adds_valid_event(self):
        """
        Testing to see if a valid event gets added to the schedule
        """
        e = UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 7, 18))
        events = []
        self.empty_engine._append_if_valid(events, e)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].name, "alice")

    def test_append_if_valid_ignores_invalid_event(self):
        """
        Testing to see if an invalid event (like schedules with the same start and end time)
        get added to the schedule
        """
        e = UserEvent("alice", self.t(2025, 11, 7, 17), self.t(2025, 11, 7, 17))
        events = []
        self.empty_engine._append_if_valid(events, e)
        self.assertEqual(len(events), 0)

    def test_handle_pre_schedule_overrides_before_first_schedule(self):
        """
        Testing to see if an override event happens before the first schedule
        The assumption is that an override event in this case ends up becoming the first schedule 
        in the final schedule
        """
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 9, 10), self.t(2025, 11, 10, 10))]
        eng = SchedulingEngine(s, o)
        final = []
        p2 = eng._handle_pre_schedule_overrides(final)
        self.assertEqual(p2, 1)
        self.assertEqual(final[0].name, "alice")

    def test_handle_partial_overlap_before_first_schedule(self):
        """
        Testing to see if the overriding event gets added correctly as the first event 
        if part of the overriding schedule overlaps the first schedule
        """
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 10, 10), self.t(2025, 11, 10, 18))]
        eng = SchedulingEngine(s, o)
        final = []
        p2 = eng._handle_partial_overlap_before_first_schedule(final, 0)
        self.assertEqual(final[0].end_time, self.t(2025, 11, 10, 18))
        self.assertEqual(o[0].start_time, self.t(2025, 11, 10, 18))
        self.assertEqual(p2, 0)

    def test_merge_main_schedule_override_fully_inside_schedule(self):
        """
        Tests the scenario where the overriding scheduling overlaps a schedule (S1) but 
        the overriding schedules start and end time is between the start and end time 
        of S1
        """
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 17, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 12, 17), self.t(2025, 11, 13, 17))]
        eng = SchedulingEngine(s, o)
        final = []
        eng._merge_main_schedule(final, 0, 0)
        self.assertEqual(len(final), 3)
        self.assertEqual([e.name for e in final], ["bob", "alice", "bob"])

    def test_merge_main_schedule_skips_empty_events(self):
        """
        Tests the case where S1.start_time == S1.end_time (Schedule 1) and
        O1.start_time == O1.end_time (Overriding Schedule 1)
        """
        s = [UserEvent("bob", self.t(2025, 11, 10, 17), self.t(2025, 11, 10, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 10, 18), self.t(2025, 11, 10, 18))]
        eng = SchedulingEngine(s, o)
        final = []
        p1, p2 = eng._merge_main_schedule(final, 0, 0)
        self.assertEqual(len(final), 0)
        self.assertIsInstance(p1, int)
        self.assertIsInstance(p2, int)

    def test_override_schedule_queue_no_overlap(self):
        """
        Testing the cases where there is no overlap between schedules and overriding schedules 
        Test to see if they are appeneded to the final list properly
        """
        s = [UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 15, 17), self.t(2025, 11, 16, 17))]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        self.assertEqual(users, ["bob", "alice"])

    def test_override_schedule_queue_with_overlap(self):
        """
        Testing to see if overlapping schedules and overrides work properly
        """
        s = [UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17)), UserEvent("charlie", self.t(2025, 11, 14, 17), self.t(2025, 11, 21, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 10, 17), self.t(2025, 11, 10, 22))]
        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]
        self.assertIn("alice", users)
        self.assertIn("bob", users)

    def test_override_schedule_queue_multiple_overlaps(self):
        """
        Test overlapping overrides:
        Alice covers 8–20, but Charlie starts at 19 and goes till 22,
        overlapping the end of Alice's shift. Charlie should take precedence.
        """
        s = [UserEvent("bob", self.t(2025, 11, 7, 17), self.t(2025, 11, 14, 17))]
        o = [UserEvent("alice", self.t(2025, 11, 8, 17), self.t(2025, 11, 8, 20)), UserEvent("charlie", self.t(2025, 11, 8, 19), self.t(2025, 11, 8, 22))]

        eng = SchedulingEngine(s, o)
        result = eng.override_schedule_queue()
        users = [e.name for e in result]

        # Expect both Alice and Charlie to appear
        self.assertIn("alice", users)
        self.assertIn("charlie", users)

        # Find exact ordering (Charlie should override Alice's tail)
        segments = [(e.name, e.start_time.hour, e.end_time.hour) for e in result]
        print("\nSegments:", segments)

        # Verify Alice’s override ends when Charlie begins
        alice_end = next(e.end_time for e in result if e.name == "alice")
        charlie_start = next(e.start_time for e in result if e.name == "charlie")
        self.assertEqual(alice_end, charlie_start)

        # Ensure no duplicate overlap segments
        for i in range(1, len(result)):
            self.assertLessEqual(result[i - 1].end_time, result[i].start_time)


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
