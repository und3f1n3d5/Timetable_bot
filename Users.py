from Events import events, event
from constants import Days


class user:
    def __init__(self, i, bot):
        self.bot = bot
        self.adding = False
        self.removing = False
        self.id = i
        self.events = events()
        self.is_subscribed = False
        self.added_day = ""
        self.added_event = event(-1, -1, "")
        self.sure_reset = False

    def add(self, line):
        self.events.add(line)

    def remind(self, evt):
        self.bot.send_message(self.id, evt)

    def add_event(self, string):
        hour, minute = self.added_event.hour, self.added_event.minute
        if string.find("/add_event") != -1:
            self.bot.send_buttons(self.id)
            return
        if hour > -1:
            self.added_event = event(hour, minute, string)
            self.events.add_event(self.added_event, self.added_day)
            self.bot.send_message(self.id, "Успешно добавлено")
            self.adding = False
            return
        else:
            if string in Days:
                self.added_day = string
                self.bot.send_message(self.id, "Введите время в 24-х часовом формате")
                return
            elif string.find(":") != -1:
                hour = string[:string.find(":")]
                minute = string[string.find(":") + 1:]
            elif string.find("-") != -1:
                hour = string[:string.find("-")]
                minute = string[string.find("-") + 1:]
            elif string.find(".") != -1:
                hour = string[:string.find(".")]
                minute = string[string.find(".") + 1:]
            elif string.find("_") != -1:
                hour = string[:string.find("_")]
                minute = string[string.find("_") + 1:]
            elif string.find("_") != -1:
                hour = string[:string.find("_")]
                minute = string[string.find("_") + 1:]
            elif string.find(" ") != -1:
                hour = string[:string.find(" ")]
                minute = string[string.find(" ") + 1:]
            elif len(string) == 3 or len(string) == 4:
                hour = string[:2]
                minute = string[2:]
            else:
                self.bot.send_message(self.id, "Некорректный формат, попробуйте ещё раз 3")
                return

        if self.added_day == "":
            self.bot.send_message(self.id, "Попробуйте еще раз выбрать день")
            self.bot.send_buttons(self.id)
            return

        try:
            self.added_event = event(hour, minute, "-")
            if not (0 <= self.added_event.hour <= 23 and 0 <= self.added_event.minute <= 59):
                self.bot.send_message(self.id, "Некорректный формат, попробуйте ещё раз 2")
                return
            self.bot.send_message(self.id, "Введите название события")
        except Exception as e:
            print(e)
            self.bot.send_message(self.id, "Некорректный формат, попробуйте ещё раз 1")
            return

    def remove_event(self, string):
        if string.find("/remove_event") != -1:
            reply = "Вот ваши события:\n"
            evs = self.events.get_events()
            for i in range(len(evs)):
                add = str(i + 1) + ". " + evs[i] + "\n"
                reply += add
            reply += "Введите номер события, которое хотите удалить"
            self.bot.send_message(self.id, reply)
            return
        else:
            try:
                number = int(string)
                number -= 1
                evs = self.events.get_events()
                if 0 <= number < len(evs):
                    self.events.remove_event(evs[number])
                    self.bot.send_message(self.id, "Успешно удалено")
                    self.removing = False
                else:
                    self.bot.send_message(self.id, "Нет такого номера, попробуйте ещё раз")
            except Exception:
                self.bot.send_message(self.id, "Некорректный формат, попробуйте ещё раз")

    def list_events(self):
        evs = self.events.get_events()
        res = ""
        i = 0
        for ev in evs:
            i += 1
            res += str(i) + ". " + ev + "\n"
        return res

    def show_subscription(self):
        if self.is_subscribed:
            self.bot.send_message(self.id, "Вы подписаны на расписание группы Б05-912")
        else:
            self.bot.send_message(self.id, "Вы не подписаны на расписание группы Б05-912")

    # todo testing
    def refresh(self):
        self.events.refresh()

    def backup(self, file):
        file.write("#\n" + self.id + "\n")
        self.events.backup(file)
        if self.is_subscribed:
            file.write("1\n")
        else:
            file.write("0\n")
        file.write("\n")

    def check_events(self):
        reminders = self.events.check_time()
        for reminder in reminders:
            self.remind(reminder)
        return

    def subscribe(self, what, timetable):
        if not self.is_subscribed and not what:
            return
        self.is_subscribed = what
        for day in Days:
            for ev in timetable.Events[day]:
                if what:
                    self.events.add_event(ev, day)
                else:
                    mm = str(ev.minute)
                    hh = str(ev.hour)
                    if ev.minute < 10:
                        mm = "0" + mm
                    if ev.hour < 10:
                        hh = "0" + hh
                    self.events.remove_event(day + " " + hh + ":" + mm + " " + ev.text)

    def reset(self):
        self.events = events()
        return
