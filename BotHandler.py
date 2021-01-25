from Users import user
from Events import events
import datetime
import telebot

Days = ["Mon", "Tue", "Wen", "Thu", "Fri", "Sat", "Sun"]

start_message = 'Приветствую, друг! Я бот, который может напоминать тебе о событиях. Нажми /help, чтобы увидеть мои ' \
                'команды '
help_message = "\n\t/start - начать общение\n\t/help - вывести список доступных команд\n\t/add_event - добавить " \
               "событие в расписание\n\t/remove_event - удалить событие из расписания\n\t" \
               "\n\t/reset - очистить расписание\n\n\t/show_timetable " \
               "- показать текущее расписание\n\t/subscribe - подписаться на все события из расписания " \
               "группы\n\t/unsubscribe - отменить подписку "
reset_message = "Все события удалены"
subscribe_message = "Теперь вы подписаны на расписание группы Б05-912"
unsubscribe_message = "Подписка отменена"


class BotHandler:
    def read_users(self):
        action = ""
        current_user = ""
        for line in self.users_read:
            line = line[:-1]
            if not line:
                print("empty line")
                continue
            if action == "read_events":
                if line == "1":
                    self.users[current_user].subscribe(True, self.timetable)
                    action = "-"
                    continue
                if line == "0":
                    self.users[current_user].subscribe(False, self.timetable)
                    action = "-"
                    continue
                self.users[current_user].add(line)
            if action == "read_user":
                current_user = line
                self.users[line] = user(current_user, self)
                action = "read_events"
            if line == "#":
                action = "read_user"

    def read_timetable(self):
        for line in self.timetable_file:
            self.timetable.add(line)

    def __init__(self, token):
        self.backup_file = "users.txt"
        self.users_read = open("users.txt", "r")
        self.timetable_file = open("timetable.txt", "r")
        self.timetable = events()
        self.users = dict()
        self.token = token
        self.bot = telebot.TeleBot(token)
        self.read_timetable()
        self.read_users()

    def send_message(self, user_id, message):
        self.bot.send_message(user_id, message)

    def send_buttons(self, user_id):
        buttons = telebot.types.ReplyKeyboardMarkup(True, True)
        buttons.row("Mon", "Tue", "Wen", "Thu", "Fri", "Sat", "Sun")
        self.bot.send_message(user_id, "Выберите день, на который вы хотели бы поставить событие", reply_markup=buttons)

    def recieve_message(self, user_id, text):
        if text.find("/start") != -1:
            if self.users[user_id] is None:
                self.users[user_id] = user(user_id, self)
            self.send_message(user_id, start_message)
        elif text.find("/help") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = False
            self.send_message(user_id, help_message)
        elif text.find("/add_event") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = True
        elif text.find("/remove_event") != -1:
            self.users[user_id].removing = True
            self.users[user_id].adding = False
        elif text.find("/reset") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = False
            self.users[user_id].is_subscribed = False
            self.send_message(user_id, reset_message)
            self.users[user_id].reset()
        elif text.find("/subscribe") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = False
            self.send_message(user_id, subscribe_message)
            self.users[user_id].subscribe(True, self.timetable)
        elif text.find("/unsubscribe") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = False
            self.send_message(user_id, unsubscribe_message)
            self.users[user_id].subscribe(False, self.timetable)
        elif text.find("/show_timetable") != -1:
            self.users[user_id].removing = False
            self.users[user_id].adding = False
            message = self.users[user_id].list_events()
            if message == "":
                message = "У вас нет событий"
            self.send_message(user_id, message)

        if self.users[user_id].adding:
            self.users[user_id].add_event(text)
        elif self.users[user_id].removing:
            self.users[user_id].remove_event(text)

    def check_users(self):
        for u in self.users.keys():
            self.users[u].check_events()

    def backup_all(self):
        file = open(self.backup_file, "w")
        for u in self.users.keys():
            self.users[u].backup(file)
        file.close()
        print("Successfully backuped")

    # todo testing
    def refresh_all(self):
        if Days[datetime.datetime.now().weekday()] == "Mon" and datetime.datetime.now().minute == 0 and datetime.datetime.now().hour == 0:
            for u in self.users.keys():
                self.users[u].refresh()

    def get_updates(self, new_offset):
        return self.bot.get_updates(offset=new_offset)
