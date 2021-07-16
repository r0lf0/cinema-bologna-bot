def send_message(bot, chat_id, message):
    if len(message) > 4096:
        for x in range(0, len(message), 4096):
            bot.send_message(chat_id, message[x:x+4096])
    else:
        bot.send_message(chat_id, message)