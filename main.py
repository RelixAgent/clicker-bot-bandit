import sqlite3
from vkbottle import API, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Bot, Message
from loguru import logger
from random import randint, choice
from config import token, admin_id, group_id

db = sqlite3.connect("clicker.db")
sql = db.cursor()
sql.execute("""CREATE TABLE IF NOT EXISTS users (
user INT,
nick TEXT,
balance INT,
click INT,
role TEXT,
captcha INT,
captcha_q TEXT,
referals INT
)""")

sql.execute("""CREATE TABLE IF NOT EXISTS bot (
users INT
)""")
db.commit()

logger.disable("vkbottle") #отключение дебага

api = API(token)
bot = Bot(token=token)
bot.on.vbml_ignore_case = True #игнор регистра

async def beuty(balance, plus):
    s_balance = str(balance+plus)
    s_balance = s_balance[::-1]
    empty = ''
    sh = 0
    for i in s_balance:
        if sh == 3:
            empty += f'.{i}'
            sh = 1
        else:
            empty += i
            sh += 1
    empty = empty[::-1]
    return empty

async def beuty2(plus):
    s_balance = str(plus)
    s_balance = s_balance[::-1]
    empty = ''
    sh = 0
    for i in s_balance:
        if sh == 3:
            empty += f'.{i}'
            sh = 1
        else:
            empty += i
            sh += 1
    empty = empty[::-1]
    return empty



@bot.on.message(text=["начать", 'я', '👮Профиль', 'назад'])
async def start(message: Message):
    menu = (
        Keyboard()
    .add(Text("💰Заработок"), color=KeyboardButtonColor.POSITIVE)
    .add(Text("👮Профиль"), color=KeyboardButtonColor.PRIMARY)
    .add(Text("Вывод"), color=KeyboardButtonColor.POSITIVE)
    .row()
    .add(Text("Статистика"), color=KeyboardButtonColor.SECONDARY)
    .add(Text("⚙️Настройки"), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text("Пригласи друга"), color=KeyboardButtonColor.POSITIVE)
    )
    human = await api.users.get(user_ids={message.from_id})
    name = human[0].first_name
    sql.execute(f"SELECT * FROM users WHERE user = {message.from_id}")
    if sql.fetchone() is None:
        if message.from_id == admin_id:
            sql.execute(f"INSERT INTO users VALUES ( {message.from_id}, ?, {2000000000}, {0}, 'admin', {0}, 'None', {0} )", (name,))
        else:
            sql.execute(f"INSERT INTO users VALUES ( {message.from_id}, ?, {0}, {0}, 'user', {0}, 'None', {0} )", (name,))
            referal = message.ref
            if referal == None:
                pass
            else:
                referals = sql.execute(f"SELECT referals FROM users WHERE user = {referal}").fetchone()[0]
                balance = sql.execute(f"SELECT balance FROM users WHERE user = {referal}").fetchone()[0]
                sql.execute(f"UPDATE users SET balance = {balance+50000000} WHERE user = {referal} ")
                sql.execute(f"UPDATE users SET balance = {referals+1} WHERE user = {referal} ")

                await api.messages.send(message=f"ты пригласил @id{message.from_id}\nтебе выдано $50.000.000", user_id=referal, random_id=0)
        sql.execute(f"SELECT * FROM bot ")
        if sql.fetchone() is None:
            sql.execute(f"INSERT INTO bot VALUES ({1})")
        else:
            users = sql.execute(f"SELECT users FROM bot ").fetchone()[0]
            sql.execute(f"UPDATE bot SET users = {users+1}")
        await message.answer(f"привет {name}, ты успешно зарегистрирован", keyboard=menu)
    else:
        nickname = sql.execute(f"SELECT nick FROM users WHERE user = {message.from_id}").fetchone()[0]
        click = sql.execute(f"SELECT click FROM users WHERE user = {message.from_id}").fetchone()[0]
        balance = sql.execute(f"SELECT balance FROM users WHERE user = {message.from_id}").fetchone()[0]
        balance = await beuty2(balance)
        await message.answer(f"Йоу, {nickname}\nТвой баланс: ${balance}.\nКликов: {click}", keyboard=menu)

    db.commit()

@bot.on.message(text="💰Заработок")
async def work(message: Message):
    work = (
        Keyboard()
        .add(Text("Клик"), color=KeyboardButtonColor.POSITIVE)
        #.add(Text("Монетка"), color=KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("Назад"), color=KeyboardButtonColor.SECONDARY)
    )
    nickname = sql.execute(f"SELECT nick FROM users WHERE user = {message.from_id}").fetchone()[0]
    await message.answer(f"{nickname}, ты в меню заработка", keyboard=work)

    db.commit()



@bot.on.message(text="клик")
async def click(message: Message):
    captcha = randint(1, 50)
    if captcha == 10:
        captcha_k = (
            Keyboard()
            .add(Text("Где"), color=KeyboardButtonColor.SECONDARY)
            .add(Text("Почему"), color=KeyboardButtonColor.SECONDARY)
            .add(Text("Зачем"), color=KeyboardButtonColor.SECONDARY)
        )
        question = ["Где", "Почему", "Зачем"]
        question_r = choice(question)
        anti_bot = randint(1, 25)
        anti_bot2 = randint(1, 5)
        anti_bot_ready = str(anti_bot2) * anti_bot
        await message.answer(f"Капча: выбери правильное слово\n{anti_bot_ready} {question_r}", keyboard=captcha_k)
        sql.execute(f"UPDATE users SET captcha = {1} WHERE user = {message.from_id}")
        sql.execute(f"UPDATE users SET captcha_q = ? WHERE user = {message.from_id}", (question_r,))
    else:
        clicker = (
            Keyboard()
            .add(Text("клик"), color=KeyboardButtonColor.POSITIVE)
            .add(Text("назад"), color=KeyboardButtonColor.SECONDARY)
        )
        click = sql.execute(f"SELECT click FROM users WHERE user = {message.from_id}").fetchone()[0]
        balance = sql.execute(f"SELECT balance FROM users WHERE user = {message.from_id}").fetchone()[0]
        nickname = sql.execute(f"SELECT nick FROM users WHERE user = {message.from_id}").fetchone()[0]
        plus = randint(100000, 300000)
        sql.execute(f"UPDATE users SET balance = {balance+plus} WHERE user = {message.from_id}")
        sql.execute(f"UPDATE users SET click = {click+1} WHERE user = {message.from_id}")
        empty = await beuty(balance, plus)
        plus = await beuty2(plus)
        await message.answer(f"{nickname}, ты получил +${plus}.\n💰Баланс: {empty}.\n👆Кликов: {click+1}")

    db.commit()

@bot.on.message(text=['Почему', 'Где', 'Зачем'])
async def captcha_answer(message: Message):
    captcha_u = sql.execute(f"SELECT captcha FROM users WHERE user = {message.from_id} ").fetchone()[0]
    question_u = sql.execute(f"SELECT captcha_q FROM users WHERE user = {message.from_id} ").fetchone()[0]
    if captcha_u == 1:
        if question_u == message.text:
            clicker = (
                Keyboard()
                .add(Text("клик"), color=KeyboardButtonColor.POSITIVE)
                .add(Text("назад"), color=KeyboardButtonColor.SECONDARY)
                )
            sql.execute(f"UPDATE users SET captcha = {0} WHERE user = {message.from_id}")
            sql.execute(f"UPDATE users SET captcha_q = 'None' WHERE user = {message.from_id}")
            await message.answer("Ты прошёл капчу", keyboard=clicker)
        else:
            await message.answer("Ответ неверный")
    else:
        pass

    db.commit()

@bot.on.message(text="Вывод")
async def deposit(message: Message):
    balance = sql.execute(f"SELECT balance FROM users WHERE user = {message.from_id}").fetchone()[0]
    nickname = sql.execute(f"SELECT nick FROM users WHERE user = {message.from_id}").fetchone()[0]
    if balance < 1000000000:
        await message.answer("🚫для вывода нужно минимум 1ккк")
    else:
        sql.execute(f"UPDATE users SET balance = {0} WHERE user = {message.from_id}")
        balance = await beuty2(balance)
        await message.answer(f"Заявка на вывод отправлена\nБудет выведено ${balance}")
        await api.messages.send(message=f"Заявка на вывод от @id{message.from_id}\nнужно отправить ему ${balance}", user_id=477715545, random_id=0)
    
    db.commit()

@bot.on.message(text="Статистика")
async def bot_stat(message: Message):
    users = sql.execute(f"SELECT users FROM bot ").fetchone()[0]
    await message.answer(f"Игроков всего - {users}")

@bot.on.message(text=["Настройки", "⚙️Настройки"])
async def settings(message: Message):
    user_settings = (
        Keyboard()
        .add(Text("Сменить ник"), color=KeyboardButtonColor.POSITIVE)
        .add(Text("назад"), color=KeyboardButtonColor.PRIMARY)
    )
    await message.answer("⚙️Ты попал в меню настроек", keyboard=user_settings)

@bot.on.message(text="Сменить ник")
async def bot_stat(message: Message):
    await message.answer("Напиши \"ник\" и как я тебя могу называть")

@bot.on.message(text=["ник <new_nick>"])
async def change_nick(message: Message, new_nick=None):
    if len(new_nick) > 15:
        await message.answer("ник должнен быть менее 15 символов")
    else:
        sql.execute(f"UPDATE users SET nick = ? WHERE user = {message.from_id} ", (new_nick,))
        await message.answer(f"Теперь твой ник {new_nick}")

    db.commit()


@bot.on.message(text="Пригласи друга")
async def ref_get(message: Message):
    nickname = sql.execute(f"SELECT nick FROM users WHERE user = {message.from_id}").fetchone()[0]
    referals = sql.execute(f"SELECT referals FROM users WHERE user = {message.from_id}").fetchone()[0]
    await message.answer(f"""{nickname}, твоя реферальная ссылка:\nhttps://vk.com/write-{group_id}?ref={message.from_id}&ref_source=1 
    \nПриведи друга по своей ссылке и получи $50.000.000
    Всего приглашено тобой: {referals}""")



print("Готово")
bot.run_forever()