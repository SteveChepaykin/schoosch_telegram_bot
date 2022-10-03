from itertools import count
import telebot
import config
from bot_session import BotSession
from telebot import types
from pymongo import MongoClient

bot = telebot.TeleBot(config.TOKEN)

count = 0
sessions: dict[int, BotSession] = {}

db = MongoClient(config.MONGO, tls=True, tlsAllowInvalidCertificates=True)

bot.set_my_commands(commands=[
    # types.BotCommand(command='/start', description=''),
    types.BotCommand(command='/login', description='узнать логин'),
    types.BotCommand(command='/tutorial', description='получить инструкцию'),
    types.BotCommand(command='/help', description='увидеть список всех команд'),
    # types.BotCommand(command='/contact', description='получить контакт поддержки'),
])


@bot.message_handler(commands=['start'])
def welcome(message):
    sessions[message.chat.id] = BotSession()
    bot.send_message(
        message.chat.id,
        "Привет!\nЭто бот для быстрой помощи пользователям приложения Schoosch.\nЧтобы узнать свою почту для логина, используй команду /login.\nДля того чтобы увидеть все возможные команды, выбери /help"
    )


@bot.message_handler(commands=['login'])
def getLogin(message):
    if not (message.chat.id in sessions.keys()):
        bot.send_message(message.chat.id, 'Давай начнем с команды /start.')
    else:
        if sessions[message.chat.id].process_command(
                command='login') == 'sendWaitLogin':
            bot.send_message(
                message.chat.id,
                'Чтобы узнать твой логин, мне нужно твое имя в формате ФИО. Как тебя зовут?'
            )


@bot.message_handler(commands=['tutorial'])
def sendTutorial(message):
    if not (message.chat.id in sessions.keys()):
        bot.send_message(message.chat.id, 'Давай начнем с команды /start.')
    else:
        if sessions[message.chat.id].process_command(
                command='tutorial') == 'getTutorial':
            keyboard = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton('Ученик', callback_data='stud')
            btn2 = types.InlineKeyboardButton('Учитель', callback_data='teach')
            btn3 = types.InlineKeyboardButton('Родитель', callback_data='par')
            btn4 = types.InlineKeyboardButton('Наставник', callback_data='obs')
            keyboard.add(btn1)
            keyboard.add(btn2)
            keyboard.add(btn3)
            keyboard.add(btn4)
            bot.send_message(message.chat.id,
                            'Кем ты являешься в системе?',
                            reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def answerQuery(call):
    if call.data == 'stud':
        bot.send_message(call.message.chat.id,
                         'Нужные файлы для ученика пока не добавлены.')
    elif call.data == 'teach':
        bot.send_message(call.message.chat.id,
                         'Нужные файлы для учителя пока не добавлены.')
    elif call.data == 'par':
        bot.send_message(call.message.chat.id,
                         'Нужные файлы для родителя пока не добавлены.')
    elif call.data == 'obs':
        bot.send_message(call.message.chat.id,
                         'Нужные файлы для наставника пока не добавлены.')


# @bot.message_handler(commands=['contact'])
# def getContact(message):
    # if not (message.chat.id in sessions.keys):
#         bot.send_message(message.chat.id, 'Давай начнем с команды /start.')
#     else:
    #     if sessions[message.chat.id].process_command(command='contact') == 'getContact':
    #         bot.send_contact(message.chat.id, phone_number='89035972452', first_name='Михаил', last_name='Чепайкин')


@bot.message_handler(commands=['help'])
def seeHelp(message):
    if not (message.chat.id in sessions.keys()):
        bot.send_message(message.chat.id, 'Давай начнем с команды /start.')
    else:
        if sessions[message.chat.id].process_command('help') == 'getHelp':
            bot.send_message(
                message.chat.id,
                '/login - узнать свой логин по имени;\n/tutorial - получить инструкцию по использованию приложения;\n/help - увидеть список команд с пояснениями.'
            )


@bot.message_handler(content_types=['text'])
def listen(message):
    if not (message.chat.id in sessions.keys()):
        bot.send_message(message.chat.id, 'Давай начнем с команды /start.')
    else:
        res = sessions[message.chat.id].process_command('input',
                                                        input=message.text)

        if res == 'sendHelpReminder':
            bot.send_message(
                message.chat.id,
                'Если что, с помощью команды /help ты можешь узнать какие команды тут поддерживаются'
            )
        elif res == 'getlogin':
            m: list[str] = message.text.split(' ')
            login = findPersonLogin(m)
            if login == None:
                bot.send_message(
                    message.chat.id,
                    'Кажется, ты не зарегистрирован в системе. Попробуй написать в поддержку, если считаешь, что должен там быть.'
                )
            elif login == 'no_email':
                bot.send_message(
                    message.chat.id,
                    'Твой логин пока пустует. Свяжись с поддержкой чтобы узнать подробности.'
                )
            else:
                bot.send_message(message.chat.id,
                                'Окей, вот твой логин:\n{0}'.format(login))
                bot.send_message(message.chat.id, 'Что нибудь еще?')
        elif res == 'sendWrongName':
            bot.send_message(message.chat.id, 'Попробуй, пожалуйста, еще раз.')
        elif res == 'sendNameReminder':
            bot.send_message(
                message.chat.id,
                'Пожалуйста, используй формат ФИО. Слова начинай с заглавных букв.\nИтак, твое имя?'
            )


def findPersonLogin(query) -> str | None:
    data = db.schoosch.people.find_one({
        'firstname': query[1],
        'middlename': query[2],
        'lastname': query[0]
    })
    if data == None:
        return None
    if data['email'].endswith('@not.yet'):
        return 'no_email'
    return data['email']


bot.polling(non_stop=True)