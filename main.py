import telebot
#import time
import datetime

token = "1411772657:AAFkziVjMcehzkWDRWJyrnt7au7EBqDL9nQ"


class BotHandler:

    def __init__(self, token):
        self.users_write = None
        self.users_read = open("users.txt", "r")
        self.users = dict()
        flag = 0
        i = ""
        for user in self.users_read:
            if user == "#\n":
                flag = 1
                continue
            if flag == 2:
                self.users[i].add_event(user[:-1])
            if flag == 1:
                i = user[:-1]
                self.users[i] = User(user[:-1])
                flag += 1
        self.token = token
        self.api_url = "https://api.telegram.org/bot1411772657:AAFkziVjMcehzkWDRWJyrnt7au7EBqDL9nQ/"

    def send_message(self, chat_id, text):
        bot.send_message(chat_id, text)

    def update_users(self, i):
        if i not in self.users:
            self.users[i] = User(i)

    def remind(self):
        for user in self.users:
            message = self.users[user].get_next_event()
            if message and self.users:
                self.send_message(user, message)

    def add_events(self, user_id, update):
        try:
            self.users[str(user_id)].add_event(update)
            self.send_message(user_id, "Добавлено")
        except Exception as e:
            errors = open("error.txt", "a")
            errors.write(str(e) + "in add events, message:" + update)
            errors.close()
            self.send_message(user_id, "Некорректный формат")

    def remove_events(self, user_id, remove):
        try:
            self.users[str(user_id)].remove_event(remove)
            self.send_message(user_id, "Удалено")
        except Exception as e:
            errors = open("error.txt", "a")
            errors.write(str(e) + "in remove events, message:" + remove)
            errors.close()
            self.send_message(user_id, "Некорректный формат или нет такого события")

    def start_update(self, user_id):
        self.send_message(user_id, "Введите событие, которое хотите добавить в формате как в примере:\n\t Thu 12:20 "
                                   "<Кр по ОКТЧ>\n (<> - обязательны!)\nПосле того как удалите все ненужные события ("
                                   "каждое в новом сообщении) введите команду /stop_adding, чтобы сохранить изменения")
        self.users[user_id].is_updating = True

    def start_removing(self, user_id):
        self.send_message(user_id, "Введите событие, которое хотите удалить в формате как в примере:\n\t Thu 12:20 "
                                   "<Кр по ОКТЧ>\n (<> - обязательны!)\nПосле того как удалите все ненужные события ("
                                   "каждое в новом сообщении) введите команду /stop_removing, чтобы сохранить изменения")
        self.users[user_id].is_removing = True

    def end_update(self, user_id):
        self.users[user_id].is_updating = False
        self.send_message(user_id, "Добавление успешно завершено")

    def end_removing(self, user_id):
        self.users[user_id].is_removing = False
        self.send_message(user_id, "Удаление успешно завершено")

    def reset(self, user_id):
        self.users[user_id].events.clear()
        self.send_message(user_id, "Успешно очищено!")

    def help(self, chat_id):
        self.send_message(chat_id,
                          "\t /start - начать общение\n\t/help - вывести список доступных команд\n\t/add_events "
                          "- добавить события в расписание\n\t/remove_events - удалить события из "
                          "расписания\n\t/stop_adding - закончить обновление\n\t/stop_removing - закончить "
                          "удаление\n\t/reset - очистить расписание\n\t/show_timetable - показать текущее расписание")

    def sync(self):
        self.users_write = open("users.txt", "w")
        for user in self.users:
            self.users[user].write(self.users_write)
        self.users_write.close()

    def show_timetable(self, user_id):
        ans = ""
        for event in self.users[user_id].events:
            ans += event.day + " " + str(event.hour) + ":" + str(event.minute) + " " + event.message + "\n"
        if not ans:
            ans = "Кажется у вас нет ни одного события!"
        self.send_message(user_id, ans)

    def start_message(self, chat_id):
        self.update_users(chat_id)
        self.send_message(chat_id, 'Приветствую, друг! Я бот, который может напоминать тебе о событиях. Нажми '
                                   '/help, чтобы увидеть мои команды')

    def refresh(self):
        for user in self.users:
            self.users[user].refresh()


class User:
    def __init__(self, string):
        self.days = ["Mon", "Tue", "Wen", "Thu", "Fri", "Sat", "Sun"]
        self.id = string
        self.events = set()
        self.is_updating = False
        self.is_removing = False

    def add_event(self, string):
        event = Event(string)
        self.events.add(event)

    def remove_event(self, string):
        event = Event(string)
        to_rm = event
        for e in self.events:
            if e.day == event.day and e.minute == event.minute and e.message == event.message:
                to_rm = e
        self.events.remove(to_rm)

    def get_next_event(self):
        now = datetime.datetime.now()
        day = self.days[now.weekday()]
        hour = now.hour
        minute = now.minute
        for event in self.events:
            if event.day == day and event.hour == hour and event.minute == minute and event.reminded == 0:
                event.reminded = 1
                return event.message
        return None

    def write(self, file):
        file.write("#\n")
        file.write(self.id + "\n")
        for event in self.events:
            file.write(event.day + " " + str(event.hour) + ":" + str(event.minute) + " <" + event.message + ">\n")

    def refresh(self):
        for event in self.events:
            event.reminded = False


class Event:
    def __init__(self, string):
        self.day = string[:string.find(" ")]
        self.hour = int(string[string.find(" ") + 1: string.find(":")])
        self.minute = int(string[string.find(":") + 1: string.find("<")])
        self.message = string[string.find("<") + 1: string.find(">")]
        self.reminded = 0


time_bot = BotHandler(token)
bot = telebot.TeleBot('1411772657:AAFkziVjMcehzkWDRWJyrnt7au7EBqDL9nQ')


def main():
    new_offset = None

    while True:
        try:
            upds = bot.get_updates(offset=new_offset)
            if upds:
                last_update = upds[-1]
                last_update_id = last_update.update_id
                last_chat_text = last_update.message.text
                last_chat_id = str(last_update.message.chat.id)
                time_bot.update_users(last_chat_id)

                in_process = time_bot.users[last_chat_id].is_removing or time_bot.users[last_chat_id].is_updating

                if last_chat_text.find("/start") != -1 and not in_process:
                    time_bot.start_message(last_chat_id)
                elif in_process and last_chat_text.find("/start") != -1:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс добавления/удаления")

                if last_chat_text.find("/help") != -1 and not in_process:
                    time_bot.help(last_chat_id)
                elif in_process and last_chat_text.find("/help") != -1:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс добавления/удаления")

                if last_chat_text.find("/reset") != -1 and not in_process:
                    time_bot.reset(last_chat_id)
                elif in_process and last_chat_text.find("/reset") != -1:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс добавления/удаления")

                if last_chat_text.find("/show_timetable") != -1 and not in_process:
                    time_bot.show_timetable(last_chat_id)
                elif in_process and last_chat_text.find("/show_timetable") != -1:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс добавления/удаления")

                if last_chat_text.find("/add_events") != -1 and not in_process:
                    time_bot.start_update(last_chat_id)
                elif last_chat_text.find("/add_events") != -1 and time_bot.users[last_chat_id].is_removing:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс удаления")
                elif last_chat_text.find("/stop_adding") != -1:
                    time_bot.end_update(last_chat_id)
                elif time_bot.users[last_chat_id].is_updating:
                    time_bot.add_events(last_chat_id, last_chat_text)

                if last_chat_text.find("/remove_events") != -1 and not in_process:
                    time_bot.start_removing(last_chat_id)
                elif last_chat_text.find("/remove_events") != -1 and time_bot.users[last_chat_id].is_updating:
                    time_bot.send_message(last_chat_id, "Сначала завершите процесс добавления")
                elif last_chat_text.find("/stop_removing") != -1:
                    time_bot.end_removing(last_chat_id)
                elif time_bot.users[last_chat_id].is_removing:
                    time_bot.remove_events(last_chat_id, last_chat_text)

                new_offset = last_update_id + 1

            time_bot.remind()
            now = datetime.datetime.now()
            if now.minute == 0:
                time_bot.sync()
            if now.day == "Mon" and now.hour == 0:
                time_bot.refresh()
        except Exception as e:
            errors = open("error.txt", "a")
            errors.write(str(e) + "in main")
            errors.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
