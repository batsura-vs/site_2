import json
import secrets
from telegram import *
from telegram.ext import *

with open('settings.json', 'r') as f:
    s = str(f.read())
    settings = json.loads(s)
bot = Bot(settings['token'])
ur = f'{settings["protocol"]}://{settings["host"]}:{settings["port"]}'


def start(update, context):
    k = [[KeyboardButton('/login')]]
    k = ReplyKeyboardMarkup(k, resize_keyboard=True)
    update.message.reply_text('Здравствуйте, для входа используйте кнопку ниже.', reply_markup=k)


def get_link(update, context):
    with open('links.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    if str(update.message.from_user.id) in js['admins']:
        with open('links.json', 'w') as f:
            s = secrets.token_urlsafe(30)
            js['links'].append(s)
            json.dump(js, f)
        k = [[InlineKeyboardButton('Клик!', url=f'{ur}/lo/{s}')]]
        k = InlineKeyboardMarkup(k)
        bot.send_message(chat_id=update.message.from_user.id, text=f'Ссылка для входа:', reply_markup=k)


def add_admin(update, context):
    with open('links.json', "r") as file:
        js = json.loads(file.read())
    if str(update.message.from_user.id) == js['head_admin']:
        mess = update.message.text
        mess = mess.split(' ')
        mess.pop(0)
        if len(mess) == 1:
            with open('links.json', "w") as file:
                js['admins'].append(str(mess[0]))
                json.dump(js, file)
            update.message.reply_text(f'Successful added user with id "{mess[0]}" to admins list')
    else:
        update.message.reply_text('Permission denied')


def rem_admin(update, context):
    with open('links.json', "r") as file:
        js = json.loads(file.read())
    if str(update.message.from_user.id) == js['head_admin']:
        try:
            mess = update.message.text
            mess = mess.split(' ')
            mess.pop(0)
            if len(mess) == 1:
                if type(int(mess[0])) is int:
                    with open('links.json', "w") as file:
                        js['admins'].remove(str(mess[0]))
                        json.dump(js, file)
                    update.message.reply_text(f'Successful removed user with id "{mess[0]}" to admins list')
        except:
            pass
    else:
        update.message.reply_text('Permission denied')


def clear(update, context):
    with open('links.json', 'r') as f:
        s = str(f.read())
        js = json.loads(s)
    with open('links.json', 'w') as f:
        js['links'] = []
        json.dump(js, f)
    update.message.reply_text('Успех!')


if __name__ == '__main__':
    updater = Updater(settings['token'])
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('add_admin', add_admin))
    updater.dispatcher.add_handler(CommandHandler('rem_admin', rem_admin))
    updater.dispatcher.add_handler(CommandHandler('clear', clear))
    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CommandHandler('login', get_link))
    updater.start_polling()
