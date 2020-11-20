import time

import requests
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

    def get_updates(self, offset=None, timeout=1):
        method = 'getUpdates'
        params = {'timeout': timeout, 'offset': offset}
        resp = requests.get(self.api_url + method, params)
        result_json = resp.json()['result']
        return result_json

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp

    def get_last_update(self, offset=None):
        get_result = self.get_updates(offset)
        if len(get_result) > 0:
            last_update = get_result[-1]
        else:
            last_update = None

        return last_update

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
            self.users[str(user_id)].add_event(update[update.find(" ") + 1:])
        except:
            self.send_message(user_id, "Некорректный формат")

    def remove_events(self, user_id, remove):
        try:
            self.users[str(user_id)].remove_event(remove[remove.find(" ") + 1:])
        except:
            self.send_message(user_id, "Некорректный формат или нет такого события")

    def start_update(self, user_id):
        self.send_message(user_id, "Введите событие, которое хотите добавить в формате как в примере:\n\t Thu 12:20 "
                                   "<Кр по ОКТЧ>\n После того как добавите все события (каждое в новом сообщении) "
                                   "введите команду /stop_adding, чтобы сохранить изменения")
        self.users[user_id].is_updating = True

    def start_removing(self, user_id):
        self.send_message(user_id, "Введите событие, которое хотите удалить в формате как в примере:\n\t Thu 12:20 "
                                   "<Кр по ОКТЧ>\n После того как удалите все ненужные события (каждое в новом "
                                   "сообщении) введите команду /stop_removing, чтобы сохранить изменения")
        self.users[user_id].is_removing = True

    def end_update(self, user_id):
        self.users[user_id].is_updating = False

    def end_removing(self, user_id):
        self.users[user_id].is_removing = False

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

    def show_timetable(self, user_id):
        ans = ""
        for event in self.users[user_id].events:
            ans += event.day + " " + event.hour + ":" + event.minute + " " + event.message + "\n";
        self.send_message(user_id, ans)


class User:
    def __init__(self, string):
        self.id = string
        self.events = set()
        self.is_updating = False
        self.is_removing = False

    def add_event(self, string):
        event = Event(string)
        self.events.add(event)

    def remove_event(self, string):
        event = Event(string)
        self.events.remove(event)

    def get_next_event(self):
        var = time.strftime("%a#%H^%M:%S", time.localtime())
        day = var[:var.find("#")]
        hour = int(var[var.find("#") + 1:var.find("^")])
        minute = int(var[var.find("^") + 1:var.find(":")])
        for event in self.events:
            if event.day == day and event.hour == hour and event.minute == minute and event.reminded == 0:
                event.reminded = 1
                return event.message
        return None

    def write(self, file):
        file.write("#\n")
        file.write(self.id + "\n")
        for event in self.events:
            file.write(event.day + " " + event.hour + ":" + event.minute + " <" + event.message + ">\n")


class Event:
    def __init__(self, string):
        self.day = string[:string.find(" ")]
        self.hour = int(string[string.find(" ") + 1: string.find(":")])
        self.minute = int(string[string.find(":") + 1: string.find("<")])
        self.message = string[string.find("<") + 1: string.find(">")]
        self.reminded = 0


time_bot = BotHandler(token)


def main():
    new_offset = None

    while True:
        #time_bot.get_updates(new_offset)

        last_update = time_bot.get_last_update(new_offset)
        if last_update:
            last_update_id = last_update['update_id']
            last_chat_text = last_update['message']['text']
            last_chat_id = last_update['message']['chat']['id']
            last_chat_name = last_update['message']['chat']['first_name']
            time_bot.update_users(last_chat_id)

            if last_chat_text.find("/help") != -1:
                time_bot.help(last_chat_id)

            if last_chat_text.find("/reset") != -1:
                time_bot.reset(last_chat_id)

            if last_chat_text.find("/show_timetable") != -1:
                time_bot.show_timetable(last_chat_id)

            if last_chat_text.find("/add_events") != -1:
                time_bot.start_update(last_chat_id)
            if time_bot.users[last_chat_id].is_updating:
                time_bot.add_events(last_chat_id, last_chat_text)
            if last_chat_text.find("/stop_adding") != -1:
                time_bot.end_update(last_chat_id)

            if last_chat_text.find("/remove_events") != -1:
                time_bot.start_removing(last_chat_id)
            if time_bot.users[last_chat_id].is_removing:
                time_bot.remove_events(last_chat_id, last_chat_text)
            if last_chat_text.find("/stop_removing") != -1:
                time_bot.end_removing(last_chat_id)


                
            ###     todo  
            # сделать команды апдейта и удаления в раздельных сообщениях 
            # например, добавить в юзера поле ожидания 
            
            ###     todo 
            # сделать команды окончания апдейта/удаления -> меняют статус ожидания юзера
            # и резет -> обнуляет расписание юзера

            ###     todo
            # обновление статусов событий каждое вс
            # вывести расписание юзера

            new_offset = last_update_id + 1

        time_bot.remind()
        now = datetime.datetime.now()
        if now.minute == 0:
            time_bot.sync()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
