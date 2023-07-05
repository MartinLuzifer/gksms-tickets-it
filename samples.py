import logging

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton

from config.mongodb import mdb_HOST, mdb_PORT, mdb_USERNAME, mdb_PASSWORD, mdb_DBNAME
from config.tgb_token import TELEGRAM_BOT_TOKEN
from responses.person import get_username_list

username_list, f_name_list, l_name_list = get_username_list()
logging.basicConfig(level=logging.ERROR)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(
    bot=bot,
    storage=MongoStorage(
        host=mdb_HOST,
        port=mdb_PORT,
        username=mdb_USERNAME,
        password=mdb_PASSWORD,
        db_name=mdb_DBNAME,
    )
)


class ProfileStateGroup(StatesGroup):
    ticket_set_f_name = State()
    ticket_set_l_name = State()
    ticket_set_problem = State()


@dp.message_handler(Text(equals='Войти в систему'))
async def get_ticket(message: types.Message) -> None:
    """
    Альтернативный способ идентификации в системе
    ПОСЛЕ НАЖАТИЯ НА КНОПКУ "Войти в систему" БОТ ЗАПРОСИТ ИМЯ И СПРЯЧЕТ КНОПКИ
    """
    await ProfileStateGroup.ticket_set_f_name.set()
    await message.answer(text='Ваше Имя:', reply_markup=ReplyKeyboardRemove())


@dp.message_handler(Text(equals=f_name_list), state=ProfileStateGroup.ticket_set_f_name)
async def get_f_name(message: types.Message, state: FSMContext) -> None:
    """ ПОЛЬЗОВАТЕЛЬ УКАЖЕТ ИМЯ, ЕСЛИ ОНО СОВПАДАЕТ СО СПИСКОМ ИМЕН, ТО ИДЕТ ДАЛЬШЕ """
    async with state.proxy() as data:
        data['name'] = message.text

    await ProfileStateGroup.ticket_set_l_name.set()
    await message.answer(text='Ваша Фамилия:')


@dp.message_handler(Text(equals=l_name_list), state=ProfileStateGroup.ticket_set_l_name)
async def get_l_name(message: types.Message, state: FSMContext) -> None:
    """ ПОЛЬЗОВАТЕЛЬ ПИШЕТ ФАМИЛИЮ, ЕСЛИ ОНО СОВПАДАЕТ СО СПИСКОМ ФАМИЛИЙ, ТО ИДЕТ ДАЛЬШЕ """
    async with state.proxy() as data:
        data['surname'] = message.text

    await ProfileStateGroup.ticket_set_problem.set()
    await message.answer(
        text='Опишите проблему:',
        reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(text="Вернуться к началу")))


@dp.message_handler(commands=['start'], state=ProfileStateGroup.ticket_set_problem)
@dp.message_handler(lambda message: message.text == "Вернуться к началу", state=ProfileStateGroup.ticket_set_problem)
async def get_problem(message: types.Message, state: FSMContext) -> None:
    """ Если пользователь хочешь вернуться обратно """
    await state.finish()
    await message.answer(
        text="Вы вернулись в начало",
        reply_markup=ReplyKeyboardMarkup(
            resize_keyboard=True,
            one_time_keyboard=True)
        .add(KeyboardButton(text="Оставить Тикет"))
    )


@dp.message_handler(state=ProfileStateGroup.ticket_set_problem)
async def get_problem(message: types.Message, state: FSMContext) -> None:
    """ ПОЛЬЗОВАТЕЛЬ ПИШЕТ ПРОБЛЕМУ, ОСУЩЕСТВЛЯЕТСЯ СБОР ИНФОРМАЦИИ И ОТПРАВКА НА ITOP """
    async with state.proxy() as data:
        data['problem'] = message.text

    await message.answer(text=f'выполняется попытка отправки тикета')

    uri = (
        f"http://172.16.11.143:3000/reqtg?"
        f"surname={data['surname']}&"
        f"name={data['name']}&"
        f"title=from_telegram_bot&"
        f"description={data['problem']}"
    )

    await message.answer("Попытка отправить запрос на сервер")

    r = requests.get(uri)
    if r.status_code == 200 and r.text == '{"Hello":"world"}':
        await message.answer(f'Заявка отправлена\n'
                             f'<code>'
                             f'requests.get({uri})\n'
                             f'{r.text}'
                             f'</code>',
                             parse_mode='HTML')


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)