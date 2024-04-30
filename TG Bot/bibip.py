import telebot
from telebot import types
import requests
import time
import datetime

tokken = '7159868970:AAFsm9OEogyC_JKphchr_YAfMw1hEx2iDHY'
bot = telebot.TeleBot(tokken)

flag = False  # флажок для определения подписки на рассылку
every_day = False  # флажок для определения подписки на ежедневную рассылку


#  Запись запросов в файл
def write_req(mess, name):
    try:
        with open("text1.txt", "a", encoding='utf8') as file:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            file.write(f"{now}:--{name} -- {mess}\n")
    except Exception as e:
        print(f"Error writing to file: {str(e)}")


#  организация рассылки
def your_curr(message, st):
    global flag
    if flag is False:
        bot.send_message(message.chat.id, "Вы подписались на рассылку! Чтобы отписаться"
                                          " от рассылки снова вызовите команду /news.")
        flag = True
    while True:
        time.sleep(1)
        #  ежечасная рассылка
        if ":" not in st:
            if datetime.datetime.now().time().strftime("%H:%M:%S")[3:] == '00:00':
                if flag:
                    try:
                        response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=usd')
                        data = response.json()

                        response_1 = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=btc')
                        data_1 = response_1.json()

                        bot.send_message(message.chat.id, "Курсы валют на данный момент:\n"
                                                          f"1 $ = {data['data']['rates']['RUB']} rub \n"
                                                          f"1 btc = {data_1['data']['rates']['USD']} $ \n"
                                                          "Чтобы отключить рассылку снова вызовите команду /news")
                    except Exception as e:
                        bot.send_message(message.chat.id, 'Не удалось вывести данные о теущих курсах валют(')
                else:
                    break
        else:  # ежедневная рассылка
            if datetime.datetime.now().time().strftime("%H:%M:%S") == st + ':00':
                if flag:
                    try:
                        response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=usd')
                        data = response.json()

                        response_1 = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=btc')
                        data_1 = response_1.json()

                        bot.send_message(message.chat.id, "Курсы валют на данный момент:\n"
                                                          f"1 $ = {data['data']['rates']['RUB']} rub \n"
                                                          f"1 btc = {data_1['data']['rates']['USD']} $ \n"
                                                          "Чтобы отключить рассылку снова вызовите команду /news")
                    except Exception as e:
                        bot.send_message(message.chat.id, 'Не удалось вывести данные о теущих курсах валют(')
                else:
                    break


@bot.message_handler(commands=['news'])
def dist_rib(message):
    global flag
    if flag is False:
        mark_up = types.InlineKeyboardMarkup()
        bt1 = types.InlineKeyboardButton("Каждый день", callback_data='day')
        bt2 = types.InlineKeyboardButton("Каждый час", callback_data='hour')
        mark_up.row(bt1, bt2)
        bot.send_message(message.chat.id, "Выберите период рассылки", reply_markup=mark_up)
    else:
        bot.send_message(message.chat.id, "Вы отписались от рассылки")
        flag = False


@bot.callback_query_handler(func=lambda callback: callback.data in ('day', 'hour'))
def callback_message_1(callback):
    global every_day

    if callback.data == 'day' and flag is False and every_day is False:
        bot.send_message(callback.message.chat.id, 'Выберите время для ежедневной рассылки(например "14:38")')
        every_day = True
    elif callback.data == 'hour' and flag is False:
        your_curr(callback.message, '10')
    elif callback.data in ('day', 'hour') and flag is True:
        bot.send_message(callback.message.chat.id, 'Вызовите команду снова')


@bot.message_handler(commands=['start'])
def main(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Перейти на сайт биржи")
    btn2 = types.KeyboardButton("Узнать курс валют")
    markup.row(btn1)
    markup.row(btn2)
    bot.send_message(message.chat.id, f"Привет👋, {message.from_user.first_name.capitalize()}. "
                                      f"Теперь ты можешь воспользоваться моими услугами связанными с валютным рынком.\n"
                                      f"Вызови команду /news, чтобы подписаться на рассылку новостей о состоянии курса"
                                      f" валют.", reply_markup=markup)


@bot.message_handler()
def get_text_messages(message):
    global every_day

    write_req(message.text, message.from_user.first_name)

    response = requests.get(f'https://api.coinbase.com/v2/exchange-rates?currency={message.text.lower()}')
    # проверка на то, чтобы при плучении любого сообщения о времени бот не включал рассылку
    if len(message.text) == 5 and ":" in message.text and every_day is True:
        try:
            if (-1 < int(message.text.split(':')[0]) < 25) and (-1 < int(message.text.split(':')[1]) < 61):
                every_day = False
                your_curr(message, message.text)
        except Exception:
            pass

    if message.text == "Узнать курс валют" or message.text == '/currency':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("USD -> RUB", callback_data='show1')
        btn2 = types.InlineKeyboardButton("EUR -> RUB", callback_data='show2')
        btn3 = types.InlineKeyboardButton("BTC -> RUB", callback_data='show3')
        btn4 = types.InlineKeyboardButton("BTC -> USD", callback_data='show4')
        btn5 = types.InlineKeyboardButton("укажите сами", callback_data='show5')
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        markup.row(btn5)
        bot.send_message(message.chat.id, "Вот некторые из них:", reply_markup=markup)

    elif message.text == "Перейти на сайт биржи" or message.text == '/check_exchanges':
        bot.send_message(message.chat.id, "https://www.moex.com/")
    #  отправка текущего курса валюты, указанного пользователем
    elif str(response.status_code)[0] == '2':
        try:
            data = response.json()
            bot.send_message(message.chat.id, f"1 {message.text.lower()} = {data['data']['rates']['USD']} $")
        except Exception as e:
            bot.send_message(message.chat.id, "Возможно, запрос некорректен")
    every_day = False


url = f'https://api.coinbase.com/v2/exchange-rates?currency=usd'


#  реагирование на нажатие Inline кнопок и вывод курса
@bot.callback_query_handler(func=lambda callback: True)
def callback_message(callback):
    if callback.data == 'show1':
        try:
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=usd')
            data = response.json()
            bot.send_message(callback.message.chat.id, f"1 $ = {data['data']['rates']['RUB']} rub")
        except Exception as e:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так...')

    elif callback.data == 'show2':
        try:
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=eur')
            data = response.json()
            bot.send_message(callback.message.chat.id, f"1 € = {data['data']['rates']['RUB']} rub")
        except Exception as e:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так...')

    elif callback.data == 'show3':
        try:
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=btc')
            data = response.json()
            bot.send_message(callback.message.chat.id, f"1 btc = {data['data']['rates']['RUB']} rub")
        except Exception as e:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так...')

    elif callback.data == 'show4':
        try:
            response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=btc')
            data = response.json()
            bot.send_message(callback.message.chat.id, f"1 btc = {data['data']['rates']['USD']} $")
        except Exception as e:
            bot.send_message(callback.message.chat.id, 'Что-то пошло не так...')

    elif callback.data == 'show5':
        bot.send_message(callback.message.chat.id, 'Чтобы узнать курс валюты(в USD), не входящей в базовый перчень, \
необходимо указать её код(ISO). Например "GBP"')


bot.polling(none_stop=True)
