import logging
import logging.config
import os

import time
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler

dict_ = {}


def get_chat_id(update, context):
    chat_id = -1

    if update.message is not None:
        chat_id = update.message.chat.id
    elif update.callback_query is not None:
        chat_id = update.callback_query.message.chat.id
    elif update.poll is not None:
        chat_id = context.bot_data[update.poll.id]

    return chat_id


def get_user_id(update):
    _from = None

    if update.message is not None:
        _from = update.message.from_user.id
    elif update.callback_query is not None:
        _from = update.callback_query.from_user.id

    return _from


def main_handler(update, context):
    logging.info(f'update : {update}')

    if update.message is not None:
        """
        "message": {
			"message_id": 27,
			"from_user": {
				"id": 123456789,
				"first_name": "YOUR_FIRST_NAME",
				"last_name": "YOUR_LAST_NAME",
				"username": "YOUR_NICK_NAME"
			},
			"chat": {
				"id": 123456789,
				"first_name": "YOUR_FIRST_NAME",
				"last_name": "YOUR_LAST_NAME",
				"username": "YOUR_NICK_NAME",
				"type": "private"
			},
			"date": 1678292650,
			"text": "test"
		}
        """
        global dict_

        user_id = update.message.from_user.id
        local_dict_ = dict_
        if user_id in local_dict_:
            local_dict_[user_id] += 1
        else:
            local_dict_[user_id] = 1

        if local_dict_[user_id] > 10:
            kick_user_from_group(update, context)

        dict_ = local_dict_


def kick_user_from_group(update, context):
    # kick a user from a group
    context.bot.kick_chat_member(
        chat_id=get_chat_id(update, context),
        user_id=get_user_id(update),
        timeout=int(time.time() + 60))


def error(update, context):
    """Log Errors caused by Updates."""
    logging.warning('Update "%s" ', update)
    logging.exception(context.error)


def main():
    print()
    updater = Updater(DefaultConfig.TELEGRAM_TOKEN, use_context=True)

    dp = updater.dispatcher

    # message handler
    dp.add_handler(MessageHandler(Filters.text, main_handler))

    # suggested_actions_handler
    dp.add_handler(CallbackQueryHandler(main_handler, pass_chat_data=True, pass_user_data=True))

    # Start the Bot
    if DefaultConfig.MODE == 'webhook':

        updater.start_webhook(listen="0.0.0.0",
                              port=int(DefaultConfig.PORT),
                              url_path=DefaultConfig.TELEGRAM_TOKEN)
        updater.bot.setWebhook(DefaultConfig.WEBHOOK_URL + DefaultConfig.TELEGRAM_TOKEN)

        logging.info(f"Start webhook mode on port {DefaultConfig.PORT}")
    else:
        updater.start_polling()
        logging.info(f"Start polling mode")

    updater.idle()


class DefaultConfig:
    PORT = int(os.environ.get("PORT", 3978))
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
    MODE = os.environ.get("MODE", "polling")
    WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "")


if __name__ == '__main__':
    main()
