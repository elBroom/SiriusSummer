from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Updater


TOKEN = '<YOUR TOKEN>'



def start_command(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Привет {update.effective_user.username}!')


def main() -> None:
    updater = Updater(TOKEN, workers=100)
    updater.dispatcher.add_handler(CommandHandler("start", start_command))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()

