import datetime
from constants import Days


class event:
    def __init__(self, HH, MM, s):
        self.hour = int(HH)
        self.minute = int(MM)
        if not s:
            self.text = "Ы"
        else:
            self.text = s
        if self.text[-1] == "\n":
            self.text = self.text[:-1]
        self.is_reminded = False

    def __lt__(self, other):
        return self.hour < other.hour or (self.hour == other.hour and self.minute < other.minute)


class events:
    def __init__(self):
        self.Events = dict()
        for day in Days:
            self.Events[day] = list()

    def check_time(self):
        res = list()
        for e in self.Events[Days[datetime.datetime.now().weekday()]]:
            if datetime.datetime.now().minute == e.minute and datetime.datetime.now().hour == e.hour and not e.is_reminded:
                res.append(e.text)
                e.is_reminded = True
        return res

    def add_event(self, ev, day):
        for e in self.Events[day]:
            if e.hour == ev.hour and e.minute == ev.minute and e.text == ev.text:
                return
        self.Events[day].append(ev)

    def add(self, string):
        day = string[:3]
        ev = event(string[4:6], string[7:9], string[10:])
        self.add_event(ev, day)

    def remove_event(self, string):
        day = string[:3]
        ev = event(string[4:6], string[7:9], string[10:])
        for e in self.Events[day]:
            if e.hour == ev.hour and e.minute == ev.minute and e.text == ev.text:
                self.Events[day].remove(e)
                return

    def backup(self, file):
        for day in Days:
            for ev in self.Events[day]:
                mm = str(ev.minute)
                hh = str(ev.hour)
                if ev.minute < 10:
                    mm = "0" + mm
                if ev.hour < 10:
                    hh = "0" + hh
                file.write(day + " " + hh + ":" + mm + " " + str(ev.text))

    # todo testing
    def refresh(self):
        for day in Days:
            for e in self.Events[day]:
                e.is_reminded = False
        return

    def get_events(self):
        res = list()
        for day in Days:
            self.Events[day].sort()
            for ev in self.Events[day]:
                mm = str(ev.minute)
                hh = str(ev.hour)
                if ev.minute < 10:
                    mm = "0" + mm
                if ev.hour < 10:
                    hh = "0" + hh
                res.append(day + " " + hh + ":" + mm + " " + ev.text)
        return res
