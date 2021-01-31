import datetime
import constants
from BotHandler import BotHandler


def main():
    new_offset = None
    bot = BotHandler(constants.token)
    backuped = False
    back_up_minute = 30

    while True:
        try:
            upds = bot.get_updates(new_offset)
            if upds:
                last_update = upds[-1]
                last_update_id = last_update.update_id
                last_chat_text = last_update.message.text
                last_chat_id = str(last_update.message.chat.id)
                bot.receive_message(last_chat_id, last_chat_text)
                new_offset = last_update_id + 1

            now = datetime.datetime.now()
            if now.minute < back_up_minute and backuped:
                backuped = False
            if now.minute >= back_up_minute and not backuped:
                bot.backup_all()
                backuped = True
            if constants.Days[now.weekday()] == "Mon" and now.hour == 0 and now.minute == 0:
                bot.refresh_all()
            bot.check_users()

        except Exception as e:
            errors = open("error.txt", "a")
            errors.write(str(e) + "in main\n")
            errors.close()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
