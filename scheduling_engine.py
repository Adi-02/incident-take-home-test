from user_event import UserEvent

class SchedulingEngine:
    def __init__(self, schedule_lst : list[UserEvent], override_lst : list[UserEvent]) -> None:
        self.schedule_lst = schedule_lst
        self.override_lst = override_lst
        self.final_schedule = []

    def _append_if_valid(self, event_list : list[UserEvent], event : UserEvent) -> None:
        """
        Append an event to a list only if it represents a valid time range.
        Ignore events if they have identical start and end times as they represent 
        zero-duration (invalid) intervals.
        """
        if event.start_time < event.end_time:
            event_list.append(event)

    def _handle_pre_schedule_overrides(self, final : list[UserEvent]) -> int:
        """
        Add override events that finish before the first scheduled event
        E.g.
        s = [(A, 3pm, 5pm), (B, 6pm, 7pm)] 
        o = [(C, 2pm, 3pm)]
        final = [(C, 2pm, 3pm), (A, 3pm, 5pm), (B, 6pm, 7pm)]
        """
        over_ptr = 0
        schedules, overrides = self.schedule_lst, self.override_lst
        while over_ptr < len(overrides) and overrides[over_ptr].end_time <= schedules[0].start_time:
            self._append_if_valid(final, overrides[over_ptr])
            over_ptr += 1
        return over_ptr

    def _handle_partial_overlap_before_first_schedule(self, final : list[UserEvent], over_ptr : int) -> int:
        """
        Handle an override that partially overlaps before the first scheduled task.
        The overriding event always takes precedence
        E.g.
        s = [(A, 3pm, 5pm), (B, 6pm, 7pm)] 
        o = [(C, 2pm, 4pm)]
        final = [(C, 2pm, 4pm), (A, 4pm, 5pm), (B, 6pm, 7pm)]
        """
        schedules, overrides = self.schedule_lst, self.override_lst
        if over_ptr < len(overrides) and overrides[over_ptr].start_time < schedules[0].start_time:
            o = overrides[over_ptr]
            self._append_if_valid(final, o)
            schedules[0].start_time = o.end_time
        return over_ptr
    
    def _resolve_override_overlaps(self) -> None:
        """
        Remove overlapping override events.
        Later overrides take precedence — earlier ones are split or truncated
        so that no overlaps remain in the final override list.

        Case 1: Override fully contains another override. 
        The earlier override is split into two non-overlapping segments.
        E.g.
        o = [(C, 2pm, 8pm), (D, 4pm, 6pm)]
        o_final = [(C, 2pm, 4pm), (D, 4pm, 6pm), (C, 6pm, 8pm)]

        Case 2: Current override overlaps the end of a previous override.
        The previous override is truncated so it ends where the current override begins.
        E.g.
        o = [(C, 2pm, 5pm), (D, 4pm, 7pm)]
        o_final = [(C, 2pm, 4pm), (D, 4pm, 7pm)]

        Case 3: No overlap between overrides.
        Both overrides remain as-is.
        E.g.
        o = [(C, 2pm, 3pm), (D, 4pm, 5pm)]
        o_final = [(C, 2pm, 3pm), (D, 4pm, 5pm)]

        Case 4: Ignore zero-duration overrides (start_time == end_time).
        These are skipped and not added to the final list.
        E.g.
        o = [(C, 2pm, 3pm), (D, 4pm, 4pm)]
        o_final = [(C, 2pm, 3pm)]
        """
        overrides = sorted(self.override_lst, key=lambda e: e.start_time)
        i = 0
        result = []
        while i < len(overrides):
            first_override = overrides[i]
            if first_override.start_time < first_override.end_time:
                result.append(first_override)
                break 
            i += 1
        
        if len(result) == 0:
            self.override_lst = []
            return
        
        for o_ptr in range(1, len(overrides)):
            prev_o = result[-1]
            curr_o = overrides[o_ptr]
            # Case 1: Ignore zero-duration overrides
            if curr_o.start_time == curr_o.end_time:
                continue
            # Case 2: Current override lies fully within the previous override
            elif prev_o.start_time <= curr_o.start_time < curr_o.end_time <= prev_o.end_time:
                temp_end = prev_o.end_time
                temp_name = prev_o.name
                if prev_o.start_time < curr_o.start_time:
                    prev_o.end_time = curr_o.start_time
                result.append(curr_o)
                if curr_o.end_time < temp_end:
                    after_override = UserEvent(temp_name, curr_o.end_time, temp_end)
                    result.append(after_override)
            # Case 3: Current override extends beyond the previous override
            elif prev_o.start_time <= curr_o.start_time and prev_o.end_time < curr_o.end_time:
                if prev_o.start_time < curr_o.start_time:
                    prev_o.end_time = curr_o.start_time
                    result.append(curr_o)
                else:
                    _ = result.pop()
                    result.append(curr_o)
            # Case 4: No overlap between overrides
            else:
                result.append(curr_o)
            

        self.override_lst = result


    def _merge_main_schedule(self, final : list[UserEvent], sched_ptr : int, over_ptr : int) -> tuple[int,int]:
        """
        Merge the main schedule and override lists when time ranges overlap.
        Each schedule event may be partially or fully replaced by one or more
        override events depending on their overlap relationships.

        Case 1: Override and schedule do not intersect. Both events are appended as-is.
        E.g. 
        s = [(A, 1pm, 2pm)]
        o = [(B, 3pm, 4pm)]
        final = [(A, 1pm, 2pm), (B, 3pm, 4pm)]

        Case 2: The override lies completely within a schedule window. 
        The schedule is split into two parts: before and after the override.
        E.g.
        s = [(A, 1pm, 5pm)]
        o = [(B, 2pm, 4pm)]
        final = [(A, 1pm, 2pm), (B, 2pm, 4pm), (A, 4pm, 5pm)]

        Case 3: The override begins within one schedule and extends into the next. 
        The current schedule's segment is replaced up to its end,
        and the override continues in the next iteration.
        E.g.
        s = [(A, 1pm, 3pm), (C, 3pm, 5pm)]
        o = [(B, 2pm, 4pm)]
        after first merge:
        s = [(C, 3pm, 5pm)] (sched_ptr is incremented so assume previous schedule is no longer visible)
        o = [(B, 3pm, 4pm)]
        final = [(A, 1pm, 2pm), (B, 2pm, 3pm)]
        """
        schedules, overrides = self.schedule_lst, self.override_lst

        while sched_ptr < len(schedules) and over_ptr < len(overrides):
            s, o = schedules[sched_ptr], overrides[over_ptr]
            s_start, s_end = s.start_time, s.end_time
            o_start, o_end = o.start_time, o.end_time

            # Skip empty events
            if s_start == s_end:
                sched_ptr += 1
                continue
            if o_start == o_end:
                over_ptr += 1
                continue

            # Case 1: No overlap
            if o_end < s_start or s_end < o_start:
                self._append_if_valid(final, s)
                sched_ptr += 1
                self._append_if_valid(final, o)
                over_ptr += 1
            # Case 2: Override fully inside schedule
            elif s_start <= o_start < o_end <= s_end:
                self._append_if_valid(final, UserEvent(s.name, s_start, o_start)) 
                self._append_if_valid(final, o)                                 
                schedules[sched_ptr] = UserEvent(s.name, o_end, s_end)
                over_ptr += 1
            # Case 3: Override spans multiple schedules
            else:
                self._append_if_valid(final, UserEvent(s.name, s_start, o_start))
                self._append_if_valid(final, UserEvent(o.name, o_start, s_end))
                o.start_time = s_end
                sched_ptr += 1

        return sched_ptr, over_ptr

    def _append_remaining(self, final : list[UserEvent], sched_ptr : int, over_ptr : int) -> None:
        """
        Add any remaining schedules or overrides.
        E.g. 
        final = [(B, 2pm, 4pm)]
        s = [(A, 4pm, 6pm), (C, 6pm, 7pm)]
        o = []
        after _append_remaining():
        final = [(B, 2pm, 4pm), (A, 4pm, 6pm), (C, 6pm, 7pm)]
        (same logic applies for override if schedule is empty)
        """
        schedules, overrides = self.schedule_lst, self.override_lst
        while sched_ptr < len(schedules):
            self._append_if_valid(final, schedules[sched_ptr])
            sched_ptr += 1
        while over_ptr < len(overrides):
            self._append_if_valid(final, overrides[over_ptr])
            over_ptr += 1

    def override_schedule_queue(self) -> list[UserEvent]:
        """
        Main entry point for generating the final merged schedule.

        Coordinates all helper functions to:
        1. Resolve overlapping overrides
        2. Merge overrides with the base schedule
        3. Append remaining events
        4. Combine consecutive segments.
        """
        final = self.final_schedule
        sched_ptr, over_ptr = 0, 0

        if len(self.schedule_lst) == 0 and len(self.override_lst) == 0:
            return
        
        if len(self.schedule_lst) == 0 and len(self.override_lst) > 0:
            final = self.override_lst
            return 
        
        if len(self.schedule_lst) > 0 and len(self.override_lst) == 0:
            final = self.schedule_lst
            return 
        
        self._resolve_override_overlaps()

        over_ptr = self._handle_pre_schedule_overrides(final)
        over_ptr = self._handle_partial_overlap_before_first_schedule(final, over_ptr)

        sched_ptr, over_ptr = self._merge_main_schedule(final, sched_ptr, over_ptr)

        self._append_remaining(final, sched_ptr, over_ptr)

        final_schedule_merged = self.events_combiner()
        return final_schedule_merged

    def events_combiner(self) -> list[UserEvent]:
        """
        Combine consecutive events with the same name (due partial events being created)
        E.g. 
        final = [(A, 3pm, 5pm), (C, 5pm, 6pm), (C, 6pm, 7pm), (B, 7pm, 9pm)]
        after events_combiner(): 
        final = [(A, 3pm, 5pm), (C, 5pm, 7pm), (B, 7pm, 9pm)]
        """
        if not self.final_schedule:
            return []

        merged = []
        prev = self.final_schedule[0]

        for curr in self.final_schedule[1:]:
            if curr.name == prev.name:
                prev.end_time = curr.end_time
            else:
                if prev.start_time < prev.end_time:
                    merged.append(prev)
                prev = curr
        if prev.start_time < prev.end_time:
            merged.append(prev)
        return merged
