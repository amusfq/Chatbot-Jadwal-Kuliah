import logging
import re
import requests
from bs4 import BeautifulSoup
from telegram.ext import (Updater, CommandHandler, 
        MessageHandler, Filters, ConversationHandler)

# TOKEN DARI BOT TELEGRAM
TOKEN = "BOT_TOKEN_DISINI"
# URL WEBSITE
BASE_URL = "URL_HALAMAN_JADWAL_WEBSITE_ASTE_DISINI"
LOGIN_URL = "URL_HALAMAN_LOGIN_PASTE_DISINI.php"
FORM_DATA = {'txtUserID': 'username', 'txtPassword': 'password', 'signIn': 'Login'}
# STATE PILIHAN 
PILIHAN, DONE = range(2)

# LOGGING HANDLER
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)

# FUNGSI SAAT BOT PERTAMA KALI DIJALANKAN
def start(update, context):
    sender = update.message.chat.first_name
    update.message.reply_text("Selamat datang, saya adalah Chatbot Jadwal Kuliah")
    update.message.reply_text("Daftar perintah bot: \n1. Cek Jadwal\n2. Bantuan\n3. Keluar")
    return PILIHAN

# FUNGSI MENGECEK INPUT DARI USER
def user_input(update, context):
    # MENGAMBIL INPUT DARI USER
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
    
    # DIKIRIM KEMBALI KE USER
    update.message.reply_text(reply)
    # KEMBALI KE STATE PILIHAN
    return PILIHAN

# FUNGSI UNTUK MENGAKHIRI PERCAKAPAN
def done(update, context):
    update.message.reply_text("Sampai jumpa lagi")
    return ConversationHandler.END

# FUNGSI LOGGING KETIKA ADA ERROR
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    
def get_jadwal(update, context):
    # Membuat session pada request
    request_session = requests.Session()
    # Melakukan post data (login)
    request_session.post(LOGIN_URL, data=FORM_DATA)
    # Mengambil halaman jadwal
    request_jadwal = request_session.get(BASE_URL)
    soup = BeautifulSoup(request_jadwal.text, 'html.parser')
    # Mencari table jadwal
    table = soup.select('table')[3]
    tr = table.select('tr')
    result = ""
    for i in tr:
        result += ' '.join(i.text.split()) + '\n'
    update.message.reply_text(result)

# FUNGSI UTAMA YANG AKAN TERUS MENERUS LOOPING
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    # FUNGSI YANG MENGHANDLE INPUT DARI USER
    conv_handler = ConversationHandler(
        # MENJALANKAN FUNGSI START() SAAT BOT PERTAMAKALI DIGUNAKAN
        entry_points=[CommandHandler('start', start)],
        # BOT MENGUNGGU INPUT DARI PENGGUNA KEMUDIAN DIARAHKAN 
        # KE FUNGSI SESUAI INPUT STATENYA
        states={
            PILIHAN: [MessageHandler(Filters.text, user_input)],
            DONE: [MessageHandler(Filters.text, done)],
        },
        # FUNGSI YANG OTOMATIS TERPANGGIL KETIKA STATE DIATAS 
        # TIDAK TERPANGGIL 
        fallbacks=[MessageHandler(Filters.regex('^(Selesai|selesai)$'), done)]
    )

    dp.add_handler(conv_handler)
    dp.add_error_handler(error)
    updater.start_polling()
    updater.idle()

# SAAT APLIKASI DIJALANKAN FUNGSI MAIN() AKAN DIJALANKAN
if __name__ == '__main__':
    main()
