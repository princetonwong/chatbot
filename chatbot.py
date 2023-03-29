from telegram import Update, ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
# import configparser
import os
import logging
import redis

global redis1
from Database import Database

# DATABASE_URL = os.environ['DATABASE_URL']

# TODO: Enable /searchSchool function to obtain {schoolCode} from {schoolName}
# TODO: Allow /search command from {schoolCode, form, exam/test, fileType, year) to [fileDescription, fileType, fileSize]
# TODO: Allow dynamic /file<id> command to download file hosted on GDrive
# TODO: Downloaded times



def main():
    # Load your token and create an Updater for your Bot
    # config = configparser.ConfigParser()
    # config.read('config.ini')
    updater = Updater(token=(os.environ['ACCESS_TOKEN']), use_context=True)
    dispatcher = updater.dispatcher
    global redis1
    redis1 = redis.Redis(host=(os.environ['HOST']),
                         password=(os.environ['PASSWORD']),
                         port=(os.environ['REDISPORT']))

    # You can set this logging module, so you will know when and why things do not work as expected
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level = logging.INFO)

    # register a dispatcher to handle message: here we register an echo dispatcher
    echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)
    dispatcher.add_handler(echo_handler)
    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("add", add))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(CommandHandler("hello", hello))
    dispatcher.add_handler(CommandHandler("searchSchool", searchSchool))
    # To start the bot:
    updater.start_polling()
    updater.idle()


def echo(update, context):
    reply_message = update.message.text.upper()
    logging.info("Update: " + str(update))
    logging.info("context: " + str(context))
    context.bot.send_message(chat_id=update.effective_chat.id, text=reply_message)


# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Helping you helping you.')


def add(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /add is issued."""
    try:
        global redis1
        logging.info(context.args[0])
        msg = context.args[0]  # /add keyword <-- this should store the keyword
        redis1.incr(msg)
        update.message.reply_text('You have said ' + msg + ' for ' +
                                  redis1.get(msg).decode('UTF-8') + ' times.')
    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def hello(update: Update, context: CallbackContext) -> None:
    try:
        logging.info(context.args[0])
        name = context.args[0]
        update.message.reply_text(f"Good day, {name}!")

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')


def searchSchool(update: Update, context: CallbackContext) -> None:
    from School import School
    try:
        logging.info(context.args[0])
        searchString = context.args[0]
        db = Database()
        records = db.searchSchool(searchString)

        count = len(records)
        schools = [School(*kwargs) for kwargs in records]
        replyText = f"Good news! We found {count} 🏫 for your request!\n"

        for school in schools:
            replyText += f"""<b>🏫[/{school.code}] {school.chinesename}</b>
<i>{school.englishname}</i>
\n"""

        update.message.reply_text(replyText,
                                  reply_to_message_id=update.message.message_id,
                                  parse_mode=ParseMode.HTML)

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /add <keyword>')

if __name__ == '__main__':
    main()