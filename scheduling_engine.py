from user_event import UserEvent
class SchedulingEngine:
    def __init__(self, schedule_lst, override_lst, schedule_start, schedule_end):
        self.schedule_lst = schedule_lst
        self.override_lst = override_lst
        self.schedule_start = schedule_start
        self.schedule_end = schedule_end
        self.final_schedule = []

    def override_schedule_queue(self):
        p1, p2 = 0, 0
        while p1 < len(self.schedule_lst) and p2 < len(self.override_lst): 
            o_start, o_end = self.override_lst[p2].start_time, self.override_lst[p2].end_time
            s_start, s_end = self.schedule_lst[p1].start_time, self.schedule_lst[p1].end_time
            s_name, o_name = self.schedule_lst[p1].name, self.override_lst[p2].name
            s_event, o_event = self.schedule_lst[p1], self.override_lst[p2]
            if o_end <= s_start:
                self.final_schedule.append(self.override_lst[p2])
                p2 += 1
                continue
            if s_end <= o_start:
                self.final_schedule.append(self.schedule_lst[p1])
                p1 += 1
                continue

            # Case 1 
            if s_start < o_start and s_end == o_end:
                before_schedule = UserEvent(s_name, s_start, o_start)
                self.final_schedule.append(before_schedule)
                self.final_schedule.append(o_event)
                p1 += 1
                p2 += 1
            # Case 2
            elif o_end < s_end and s_start == o_start:
                self.final_schedule.append(o_event)
                after_schedule = UserEvent(s_name, o_end, s_end)
                self.final_schedule.append(after_schedule)
                p2 += 1
                p1 += 1
            # Case 3
            elif s_start == o_start and s_end == o_end:
                self.final_schedule.append(o_event)
                p1 += 1
                p2 += 1
            # Case 4
            elif s_start < o_start and s_end < o_end:
                before_schedule = UserEvent(s_name, s_start, o_start)
                self.final_schedule.append(before_schedule)
                partial_override = UserEvent(o_name, o_start, s_end)
                self.final_schedule.append(partial_override)
                self.override_lst[p2].start_time = s_end
                p1 += 1
            # Case 5
            elif o_start < s_start and o_end < s_end:
                self.final_schedule.append(o_event)
                



            

            

        while p1 < len(self.schedule_lst): 
            self.final_schedule.append(self.schedule_lst[p1])
            p1 += 1

        while p2 < len(self.override_lst): 
            self.final_schedule.append(self.override_lst[p2])
            p2 += 1


 

                        
# # Case 1 in between overlap 
            # if s_start <= o_start < o_end <= s_end:
            #     if s_start < o_start:
            #         before_schedule = UserEvent(self.schedule_lst[p1].name, s_start, o_start)
            #         self.final_schedule.append(before_schedule)

            #     self.final_schedule.append(self.override_lst[p2])
            #     if o_end < s_end:
            #         self.schedule_lst[p1] = UserEvent(self.schedule_lst[p1].name, o_end, s_end)
            #         p2 += 1
            #     else:
            #         p1 += 1
            #         p2 += 1

                
            # # Case 2 override start time overlap between schedule
            # elif s_start < o_start < s_end and s_end < o_end:
            #     before_schedule = UserEvent(self.schedule_lst[p1].name, s_start, o_start)
            #     self.final_schedule.append(before_schedule)
            #     p1 += 1
            
            # # Case 3 override end time overlap between schedule (schedule_start < override_end < schedule_end and override_start < schedule_start)
            # elif o_start < s_start and s_start < o_end <= s_end:
            #     self.final_schedule.append(self.override_lst[p2])
            #     if o_end < s_end:
            #         # keep cutting the same schedule tail
            #         self.schedule_lst[p1] = UserEvent(self.schedule_lst[p1].name, o_end, s_end)
            #         p2 += 1
            #     else:  # o_end == s_end
            #         p1 += 1
            #         p2 += 1

            # elif o_start <= s_start and s_end <= o_end:
            #     # When it ends exactly with this schedule, output override once here
            #     if o_end == s_end:
            #         self.final_schedule.append(self.override_lst[p2])
            #         p1 += 1
            #         p2 += 1
            #     else:
            #         # override continues beyond this schedule; consume the schedule only
            #         p1 += 1



    