from user_event import UserEvent

class SchedulingEngine:
    def __init__(self, schedule_lst : list[UserEvent], override_lst : list[UserEvent]) -> None:
        self.schedule_lst = schedule_lst
        self.override_lst = override_lst
        self.final_schedule = []

    def _append_if_valid(self, event_list : list[UserEvent], event : UserEvent) -> None:
        """
        Ignore events if they have the same start and end time
        """
        if event.start_time < event.end_time:
            event_list.append(event)

    def _handle_pre_schedule_overrides(self, final : list[UserEvent]) -> int:
        """
        Add override tasks that start before the first scheduled task 
        """
        p2 = 0
        schedules, overrides = self.schedule_lst, self.override_lst
        while p2 < len(overrides) and overrides[p2].end_time <= schedules[0].start_time:
            self._append_if_valid(final, overrides[p2])
            p2 += 1
        return p2

    def _handle_partial_overlap_before_first_schedule(self, final : list[UserEvent], p2 : int) -> int:
        """
        Handle an override that partially overlaps before the first scheduled task
        """
        schedules, overrides = self.schedule_lst, self.override_lst
        if p2 < len(overrides) and overrides[p2].start_time < schedules[0].start_time:
            o = overrides[p2]
            self._append_if_valid(final, o)
            o.start_time = o.end_time
        return p2
    
    def _resolve_override_overlaps(self) -> None:
        """
        Adjust override_lst so no two overrides overlap.
        If overlap occurs, the later override takes precedence,
        and the earlier one is split into non-overlapping pieces.
        """
        overrides = sorted(self.override_lst, key=lambda e: e.start_time)
        result = []

        for o in overrides:
            # Compare with previous overrides in result
            i = 0
            while i < len(result):
                r = result[i]
                if o.start_time < r.end_time and o.end_time > r.start_time:
                    # Overlap detected
                    if o.start_time > r.start_time:
                        # Keep left non-overlapping segment
                        result.insert(i, UserEvent(r.name, r.start_time, o.start_time))
                        i += 1
                    if o.end_time < r.end_time:
                        # Keep right non-overlapping segment
                        result.insert(i + 1, UserEvent(r.name, o.end_time, r.end_time))
                    # Remove the overlapped event
                    result.pop(i)
                    # Do not increment i (recheck with next)
                else:
                    i += 1
            result.append(o)

        # Sort again for safety
        result.sort(key=lambda e: e.start_time)
        self.override_lst = result


    def _merge_main_schedule(self, final : list[UserEvent], p1 : int, p2 : int) -> tuple[int,int]:
        """
        Merging schedules and overrides if and when they overlap
        """
        schedules, overrides = self.schedule_lst, self.override_lst

        while p1 < len(schedules) and p2 < len(overrides):
            s, o = schedules[p1], overrides[p2]
            s_start, s_end = s.start_time, s.end_time
            o_start, o_end = o.start_time, o.end_time

            # Skip empty events
            if s_start == s_end:
                p1 += 1
                continue
            if o_start == o_end:
                p2 += 1
                continue

            # Case 1: Override fully inside schedule
            if s_start <= o_start < o_end <= s_end:
                self._append_if_valid(final, UserEvent(s.name, s_start, o_start))  # before
                self._append_if_valid(final, o)                                   # override
                self._append_if_valid(final, UserEvent(s.name, o_end, s_end))     # after
                p1 += 1
                p2 += 1
            else:
                # Case 2: Override spans multiple schedules
                self._append_if_valid(final, UserEvent(s.name, s_start, o_start))
                self._append_if_valid(final, UserEvent(o.name, o_start, s_end))
                o.start_time = s_end
                p1 += 1

        return p1, p2

    def _append_remaining(self, final : list[UserEvent], p1 : int, p2 : int) -> None:
        """
        Add any remaining schedules or overrides.
        """
        schedules, overrides = self.schedule_lst, self.override_lst
        while p1 < len(schedules):
            self._append_if_valid(final, schedules[p1])
            p1 += 1
        while p2 < len(overrides):
            self._append_if_valid(final, overrides[p2])
            p2 += 1

    def override_schedule_queue(self) -> list[UserEvent]:
        """
        Handles the logic for generating the schedule queue
        """
        final = self.final_schedule
        p1, p2 = 0, 0

        if len(self.schedule_lst) == 0 and len(self.override_lst) == 0:
            return
        
        # Resolves any event overlaps in the list of override events
        self._resolve_override_overlaps()
        
        if len(self.schedule_lst) == 0 and len(self.override_lst) > 0:
            final = self.override_lst
            return 

        # Handle overrides that start just before or end between the first and second schedule
        p2 = self._handle_pre_schedule_overrides(final)
        p2 = self._handle_partial_overlap_before_first_schedule(final, p2)

        # Handle overrides that happen in between schedules 
        p1, p2 = self._merge_main_schedule(final, p1, p2)

        # Remaining overrides and schedules get appended
        self._append_remaining(final, p1, p2)

        # Combine the events
        final_schedule_merged = self.events_combiner()
        return final_schedule_merged

    def events_combiner(self) -> list[UserEvent]:
        """
        Combine consecutive events with the same name (due partial events being created)
        E.g. [(A, 3pm, 5pm), (C, 5pm, 6pm), (C, 6pm, 7pm), (B, 7pm, 9pm)]
        gets converted to -> [(A, 3pm, 5pm), (C, 5pm, 7pm), (B, 7pm, 9pm)]
        """
        if not self.final_schedule:
            return []

        merged = []
        prev = self.final_schedule[0]

        for curr in self.final_schedule[1:]:
            if curr.name == prev.name:
                prev.end_time = curr.end_time
            else:
                merged.append(prev)
                prev = curr

        merged.append(prev)
        return merged
