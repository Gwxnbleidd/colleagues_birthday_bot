from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
import requests
import re
import datetime

import keyboards as kb
from config import TUNA_URL

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    responce = requests.get(f'{TUNA_URL}/all_users_id1')
    if responce.status_code == 200:
        users = responce.json()
        id = message.from_user.id
        if id in users:
            await message.answer(f'Привет!\nЯ бот отправки уведомлений о дне рождения твоих коллег.\nЧто мне нужно сделать?', reply_markup=kb.menu)
        else:
            await message.answer('Регистрация\nВведите ваше ФИО:')
            
            @router.message(lambda m: not re.search(r'\d{4}-\d{2}-\d{2}', m.text))
            async def get_name(message: Message):
                name = message.text
                await message.answer('Введите вашу дату рождения (гггг-мм-дд):')
                
                @router.message(lambda m: m.text == re.search(r'\d{4}-\d{2}-\d{2}', m.text).group())
                async def get_birthdate(message: Message):
                    # обработать получение даты рождения и запишите ее в переменную
                    birthdate = message.text
                    birthdate = datetime.date.fromisoformat(birthdate)
                    print(f'birthday {birthdate}')
                    user_id = message.from_user.id
                    print(f'name {name}')
                    responce = requests.post(url=f'{TUNA_URL}/add_user_in_db?id={user_id}&name={name}&birhday={birthdate}')
                    if responce.status_code == 200:
                        await message.answer('Регистрация прошла успешно!')
                        await message.answer(f'Привет!\nЯ бот отправки уведомлений о дне рождения твоих коллег.\nЧто мне нужно сделать?', reply_markup=kb.menu)
                    else:
                        message.answer('Ошибка регистрации')
    else:
        await message.answer('Ошибка!')
    
    
@router.message(F.text == 'Вывести список всех коллег')
async def get_list_of_all_employees(message: Message):
    responce = requests.get(f'{TUNA_URL}/all_users')
    if responce.status_code == 200:
        users = responce.json()
        user_list = '\n\n'.join(users)
        await message.answer(f'Список всех коллег:\n\n{user_list}')
    else:
        await message.answer('Ошибка получения списка коллег')

# убрать бы из keybord текущего пользователя
@router.message(F.text == 'Подписаться на коллегу')
async def subscribe_to_employee(message: Message):
    responce = requests.get(f'{TUNA_URL}/all_users_id?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        buttons = kb.form_users_list(users)
        await message.answer(f'Выберите на кого подписаться:', reply_markup= buttons)
    else:
        await message.answer('Ошибка получения списка подписок')

@router.callback_query(lambda c: c.data is not None and re.search('subs_', c.data))
async def process_callback(callback_query: CallbackQuery):
    chosen_user_id = kb.get_id_from_subs_string(callback_query.data)
    await callback_query.answer()
    #Хотел сделать так, но чтобы ни делал, получал ошибку 422
    #responce = requests.post(url=f'{TUNA_URL}/add_subscription', data={'user_id':callback_query.message.from_user.id, 'subs_id':chosen_user_id})
    user_id = callback_query.from_user.id
    responce = requests.post(url=f'{TUNA_URL}/add_subscription?user_id={user_id}&subs_id={chosen_user_id}')
    if responce.status_code == 200:
        await callback_query.message.answer('Вы успешно подписались на коллегу!')
    else:
        await callback_query.message.answer('Ошибка!')
    

@router.message(F.text == 'Отписаться от коллеги')
async def unfollow_an_employee(message: Message):
    #Здесь мы обращаемтся к бд и получаем список всех пользователей, на которых пользователь подписан, и выбираем того, от которого нужно отписаться
    responce = requests.get(f'{TUNA_URL}/subscription_list?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        buttons = kb.form_subsctibers_list(users)
        await message.answer(f'Выберите от кого отписаться:', reply_markup= buttons)
    else:
        await message.answer('Ошибка получения списка пользователей')

@router.callback_query(lambda c: c.data is not None and re.search('unfol_', c.data))
async def process_callback(callback_query: CallbackQuery):
    chosen_user_id = kb.get_id_from_unfol_string(callback_query.data)
    await callback_query.answer()
    user_id = callback_query.from_user.id
    responce = requests.post(url=f'{TUNA_URL}/unsubscribe?user_id={user_id}&subs_id={chosen_user_id}')
    if responce.status_code == 200:
        await callback_query.message.answer('Вы успешно отписались от коллеги!')
    else:
        await callback_query.message.answer('Ошибка!')

@router.message(F.text == 'Посмотреть список подписок')
async def get_subscription_list_cmd(message:Message):
    responce = requests.get(f'{TUNA_URL}/subscription_list?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        res = '\n\n'.join([user[1] for user in users])
        await message.answer(f'Список всех твоих подписок:\n\n{res}')
    else:
        await message.answer('Ошибка получения списка подписок')

# @router.message(F.text == 'Проверить дни рождения коллег')
# async def get_birthday(message:Message):
#     responce = requests.get(f'{TUNA_URL}/is_birthday')