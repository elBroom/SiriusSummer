import datetime
import random

from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    CallbackContext, CallbackQueryHandler, CommandHandler, Updater
)

# @AliasGameTest123Bot
# Игра alias, за минуту нужно описать как можно больше слов загаданные ботом


# Загрузка telegram библиотеки
# pip install python-telegram-bot --upgrade

# Создание бота в телеграме
# @BotFather /newbot

# Use this token to access the HTTP API: TOKEN
# Токен который выдал @BotFather
TOKEN = '<YOUR TOKEN>'
# Время в секундах через которое заработает алерт
INTERVAL = 60  
# Временное хранилище, сбрасывается при перезагрузки файла
# Что бы память не сбрасывалась и была статистика
# данные можно хранить в файлах или в sqllite
MEMORY = {}

# управляющие кнопки в игре
buttons = [
    InlineKeyboardButton(text='Дальше', callback_data=f'next'),
    InlineKeyboardButton(text='Пропустить', callback_data=f'skip'),
]
# список генерируемых слов, можно вынести в отдельный файл и читать оттуда
words = [
    'футбол', 'каша', 'карандаш', 'тигр', 'автобус', 'роза', 'учитель',
    'рыба', 'трава', 'ракета', 'диван', 'шерсть', 'дневник', 'радио',
    'самокат', 'лента', 'утюг', 'пейзаж', 'окно', 'компьютер', 'лягушка',
]

def generate_word() -> str:
    '''Генератор слов'''
    num = random.randrange(len(words))
    return words[num]


def start_command(update: Update, context: CallbackContext) -> None:
    '''Обработчик команды /start'''
    print(f'Start new chat_id {update.message.chat_id}')
    update.message.reply_text('Для начала игры нажми /game.')
    update.message.reply_text('Для отмены /cancel.')


def cancel_command(update: Update, context: CallbackContext) -> None:
    '''Обработчик команды /cancel'''
    print(f'Cancel game for chat_id {update.message.chat_id}')
    chat_id = update.message.chat_id
    # Отменяем алерт запущеннный в команде /game
    for job in context.job_queue.get_jobs_by_name(f'{chat_id} game'):
        job.schedule_removal()
    update.message.reply_text('Игра остановлена')


def game_command(update: Update, context: CallbackContext) -> None:
    '''Обработчик команды /game'''
    print(f'Start new game for chat_id {update.message.chat_id}')
    # Устанавливаем интервал через который будет окончен раунд
    timedelta = datetime.timedelta(seconds=INTERVAL)
    chat_id = update.message.chat_id
    word = generate_word()

    MEMORY[chat_id] = []
    # Запускаем алерт об окончании раунда
    context.job_queue.run_once(
        alert, timedelta, name=f'{chat_id} game',
        context={'chat_id': chat_id},
    )

    update.message.reply_text('Время пошло')
    # Отправляем в чат сгенереное слово и панель из кнопок
    update.message.reply_text(
        word, reply_markup=InlineKeyboardMarkup([buttons]),
    )

def next_query(update: Update, context: CallbackContext) -> None:
    '''Обработчик кнопки Дальше'''
    chat_id = update.callback_query.message.chat_id
    word = update.callback_query.message.text
    # Засчитываем слово в статистику 
    MEMORY[chat_id].append(word)

    word = generate_word()
    # Отправляем в чат сгенереное слово и панель из кнопок
    update.callback_query.message.reply_text(
        word, reply_markup=InlineKeyboardMarkup([buttons]),
    )

def skip_query(update: Update, context: CallbackContext) -> None:
    '''Обработчик кнопки Пропустить'''
    word = generate_word()
    # Отправляем в чат сгенереное слово и панель из кнопок
    update.callback_query.message.reply_text(
        word, reply_markup=InlineKeyboardMarkup([buttons]),
    )


def alert(context: CallbackContext) -> None:
    '''Обработчик оповещающий о конце раунда'''
    print(f'Alert {context.job.name}')
    chat_id = context.job.context['chat_id']
    # Получаем из статистики слова
    words = MEMORY.get(chat_id, [])

    context.bot.send_message(
        chat_id, 
        text=f"Время вышло. Слов за минуту {len(words)}.",
    )
    if words:
        context.bot.send_message(chat_id, 
            text=f"Засчитанные слова: {', '.join(MEMORY.get(chat_id, []))}.",
        )
    # Отчищаем статистику для новой игры
    MEMORY[chat_id] = []

# Резервируем команды и обработчики
handlers = [
    CommandHandler('start', start_command),
    CommandHandler('game', game_command),
    CommandHandler('cancel', cancel_command),

    CallbackQueryHandler(next_query, pattern='next'),
    CallbackQueryHandler(skip_query, pattern='skip'),
]

def main() -> None:
    updater = Updater(TOKEN, workers=100)
    for handler in handlers:
        updater.dispatcher.add_handler(handler)

    updater.start_polling()
    print('Start bot')
    updater.idle()


if __name__ == '__main__':
    main()

