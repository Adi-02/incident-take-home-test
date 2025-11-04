from user_event import UserEvent
class SchedulingEngine:
    def __init__(self, schedule_lst, override_lst, schedule_start, schedule_end):
        self.schedule_lst = schedule_lst
        self.override_lst = override_lst
        self.schedule_start = schedule_start
        self.schedule_end = schedule_end
        self.final_schedule = []


    def _truncate_events(self, events_lst):
        for event in events_lst:
            if event.start_time < self.schedule_start:
                event.start_time = self.schedule_start
            if event.end_time > self.schedule_end:
                event.end_time = self.schedule_end

    def override_schedule_queue(self):
        # Truncate Schedule Time 
        self._truncate_events(self.schedule_lst)
        
        # Truncate Override Time 
        self._truncate_events(self.override_lst)

        p1, p2 = 0, 0

        # All the overrides before the main schedule starts
        while p2 < len(self.override_lst) and self.override_lst[p2].end_time <= self.schedule_lst[0].start_time:
            self.final_schedule.append(self.override_lst[p2])
            p2 += 1

        # End_time of p2 must overlap (inbetween p1.start_time and p1.end_time) -> truncate
        if p2 < len(self.override_lst) and self.override_lst[p2].start_time < self.schedule_lst[0].start_time:
            initial_o = UserEvent(self.override_lst[p2].name, self.override_lst[p2].start_time, self.schedule_lst[0].start_time)
            self.final_schedule.append(initial_o)
            self.override_lst[p2].start_time = self.schedule_lst[0].start_time
        
        while p1 < len(self.schedule_lst) and p2 < len(self.override_lst):
            s_start, s_end = self.schedule_lst[p1].start_time, self.schedule_lst[p1].end_time
            o_start, o_end = self.override_lst[p2].start_time, self.override_lst[p2].end_time
            s_name = self.schedule_lst[p1].name
            o_event = self.override_lst[p2]
            if s_start == s_end:
                p1 += 1
                continue 
            if o_start == o_end:
                p2 += 1
                continue

            # Case 1: Inside one schedule
            if s_start <= o_start < o_end <= s_end:
                if s_start < o_start:
                    before_schedule = UserEvent(s_name, s_start, o_start)
                    self.final_schedule.append(before_schedule)
                self.final_schedule.append(o_event)
                p2 += 1 # Override event fully consumed
                if o_end < s_end:
                    after_schedule = UserEvent(s_name, o_end, s_end)
                    self.final_schedule.append(after_schedule)
                p1 += 1
            else: # Case 2: Between two schedules
                if s_start < o_start:
                    before_schedule = UserEvent(s_name, s_start, o_start)
                    self.final_schedule.append(before_schedule)
                p1 += 1 # Current schedule has been consumed
                partial_o = UserEvent(o_event.name, o_start, s_end)
                self.final_schedule.append(partial_o)
                o_event.start_time = s_end 

        while p1 < len(self.schedule_lst):
            s_event = self.schedule_lst[p1]
            if s_event.start_time < s_event.end_time:
                self.final_schedule.append(s_event)
            p1 += 1
        
        while p2 < len(self.override_lst):
            o_event = self.override_lst[p2]
            if o_event.start_time < o_event.end_time:
                self.final_schedule.append(o_event)
            p2 += 1

    def events_combiner(self):
        output_lst = []
        i = 1
        prev_event = self.final_schedule[0] if len(self.final_schedule) >= 1 else None
        while i < len(self.final_schedule):
            curr_event = self.final_schedule[i]
            if prev_event.name == curr_event.name:
                prev_event.end_time = curr_event.end_time 
            else:
                output_lst.append(prev_event)
                prev_event = curr_event

            i += 1

        output_lst.append(prev_event)

        return output_lst

            

