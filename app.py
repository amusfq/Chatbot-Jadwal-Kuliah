import logging
import re
import requests
from bs4 import BeautifulSoup
from telegram.ext import (Updater, CommandHandler, 
        MessageHandler, Filters, ConversationHandler)

TOKEN = "897801904:AAEFt5WoXfuwZiXC_guUma25NO1kj0Us0wk"
BASE_URL = "http://akademik.narotama.ac.id/akademik/mhs_jadwal.php"
LOGIN_URL = "http://akademik.narotama.ac.id/akademik/checklogin.php"
FORM_DATA = {'txtUserID': 'username', 'txtPassword': 'password', 'signIn': 'Login'}

PILIHAN, DONE = range(2)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

def start(update, context):
    sender = update.message.chat.first_name
    update.message.reply_text("Selamat datang, saya adalah Chatbot Jadwal Kuliah")
    update.message.reply_text("Daftar perintah bot: \n1. Cek Jadwal\n2. Bantuan\n3. Keluar")
    return PILIHAN

def user_input(update, context):
    text = update.message.text.lower()
    reply = ''
    if re.match('^(1|cek jadwal)$', text) is not None:
        return get_jadwal(update, context)
    elif re.match('^(2|bantuan)$', text) is not None:
        reply = 'Daftar perintah bot: \n1. Cek Jadwal\n2. Bantuan\n3. Keluar'
    elif re.match('^(3|keluar)$', text) is not None:
        context.user_data.clear()
        update.message.reply_text("Sampai jumpa lagi")
        return ConversationHandler.END
    else:
        reply = 'Kata kunci tidak ditemukan'
    
    update.message.reply_text(reply)
    return PILIHAN

def done(update, context):
    update.message.reply_text("Sampai jumpa lagi")
    return ConversationHandler.END

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
def get_jadwal(update, context):
    request_session = requests.Session()
    request_login = request_session.post(LOGIN_URL, data=FORM_DATA)
    soup = BeautifulSoup(request_login.text, 'html.parser')

    request_jadwal = request_session.get(BASE_URL)
    soup = BeautifulSoup(request_jadwal.text, 'html.parser')
    
    table = soup.select('table')[3]
    tr = table.select('tr')
    result = ""
    for i in tr:
        result += ' '.join(i.text.split()) + '\n'
    update.message.reply_text(result)

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PILIHAN: [MessageHandler(Filters.text, user_input)],
            DONE: [MessageHandler(Filters.text, done)],
        },
        fallbacks=[MessageHandler(Filters.regex('^(Selesai|selesai)$'), done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()