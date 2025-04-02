import sqlite3
import telebot
from telebot import types
import random

token = ''
bot = telebot.TeleBot(token)

# Функция для подключения к базе данных
def connect_db():
    return sqlite3.connect('users.db')

# Функция для создания таблицы users
def create_users_table():
    with connect_db() as conn:
        cursor = conn.cursor()
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
        return cursor.fetchone()

# Функция для добавления пользователя в базу данных 
def add_user(user_id, user_name):
    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT OR IGNORE INTO users (user_id, user_name, user_group_id) VALUES (?, ?, ?)',
                      (user_id, user_name, 0))
        conn.commit()

@bot.message_handler(commands=['start'])
def handle_start_command(message):
    user_id = message.chat.id
    access = get_access(user_id)

    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("проверка на лоха")
    btn3 = types.KeyboardButton("Создавал Андрей")
    markup.add(btn1, btn2, btn3)
    
    if access:
        bot.send_message(user_id, f'Вы уже зарегистрированы как {access[1]}.', reply_markup=markup)
    else:
        msg = bot.send_message(user_id, 'Привет! Пожалуйста, введите ваше имя для регистрации:', reply_markup=markup)
        bot.register_next_step_handler(msg, process_name)

def process_name(message):
    user_id = message.chat.id
    user_name = message.text.strip()
    add_user(user_id, user_name)
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("👋 Поздороваться")
    btn2 = types.KeyboardButton("проверка на лоха")
    btn3 = types.KeyboardButton("Создавал Андрей")
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(user_id, f'Спасибо, {user_name}! Вы успешно зарегистрированы.', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == '👋 Поздороваться':
        markup = types.InlineKeyboardMarkup()
        github_btn = types.InlineKeyboardButton("GitHub", url='https://github.com/asdeshnick')
        markup.add(github_btn)
        bot.send_message(message.chat.id, 'Мой GitHub:', reply_markup=markup)
        
    elif message.text == 'проверка на лоха':
        loh = ["Лох", "Не лох"]
        bot.send_message(message.chat.id, random.choice(loh))
        
    elif message.text == 'Создавал Андрей':
        bot.send_message(message.chat.id, 'Да, этого бота создал Андрей!')

@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    access = get_access(message.chat.id)
    
    if not access:
        return bot.send_message(message.chat.id, 'Вы не зарегистрированы в системе!')
    
    if access[0] == 1:
        bot.send_message(message.chat.id, 'Привет Admin!')
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Управление пользователями", callback_data='manage_users')
        btn2 = types.InlineKeyboardButton("Просмотр статистики", callback_data='view_stats')
        markup.add(btn1, btn2)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Привет User! У вас нет прав администратора.')

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.data == 'manage_users':
        bot.answer_callback_query(call.id, "Вы выбрали управление пользователями.")
        # Здесь можно добавить логику управления пользователями
    elif call.data == 'view_stats':
        bot.answer_callback_query(call.id, "Вы выбрали просмотр статистики.")
        # Здесь можно добавить логику просмотра статистики

if __name__ == '__main__':
    create_users_table()
    bot.polling(none_stop=True)
