# IMPORT VARIABLES #####################################################################################################
from config.tgb_token import *
from config.mongodb import *
from message_texts import *
from keyboards import *
# IMPORT RESPONSES #####################################################################################################
from responses.tickets import get_active_tickets
# AIOGRAM ##############################################################################################################
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
########################################################################################################################
import logging
import requests
import datetime
import json
import os
import random
import hashlib
########################################################################################################################
########################################################################################################################


class ProfileStateGroup(StatesGroup):
    phone = State()
    ticket_set_f_name = State()
    ticket_set_l_name = State()
    ticket_set_problem = State()


logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(
    bot=bot,
    storage=MongoStorage(
        host=mdb_HOST, port=mdb_PORT,
        username=mdb_USERNAME, password=mdb_PASSWORD,
        db_name=mdb_DBNAME
    )
)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    """ 1 - Стандартная обработка начала сеанса с ботом """
    await message.answer(text=START_TEXT, reply_markup=KB_LOGIN)


@dp.message_handler(content_types=['contact'])
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ 2 - Работа с ботом начинается после передачи номера телефона.
    После указания номера телефона пользователь отправляется в FSM 'phone' """
    await ProfileStateGroup.phone.set()
    async with state.proxy() as data:
        phone_number = data['phone_number'] = message.contact.phone_number
        first_name = data['first_name'] = message.contact.first_name  # в бд заносится имя и фамилия из телеги
        last_name = data['last_name'] = message.contact.last_name     # если фи отличается от itop, то ничего страшного
    await message.answer(
        text=f"Ваш номер: {phone_number}\n" 
             f"Ваше имя в мессенджере: {first_name}\n" 
             f"Ваша Фамилия в мессенджере: {last_name}\n" 
             f"\nПишите проблемы ниже",
        reply_markup=KB_EXIT
    )


@dp.message_handler(commands=['help'], state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message) -> None:
    """ 2.1 - Вывод справки """
    await message.reply(text=HELP_MESSAGE)


@dp.message_handler(commands=['start'], state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ 2.2 - Если хочется сбросить state на 0 во время уже установленного состояния """
    try:
        await state.finish()
    except:  # скорее всего никогда не отработает
        await message.answer("Не удалось выполнить сброс состояния")
    else:
        await message.answer("Выполненен сброс контекста! \nВведите /start еще раз, чтобы начать заново")


@dp.message_handler(Text(equals=BT_MY_TICKETS.text), state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ Передать список активных заявок пользователю """

    async with state.proxy() as data:
        first_name = data.get('first_name')
        last_name = data.get('last_name')

    tickets = get_active_tickets(first_name, last_name)

    for ticket in tickets:
        await message.answer(ticket)


@dp.message_handler(Text(equals=BT_EXIT.text), state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ Если пользователю хочется идентифицироваться заново, например: он сменил номер телефона """
    await state.finish()
    await message.answer(text='Вы вернулись в начало', reply_markup=KB_LOGIN)


@dp.message_handler(state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """
    Основной код для обработки тикетов на ITOP
    ITOP автоматически подставит имя и фамилию пользователя в тикет
    """

    async with state.proxy() as data:
        phone_number = f"{data['phone_number']}"  # номер телефона из бд, который был записан во время авторизации
    if '+' in phone_number:
        phone_number = phone_number.split(sep='+')[1]

    ticket = message.text
    title = 'tb_ticket'

    try:  # Создать каталог для ответов, если его нет
        os.mkdir("answers")
    except FileExistsError:
        pass  # Если каталог уже существует, то ничего не делать

    # Generate name for .json-file
    dt = f"{datetime.datetime.now()}".replace(' ', '')
    hs = hashlib.sha256()
    hs.update(f"{dt}+{random.randint(0, 999)}".encode())
    random_symbols = hs.hexdigest()
    json_file_name = f"answers/answer-{dt}-№-{random_symbols}.json"

    with open(json_file_name, 'w') as file:
        r = requests.get(
            f"http://172.16.11.143:3000/reqtg_by_phone?"
            f"phone={phone_number}&"
            f"title={title}&"
            f"description={ticket}"
        )
        file.write(r.json())

    with open(json_file_name, 'r') as file:
        json_file = json.load(file)
        name = json_file.get('name')
        surname = json_file.get('surname')
        answer = json_file.get('answer')

    async with state.proxy() as data:
        """ 
        ЭТО ЧАСТЬ КОСТЫЛЯ: 
        Обновляет запись в субд, изменяя ФИ из телеграма на ФИ из ITOP, для получения списка тикетов в будущем
        Потому что не у всех в телеге указаны настоящие имя и фамилия
        """
        data['first_name'] = name
        data['last_name'] = surname

    await message.reply(text=f"Имя: {name} \nФамилия: {surname} \nОтвет: {answer}", reply_markup=KB_NAVIGATION)


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
