import unittest
from datetime import datetime, timedelta
from scheduling_engine import SchedulingEngine
from user_event import UserEvent


class TestSchedulingEngine(unittest.TestCase):
    def setUp(self):
        self.empty_engine = SchedulingEngine([], [])

    def _get_dt(self, y, m, d, h):
        return datetime(y, m, d, h)

    def test_append_if_valid_adds_valid_event(self):
        """
        Testing to see if a valid event gets added to the schedule.
        """
        self.empty_engine.schedule_lst = [UserEvent("alice", self._get_dt(2025, 11, 7, 17), self._get_dt(2025, 11, 7, 18))]
        expected = [UserEvent("alice", self._get_dt(2025, 11, 7, 17), self._get_dt(2025, 11, 7, 18))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_append_if_valid_ignores_invalid_event(self):
        """
        Testing to see if an invalid event (like schedules with the same start and end time)
        get added to the schedule.
        """
        self.empty_engine.schedule_lst = [UserEvent("alice", self._get_dt(2025, 11, 7, 17), self._get_dt(2025, 11, 7, 17))]
        expected = []
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_handle_pre_schedule_overrides_before_first_schedule(self):
        """
        Testing to see if an override event happens before the first schedule.
        The assumption is that an override event in this case becomes the first
        event in the final schedule.
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025, 11, 10, 17), self._get_dt(2025, 11, 17, 17))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025, 11, 9, 10), self._get_dt(2025, 11, 10, 10))]
        expected = [UserEvent("alice", self._get_dt(2025, 11, 9, 10), self._get_dt(2025, 11, 10, 10)), 
                    UserEvent("bob", self._get_dt(2025, 11, 10, 17), self._get_dt(2025, 11, 17, 17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_handle_partial_overlap_before_first_schedule(self):
        """
        Testing to see if the overriding event gets added correctly as the first event 
        if part of the overriding schedule overlaps the first schedule.
        """
        self.empty_engine.schedule_lst = [UserEvent("alice", self._get_dt(2025,11,10,15), self._get_dt(2025,11,17,17)), 
                                          UserEvent("bob", self._get_dt(2025,11,10,18), self._get_dt(2025,11,17,19))]
        self.empty_engine.override_lst = [UserEvent("charlie", self._get_dt(2025,11,10,14), self._get_dt(2025,11,10,16))]
        expected = [UserEvent("charlie", self._get_dt(2025,11,10,14), self._get_dt(2025,11,10,16)), 
                    UserEvent("alice", self._get_dt(2025,11,10,16), self._get_dt(2025,11,17,17)), 
                    UserEvent("bob", self._get_dt(2025,11,10,18), self._get_dt(2025,11,17,19))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_merge_main_schedule_override_fully_inside_schedule(self):
        """
        Tests the scenario where the overriding scheduling overlaps a schedule (S1) but 
        the overriding schedules start and end time is between the start and end time 
        of S1.
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025,11,10,17), self._get_dt(2025,11,17,17))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025,11,12,17), self._get_dt(2025,11,13,17))]
        expected = [UserEvent("bob", self._get_dt(2025,11,10,17), self._get_dt(2025,11,12,17)), 
                    UserEvent("alice", self._get_dt(2025,11,12,17), self._get_dt(2025,11,13,17)), 
                    UserEvent("bob", self._get_dt(2025,11,13,17), self._get_dt(2025,11,17,17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_merge_main_schedule_skips_empty_events(self):
        """
        Tests the case where S1.start_time == S1.end_time (Schedule 1) and
        O1.start_time == O1.end_time (Overriding Schedule 1).
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025,11,10,17), self._get_dt(2025,11,10,17))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025,11,10,18), self._get_dt(2025,11,10,18))]
        expected = []
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_override_schedule_queue_no_overlap(self):
        """
        Testing the cases where there is no overlap between schedules and overriding schedules.
        Test to see if they are appeneded to the final list properly.
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025,11,15,17), self._get_dt(2025,11,16,17))]
        expected = [UserEvent("bob", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17)), 
                    UserEvent("alice", self._get_dt(2025,11,15,17), self._get_dt(2025,11,16,17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_override_schedule_queue_with_overlap(self):
        """
        Testing to see if overlapping schedules and overrides work properly.
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17)), 
                                          UserEvent("charlie", self._get_dt(2025,11,14,17), self._get_dt(2025,11,21,17))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025,11,10,17), self._get_dt(2025,11,10,22))]
        expected = [UserEvent("bob", self._get_dt(2025,11,7,17), self._get_dt(2025,11,10,17)), 
                    UserEvent("alice", self._get_dt(2025,11,10,17), self._get_dt(2025,11,10,22)), 
                    UserEvent("bob", self._get_dt(2025,11,10,22), self._get_dt(2025,11,14,17)), 
                    UserEvent("charlie", self._get_dt(2025,11,14,17), self._get_dt(2025,11,21,17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_override_schedule_queue_multiple_overlaps(self):
        """
        Testing to see if overlapping override events work correctly.
        Alice covers 17–20, but Charlie starts at 19 and goes till 22,
        overlapping the end of Alice's shift. Charlie should take precedence.
        E.g.
        s = [(bob, 5pm, 11pm)]
        o = [(alice, 5pm, 8pm), (charlie, 7pm, 10pm)]
        final = [(alice, 5pm, 7pm), (charlie, 7pm, 10pm), (bob, 10pm, 11pm)]
        """
        self.empty_engine.schedule_lst = [UserEvent("bob", self._get_dt(2025,11,8,17), self._get_dt(2025,11,8,23))]
        self.empty_engine.override_lst = [UserEvent("alice", self._get_dt(2025,11,8,17), self._get_dt(2025,11,8,20)), 
                                          UserEvent("charlie", self._get_dt(2025,11,8,19), self._get_dt(2025,11,8,22))]
        expected = [UserEvent("alice", self._get_dt(2025,11,8,17), self._get_dt(2025,11,8,19)), 
                    UserEvent("charlie", self._get_dt(2025,11,8,19), self._get_dt(2025,11,8,22)), 
                    UserEvent("bob", self._get_dt(2025,11,8,22), self._get_dt(2025,11,8,23))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_override_spans_entire_multiple_schedules(self):
        """
        Testing to see if a single override spans across multiple schedules.
        The override completely covers all scheduled events, resulting in a single
        continuous override in the final list.
        E.g.
        s = [(alice, 7pm, 2pm), (bob, 2pm, 9pm), (charlie, 9pm, 4pm)]
        o = [(david, 7pm, 4pm)]
        final = [(david, 7pm, 4pm)]
        """
        s = [UserEvent("alice", self._get_dt(2025,11,7,17), self._get_dt(2025,11,14,17)), 
             UserEvent("bob", self._get_dt(2025,11,14,17), self._get_dt(2025,11,21,17)), 
             UserEvent("charlie", self._get_dt(2025,11,21,17), self._get_dt(2025,11,28,17))]
        o = [UserEvent("david", self._get_dt(2025,11,7,17), self._get_dt(2025,11,28,17))]
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("david", self._get_dt(2025,11,7,17), self._get_dt(2025,11,28,17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)

    def test_override_merges_consecutive_same_user(self):
        """
        Testing to see if consecutive events for the same user merge correctly
        into one continuous segment in the final schedule.
        E.g.
        s = [(alice, 5pm, 6pm), (alice, 6pm, 7pm), (bob, 7pm, 8pm)]
        final = [(alice, 5pm, 7pm), (bob, 7pm, 8pm)]
        """
        s = [UserEvent("alice", self._get_dt(2025,11,7,17), self._get_dt(2025,11,8,17)),
             UserEvent("alice", self._get_dt(2025,11,8,17), self._get_dt(2025,11,9,17)),
             UserEvent("bob", self._get_dt(2025,11,9,17), self._get_dt(2025,11,10,17))]
        o = []
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("alice", self._get_dt(2025,11,7,17), self._get_dt(2025,11,9,17)),
                    UserEvent("bob", self._get_dt(2025,11,9,17), self._get_dt(2025,11,10,17))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_override_handles_empty_final_schedule(self):
        """
        Testing to see if an empty schedule and override list
        return an empty final list as expected.
        E.g.
        s = []
        o = []
        final = []
        """
        s, o = [], []
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = []
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_override_nested_overrides(self):
        """
        Testing to see if nested overrides are handled correctly.
        Bob (8am–8pm), Alice (10am–3pm), and Charlie (12pm–1pm).
        The override within an override should correctly segment
        and restore the schedule in between.
        E.g.
        s = [(bob, 8am, 8pm)]
        o = [(alice, 10am, 3pm), (charlie, 12pm, 1pm)]
        final = [(bob, 8am, 10am), (alice, 10am, 12pm), (charlie, 12pm, 1pm), (alice, 1pm, 3pm), (bob, 3pm, 8pm)]
        """
        s = [UserEvent("bob", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,20))]
        o = [UserEvent("alice", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,15)), 
             UserEvent("charlie", self._get_dt(2025,11,8,12), self._get_dt(2025,11,8,13))]
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("bob", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,10)), 
                    UserEvent("alice", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,12)), 
                    UserEvent("charlie", self._get_dt(2025,11,8,12), self._get_dt(2025,11,8,13)), 
                    UserEvent("alice", self._get_dt(2025,11,8,13), self._get_dt(2025,11,8,15)), 
                    UserEvent("bob", self._get_dt(2025,11,8,15), self._get_dt(2025,11,8,20))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_override_touching_overrides(self):
        """
        Testing to see if touching overrides are handled without overlap.
        Alice ends exactly when Bob starts, so both should appear
        consecutively in the final schedule.
        E.g.
        s = [(base, 8am, 12pm)]
        o = [(alice, 8am, 10am), (bob, 10am, 12pm)]
        final = [(alice, 8am, 10am), (bob, 10am, 12pm)]
        """
        s = [UserEvent("base", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,12))]
        o = [UserEvent("alice", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,10)), 
             UserEvent("bob", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,12))]
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("alice", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,10)), 
                    UserEvent("bob", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,12))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_override_partial_overlap(self):
        """
        Testing to see if partial overlaps are resolved correctly.
        Bob starts while Alice is still active, so the schedule is split
        at the point of overlap.
        E.g.
        s = [(alice, 8am, 12pm)]
        o = [(bob, 10am, 2pm)]
        final = [(alice, 8am, 10am), (bob, 10am, 2pm)]
        """
        s = [UserEvent("alice", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,12))]
        o = [UserEvent("bob", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,14))]
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("alice", self._get_dt(2025,11,8,8), self._get_dt(2025,11,8,10)), 
                    UserEvent("bob", self._get_dt(2025,11,8,10), self._get_dt(2025,11,8,14))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)


    def test_override_multiday_chained_overrides(self):
        """
        Testing to see if multi-day chained overrides are processed correctly.
        Overlapping and consecutive overrides should produce a sequence with
        clear boundaries and restored segments where appropriate.
        E.g.
        s = [(alice, 7am, 2pm)]
        o = [(bob, 9am, 11am), (charlie, 10am, 1pm)]
        final = [(alice, 7am, 9am), (bob, 9am, 10am), (charlie, 10am, 1pm), (alice, 1pm, 2pm)]
        """
        s = [UserEvent("alice", self._get_dt(2025,11,7,7), self._get_dt(2025,11,7,14))]
        o = [UserEvent("bob", self._get_dt(2025,11,7,9), self._get_dt(2025,11,7,11)), 
             UserEvent("charlie", self._get_dt(2025,11,7,10), self._get_dt(2025,11,7,13))]
        self.empty_engine.schedule_lst, self.empty_engine.override_lst = s, o
        expected = [UserEvent("alice", self._get_dt(2025,11,7,7), self._get_dt(2025,11,7,9)),
                    UserEvent("bob", self._get_dt(2025,11,7,9), self._get_dt(2025,11,7,10)),
                    UserEvent("charlie", self._get_dt(2025,11,7,10), self._get_dt(2025,11,7,13)),
                    UserEvent("alice", self._get_dt(2025,11,7,13), self._get_dt(2025,11,7,14))]
        actual = self.empty_engine.override_schedule_queue()
        self.assertListEqual(expected, actual)




if __name__ == "__main__":
    unittest.main()
