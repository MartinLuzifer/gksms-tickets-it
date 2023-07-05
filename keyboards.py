from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# KEYBOARD ON STARTUP
KB_LOGIN = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
BT_LOGIN = KeyboardButton(text="Войти с помощью номера телефона", request_contact=True)
KB_LOGIN.add(BT_LOGIN)
#####################

# KEYBOARD FOR EXIT
KB_NAVIGATION = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
KB_EXIT = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

BT_MY_TICKETS = KeyboardButton(text="Мои Заявки")
BT_EXIT = KeyboardButton(text="Повторная авторизация")

KB_EXIT.add(BT_EXIT)
KB_NAVIGATION.add(BT_MY_TICKETS)
KB_NAVIGATION.add(BT_EXIT)

###################

print(KB_LOGIN.keyboard[0][0].text)