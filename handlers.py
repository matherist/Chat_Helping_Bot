from aiogram import Dispatcher, types
# from dotenv import load_dotenv
# import os
# import logging
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# from aiogram.dispatcher.middlewares import BaseMiddleware
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.contrib.middlewares.logging import LoggingMiddleware
from models import User, Question, Answer, SessionLocal
# from middlewares import SQLAlchemySessionManager
from sqlalchemy import and_, desc
from config import dp


        
class Quiz(StatesGroup):
    q_number = State()



async def update_q_number(state: FSMContext, num: int):
    await state.update_data(q_number=num)


async def get_current_question_from_state(state: FSMContext):
    question_number = await state.get_data()
    question_number = question_number.get('q_number', 1)
    return question_number

async def check_answer(answer: str, question_number: int, db_session):
    return None

async def send_question(message: types.Message, question: str, retry = False):
    await message.answer(question)

# @dp.message_handler(commands=["Start"])
async def start_cmd(message: types.Message):
    db_session = message.conf['db_session']
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user:
        # user does not exist yet, lets create one
        user = User(name=message.from_user.username, telegram_id=message.from_user.id)
        db_session.add(user)
        db_session.commit()
    await message.answer('''Добро пожаловать в наш помощник-бот!''')
    await message.answer("Выберите в меню нужный для вас пункт.💫")
    await message.answer("Наша главная старница ... ")


# @dp.message_handler(commands=["quiz"])
async def quiz_cmd(message: types.Message):
    db_session = message.conf['db_session']
    user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
    await Quiz.q_number.set()
    state = dp.current_state()
    first_question = db_session.query(Question).first()
    if first_question:
        await update_q_number(state, first_question.id)
        await message.answer(f"Первый вопрос: {first_question}")

# ПРОЦЕСС ПРОВЕРКИ СООБЩЕНИЙ

async def process_answer(message: types.Message, state: FSMContext):
    db_session = message.conf['db_session']
    answer = message.text.strip()

    q_num = await get_current_question_from_state(state)
    current_question = db_session.query(Question).filter(Question.id == q_num).first()
    length = db_session.query(Question).count()

    if q_num < length:
        user = db_session.query(User).filter_by(telegram_id=message.from_user.id).first()
        user_answer = Answer(text=answer, user=user, question=current_question)
        db_session.add(user_answer)
        db_session.commit()

        next_question = db_session.query(Question).filter(Question.id > q_num).first()
        await send_question(message, next_question.text)
        await update_q_number(state, next_question.id)
    else:
        user = db_session.query(User).filter(User.telegram_id == message.from_user.id).first()
        if user:
            user.succeeded = True
            db_session.commit()
        await message.answer("Мы очень благодарны за ваш отзыв. До встречи!")
        await state.finish()



# @dp.message_handler(commands=["Cancel"])
async def cancel_quiz(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Спасибо за ваши ответы. До встреч! 💕")


# @dp.message_handler(commands=["Help"])
async def help_quiz(message: types.Message, state: FSMContext):
    await message.answer('''Добро пожаловать в наш помощник-бот! \n Вы тут можете пройти опрос, кликнув на /quiz . \n Или можете получить дополнительную информацию, кликнув /info .  \n Кликнув на /events вы можете узнать про приближающиеся мероприятия.
    ''')


# @dp.message_handler(commands=["Information"])
async def info_cmd(message: types.Message, state: FSMContext):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    buttons = ["Инвалидность", "Пособия", "Где погулять", "Льготы", "Образование"]
    
    # Добавляем кнопки с обратными вызовами
    # for button_text in buttons:
        # keyboard.add(KeyboardButton(button_text))
    keyboard.add(*buttons)

    
    await message.answer('Выберите одну из следующих опций:', reply_markup=keyboard)



# @dp.message_handler(commands=["Events"])
async def events_cmd(message: types.Message, state: FSMContext):
    await message.answer('''Soon coming''')

#BUTTONS
async def set_default_commands(dp):
    await dp.bot.set_my_commands([
        types.BotCommand("start", "Запустить бота"),
        types.BotCommand("help", "Помощь"),
        types.BotCommand("quiz", "Запустить опрос"),
        types.BotCommand("info", "Информация"),
        types.BotCommand("cancel", "Остановить опрос"),
        types.BotCommand("events", "Ближайшие мероприятия"),
    ])


async def handle_invalidnost(message: types.Message):

    await message.answer("Текст для Инвалидности")


async def handle_posobia(message: types.Message):
    await message.answer("Текст для Пособии")


async def handle_walk(message: types.Message):
    await message.answer("Текст для мест для Прогулок")


async def handle_lgoty(message: types.Message):
    await message.answer("Текст для Льгот")


async def handle_obrazovanie(message: types.Message):
    await message.answer("Текст для списка мест по получению Образования")


#LIST OF FUNCTIONS OF BUTTONS
def register_hadlers(dp: Dispatcher):
    dp.register_message_handler(start_cmd, commands=["start"])
    dp.register_message_handler(help_quiz, commands=["help"], state="*")  
    dp.register_message_handler(quiz_cmd, commands=["quiz"])
    dp.register_message_handler(cancel_quiz, commands=["cancel"], state="*")    
    dp.register_message_handler(info_cmd, commands=["info"], state="*")
    dp.register_message_handler(events_cmd, commands=["events"], state="*")

    dp.register_message_handler(handle_invalidnost, Text(equals="Инвалидность"))
    dp.register_message_handler(handle_posobia, Text(equals="Пособия"))
    dp.register_message_handler(handle_walk, Text(equals="Где погулять"))
    dp.register_message_handler(handle_lgoty, Text(equals="Льготы"))
    dp.register_message_handler(handle_obrazovanie, Text(equals="Образование"))

    dp.register_message_handler(process_answer, state=Quiz.q_number)


# Зарегистрируйте обработчик обратных вызовов
# dp.register_callback_query_handler(button_click_handler)