import telebot
from telebot import types
import requests
import xml.etree.ElementTree as ET

# ТОКЕН БОТА
bot = telebot.TeleBot('6919365199:AAEJNMO1nOYsi25lhDTYfUNUYZWNCa906uQ')

#API ПОГОДЫ
OPENWEATHERMAP_API_KEY = '362926bd81ac66dcdf6a602df5003fbc'

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=ru'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        weather = data['weather'][0]['description']
        temperature = data['main']['temp']
        return f'Погода в {city}: {weather}, температура: {temperature}°C'
    else:
        return 'Город не найден.'

def get_joke(age_limit):
    url = 'https://www.anekdot.ru/rss/export_j.xml'
    response = requests.get(url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        items = root.findall('./channel/item')
        jokes = [item.find('description').text for item in items]
        if jokes:
            # фильтрация по возрастному ограничению
            if age_limit == '0+':
                return jokes[0]  
            elif age_limit == '18+':
                return jokes[1]  
            else:
                return 'Некорректное возрастное ограничение.'
        else:
            return 'Анекдотов не найдено.'
    else:
        return 'Не удалось получить анекдоты.'

def main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    weather_button = types.KeyboardButton('Погода')
    joke_button = types.KeyboardButton('Анекдоты')
    compare_weather_button = types.KeyboardButton('Сравнить погоду')
    markup.add(weather_button, joke_button, compare_weather_button)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Что ты хочешь узнать?", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Погода")
def ask_city(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    main_menu_button = types.KeyboardButton('Главное меню')
    markup.add(main_menu_button)
    msg = bot.send_message(message.chat.id, "Введите название города:", reply_markup=markup)
    bot.register_next_step_handler(msg, send_weather)

def send_weather(message):
    if message.text == 'Главное меню':
        bot.send_message(message.chat.id, "Возвращение в главное меню.", reply_markup=main_menu())
    else:
        city = message.text
        weather_info = get_weather(city)
        bot.send_message(message.chat.id, weather_info, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Анекдоты")
def ask_age_limit(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    kids_button = types.KeyboardButton('0+')
    adult_button = types.KeyboardButton('18+')
    main_menu_button = types.KeyboardButton('Главное меню')
    markup.add(kids_button, adult_button, main_menu_button)
    msg = bot.send_message(message.chat.id, "Выберите возрастное ограничение:", reply_markup=markup)
    bot.register_next_step_handler(msg, send_joke)

def send_joke(message):
    if message.text == 'Главное меню':
        bot.send_message(message.chat.id, "Возвращение в главное меню.", reply_markup=main_menu())
    else:
        age_limit = message.text.lower()
        joke = get_joke(age_limit)
        bot.send_message(message.chat.id, joke, reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Сравнить погоду")
def ask_cities(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    main_menu_button = types.KeyboardButton('Главное меню')
    markup.add(main_menu_button)
    msg = bot.send_message(message.chat.id, "Введите названия двух городов через запятую (например, Москва, Санкт-Петербург)", reply_markup=markup)
    bot.register_next_step_handler(msg, compare_weather)

def compare_weather(message):
    if message.text == 'Главное меню':
        bot.send_message(message.chat.id, "Возвращение в главное меню.", reply_markup=main_menu())
    else:
        cities = message.text.split(',')
        if len(cities) != 2:
            bot.send_message(message.chat.id, "Пожалуйста, введите два города через запятую.", reply_markup=main_menu())
            return
        
        city1 = cities[0].strip()
        city2 = cities[1].strip()
        
        weather1 = get_weather(city1)
        weather2 = get_weather(city2)
        
        comparison = f"Сравнение погоды:\n\n{weather1}\n\n{weather2}"
        bot.send_message(message.chat.id, comparison, reply_markup=main_menu())

bot.polling()
