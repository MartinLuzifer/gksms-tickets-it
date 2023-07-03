# IMPORT VARIABLES #####################################################################################################
from config.tgb_token import TELEGRAM_BOT_TOKEN
from config.mongodb import mdb_USERNAME, mdb_PASSWORD
from keyboards import KB_LOGIN, KB_EXIT
from person import get_username_list
from message_texts import *
# AIOGRAM ##############################################################################################################
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.mongo import MongoStorage
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
#############################################
from aiogram.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton
########################################################################################################################
import logging
import requests
from asyncio import sleep


########################################################################################################################
########################################################################################################################


class ProfileStateGroup(StatesGroup):
    phone = State()
    ticket_set_f_name = State()
    ticket_set_l_name = State()
    ticket_set_problem = State()


username_list, f_name_list, l_name_list = get_username_list()

storage = MongoStorage(
    host='172.16.11.136',  # "127.0.0.1",
    port=27017,
    db_name='aiogram_fsm',
    username=mdb_USERNAME,
    password=mdb_PASSWORD,
)

logging.basicConfig(level=logging.DEBUG)
bot = Bot(token=TELEGRAM_BOT_TOKEN)
dp = Dispatcher(bot, storage=storage)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message) -> None:
    """ Стандартная обработка начала сеанса с ботом """
    await message.answer(text=START_TEXT, reply_markup=KB_LOGIN)


@dp.message_handler(content_types=['contact'])
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ После указания номера телефона юзверь отправляется в FSM 'phone' """
    await ProfileStateGroup.phone.set()
    async with state.proxy() as data:
        data['phone_number'] = message.contact.phone_number

    await message.answer(text=f'ваш номер: {data["phone_number"]}\nПишите проблемы ниже', reply_markup=KB_EXIT)


@dp.message_handler(commands=['start'], state=ProfileStateGroup.phone)
async def get_phone_number(message: types.Message, state: FSMContext) -> None:
    """ Если хочется сбросить state на 0 во время уже установленного состояния """
    await state.finish()
    await message.reply("Выполняется сброс состояния")
    await sleep(1)  # можно удалить
    await message.answer("Выполнено! \nВведите /start еще раз, чтобы начать заново")


@dp.message_handler(Text(equals=KB_EXIT.keyboard[0][0].text), state=ProfileStateGroup.phone)
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

        title = 'tb_ticket'
        if '+' in data['phone_number']:
            phone_number = data['phone_number'].split(sep="+")[1]
        else:
            phone_number = data['phone_number']
        ticket = message.text

        r = requests.get(
            f"http://172.16.11.143:3000/reqtg_by_phone?"
            f"phone={phone_number}&"
            f"title={title}&"
            f"description={ticket}"
        )

    await message.reply(text=r.json())


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
    await sleep(1)

    uri = (
        f"http://172.16.11.143:3000/reqtg?"
        f"surname={data['surname']}&"
        f"name={data['name']}&"
        f"title=from_telegram_bot&"
        f"description={data['problem']}"
    )

    await message.answer("Попытка отправить запрос на сервер")
    await sleep(1)

    r = requests.get(uri)
    if r.status_code == 200 and r.text == '{"Hello":"world"}':
        await message.answer(f'Заявка отправлена\n'
                             f'<code>'
                             f'requests.get({uri})\n'
                             f'{r.text}'
                             f'</code>',
                             parse_mode='HTML')

    print(uri)
    # await state.finish()


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
