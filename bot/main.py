from telegram.ext import Updater
from telegram.bot import Update
from telegram.ext import CommandHandler
import logging

# TODO: put logs in some logs file
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def start(bot, update:Update):
    update.message.reply_text('start')

def help(bot, update:Update):
    update.message.reply_text('help')

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    TOKEN_ARMOR = "616701770:AAELU_nMtn8xDAo-8e8OORrp7vJF3P1PQEo" # @armor_test_bot

    updater = Updater(TOKEN_ARMOR)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()