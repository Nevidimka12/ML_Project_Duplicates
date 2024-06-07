import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext

from config import api_token
from get_ans import predict, prepare_data

API_TOKEN = api_token

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


class Form(StatesGroup):
    waiting_for_first_question = State()
    waiting_for_second_question = State()


start_kb = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Ввести вопросы")]], resize_keyboard=True, one_time_keyboard=True)


@dp.message(Command(commands=['start']))
async def send_welcome(message: types.Message):
    await message.reply("Привет!\nЯ бот для нахождения дубликатов вопросов\nНажми на кнопку, чтобы начать.", reply_markup=start_kb)


@dp.message()
async def echo(message: types.Message, state: FSMContext):
    if message.text == "Ввести вопросы":
        await message.answer("Отлично! Нажми на кнопку, когда будешь готов", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Ввести первый вопрос")]], resize_keyboard=True, one_time_keyboard=True))
        await state.set_state(Form.waiting_for_first_question)
    elif message.text == "Ввести первый вопрос":
        await message.answer("Введите первый вопрос:")
        await state.set_state(Form.waiting_for_first_question)
    elif message.text == "Ввести второй вопрос":
        await message.answer("Введите второй вопрос:")
        await state.set_state(Form.waiting_for_second_question)
    else:
        state2 = await state.get_state()
        if state2 == Form.waiting_for_first_question:
            await state.update_data(first_question=message.text)
            await message.answer("Вопрос получен", reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Ввести второй вопрос")]], resize_keyboard=True, one_time_keyboard=True))
        elif state2 == Form.waiting_for_second_question:
            await state.update_data(second_question=message.text)
            data = await state.get_data()
            first_question = data.get('first_question')
            second_question = data.get('second_question')
            await message.answer(f"{predict(prepare_data(first_question, second_question)[0], prepare_data(first_question, second_question)[1])}", reply_markup=start_kb)
            await state.set_state(None)
        else:
            await message.answer("Некорректное действие, пожалуйста, следуйте инструкциям!")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
