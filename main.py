import sqlite3
import telebot
from telebot import types
import random

# Задаем токен бота и подключаемся к Telegram API
token = ''  # Ваш токен брать его у ботфатзер
bot = telebot.TeleBot(token)

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect('users.db')

# Функция для создания таблицы users
def create_users_table():
    with connect_db() as conn:
        cursor = conn.cursor()
        # SQL-запрос для создания таблицы
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            user_group_id INTEGER,
            user_name TEXT
        );
        '''
        cursor.execute(create_table_query)

# Функция для получения доступа пользователя
def get_access(user_id):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT user_group_id, user_name FROM users WHERE user_id=?', (user_id,))
        result = cursor.fetchone()
        return result

# Функция для добавления пользователя в базу данных 
def add_user(user_id, user_name):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (user_id, user_name, user_group_id) VALUES (?, ?, ?)',
                       (user_id, user_name, '0'))  # Новые пользователи начинают с группы '0'
        conn.commit()

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    user_id = message.chat.id
    access = get_access(user_id)

    if access:
        bot.send_message(message.chat.id, 'Вы уже зарегистрированы как {}.'.format(access[1])) 
    else:
        msg = bot.send_message(message.chat.id, 'Привет! Пожалуйста, введите Ваше имя для регистрации:')
        bot.register_next_step_handler(msg, process_name)
        btn_greet = types.KeyboardButton("/play")
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(btn_greet)
        
    # Добавляем кнопки после сообщения
    
    
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == '👋 Поздороваться':
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # создание новых кнопок
        btn_check = types.KeyboardButton('Сосал?')
        btn_creator = types.KeyboardButton('Создавал Андрей')
        bot.send_message(message.from_user.id, 'мой github ' + '[ссылка](https://github.com/asdeshnick)', parse_mode='Markdown')
        markup.add(btn_check, btn_creator)
        bot.send_message(message.from_user.id, '❓ Выберите ', reply_markup=markup)  # ответ бота

    elif message.text == 'Сосал?':  
        loh = ["Сосал", "Нет"]
        loh_bot = random.choice(loh)
        bot.send_message(message.from_user.id, loh_bot)  # ответ бота

def process_name(message):
    user_id = message.chat.id
    user_name = message.text.strip()
    print(user_name, user_id)

    # Добавляем пользователя в базу данных
    add_user(user_id, user_name)

    bot.send_message(message.chat.id, 'Спасибо, {}! Вы успешно зарегистрированы.'.format(user_name))

@bot.message_handler(commands=['admin']) # adminку мне в падлу делать, но ее сделать легко 
def handle_admin_command(message):
    access = get_access(message.chat.id)

    if access:
        if access[0] == '1':
            bot.send_message(message.chat.id, 'Привет Admin!')
        else:
            bot.send_message(message.chat.id, 'Привет User!')
    else:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы в системе!')

# Запуск бота
if __name__ == '__main__':
    create_users_table()
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка: {e}")
        bot.stop_bot()

