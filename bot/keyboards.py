from aiogram.types import (KeyboardButton, ReplyKeyboardMarkup, 
                           InlineKeyboardButton, InlineKeyboardMarkup)
import re

menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Вывести список всех коллег')],
                                     [KeyboardButton(text='Подписаться на коллегу'),
                                      KeyboardButton(text='Отписаться от коллеги')],
                                     [KeyboardButton(text='Посмотреть список подписок'),
                                      KeyboardButton(text='Настройки')]], resize_keyboard=True,
                                     input_field_placeholder='Выберите действие')

settings = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Получить информацию о себе')],
                                         [KeyboardButton(text='Изменить имя'),
                                          KeyboardButton(text='Изменить дату рождения')],
                                          [KeyboardButton(text='Вернуться в меню')]], resize_keyboard=True,
                                        input_field_placeholder='Выберите действие')

def form_users_list(list_users):
    db = []
    for i,user in enumerate(list_users):
        db.append([InlineKeyboardButton(text=f'{user[1]}',callback_data=f'subs_{user[0]}')])
    buttons = InlineKeyboardMarkup(inline_keyboard=db)
    return buttons

def form_subsctibers_list(list_users):
    db = []
    for i,user in enumerate(list_users):
        db.append([InlineKeyboardButton(text=f'{user[1]}',callback_data=f'unfol_{user[0]}')])
    buttons = InlineKeyboardMarkup(inline_keyboard=db)
    return buttons


def get_id_from_subs_string(string):
    pattern = r'subs_(\d+)'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return None

def get_id_from_unfol_string(string):
    pattern = r'unfol_(\d+)'
    match = re.search(pattern, string)
    if match:
        return int(match.group(1))
    else:
        return None


