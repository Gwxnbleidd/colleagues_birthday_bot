from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import requests
import re
import datetime

import keyboards as kb
from config import TUNA_URL
from db.orm import get_user_from_db

router = Router()

class RegistrationForm(StatesGroup):
    name = State()
    password = State()
    birthday = State()

class AuthorizationForm(StatesGroup):
    password = State()
        
class ChangeNameForm(StatesGroup):
    new_name = State()

class ChangeBirthdayForm(StatesGroup):
    new_birthday = State()

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    if get_user_from_db(message.from_user.id) == None:
        await state.set_state(RegistrationForm.name)
        text = """Привет!
Я бот отправки уведомлений о дне рождения твоих коллег.
Просто подпишись на коллегу, и ты первым узнаешь о его дне рождения! 
                  \nДавай зарегистрируемся.\nВведи свое ФИО."""
        await message.answer(text)
    else:
        await state.set_state(AuthorizationForm.password)
        await message.answer("""Привет!
Я бот отправки уведомлений о дне рождения твоих коллег.
Просто подпишись на коллегу, и ты первым узнаешь о его дне рождения!
                             \nДавай авторизуемся.\nВведи свой пароль.""")    

@router.message(RegistrationForm.name)
async def get_name_registration(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegistrationForm.password)
    await message.answer(f'Приятно познакомится {message.text}!\nТеперь введи свой пароль.')
    

@router.message(RegistrationForm.password)
async def get_password_registration(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    await state.set_state(RegistrationForm.birthday)
    await message.answer('Отлично!\nТеперь введи свою дату рождения в формате ГГГГ-ММ-ЧЧ. \nНапример, 2003-11-14')

@router.message(RegistrationForm.birthday)
async def get_password_registration(message: Message, state: FSMContext):
    await state.update_data(birthday=message.text)
    user = await state.get_data()
    try:
        name = user['name']
        birthday = user['birthday']
        birthday = datetime.date.fromisoformat(user['birthday'])
        password = user['password']
        user_id = message.from_user.id
        responce = requests.post(url=f"{TUNA_URL}/add_user_in_db?id={user_id}&name={name}&birthday={birthday}&password={password}")
        if responce.status_code == 200:
            await message.answer('Регистрация прошла успешно!\nЧто мне нужно сделать?',reply_markup=kb.menu)
            await state.clear()
        else:
            await message.answer('Ошибка регистрации!\nВведите команду /start .')
            await state.clear()
    except:
        await message.answer('Вы ввели неправильную дату!\nПопробуйте еще раз в формате ГГГГ-ММ-ДД.\nНапример, 2003-11-14')
    

@router.message(AuthorizationForm.password)
async def get_password_registration(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    user_password = await state.get_data()
    password = user_password['password']
    user_id = message.from_user.id
    responce = requests.post(url=f"{TUNA_URL}/login?user_id={user_id}&user_password={password}")
    if responce.status_code == 200:
        await message.answer('Авторизация прошла успешно!\nЧто мне нужно сделать?',reply_markup=kb.menu)
        await state.clear()
    elif responce.status_code == 401:
        await message.answer('Неверный пароль!\nПопробуй еще раз .\nЕсли вы забыли пароль, обратитесь к администратору.')
    else:
        await message.answer('Ошибка авторизации!\nВведите команду /start .')
        await state.clear()
    
@router.message(F.text == 'Вывести список всех коллег')
async def get_list_of_all_employees(message: Message):
    responce = requests.get(f'{TUNA_URL}/all_users')
    if responce.status_code == 200:
        users = responce.json()
        user_list = '\n\n'.join(users)
        await message.answer(f'Список всех коллег:\n\n{user_list}', reply_markup=kb.menu)
    else:
        await message.answer('Ошибка получения списка коллег')

@router.message(F.text == 'Подписаться на коллегу')
async def subscribe_to_employee(message: Message):
    responce = requests.get(f'{TUNA_URL}/users_no_subs?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        if not users:
            return await message.answer('Вы подписались на всех коллег!')
        buttons = kb.form_users_list(users)
        await message.answer(f'Выберите на кого подписаться:', reply_markup= buttons)
    else:
        await message.answer('Ошибка получения списка подписок')

@router.callback_query(lambda c: c.data is not None and re.search('subs_', c.data))
async def process_callback(callback_query: CallbackQuery):
    chosen_user_id = kb.get_id_from_subs_string(callback_query.data)
    await callback_query.answer()
    user_id = callback_query.from_user.id
    responce = requests.post(url=f'{TUNA_URL}/add_subscription?user_id={user_id}&subs_id={chosen_user_id}')
    if responce.status_code == 200:
        await callback_query.message.answer('Вы успешно подписались на коллегу!', reply_markup=kb.menu)
    elif responce.status_code == 409:
        await callback_query.message.answer('Вы уже подписаны на этого коллегу', reply_markup=kb.menu)
    else:
        await callback_query.message.answer('Ошибка!', reply_markup=kb.menu)
    

@router.message(F.text == 'Отписаться от коллеги')
async def unfollow_an_employee(message: Message):
    responce = requests.get(f'{TUNA_URL}/subscription_list?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        if not users:
            return await message.answer(f'Список твоих подписок пуст.')
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
        await callback_query.message.answer('Вы успешно отписались от коллеги!', reply_markup=kb.menu)
    elif responce.status_code == 409:
        await callback_query.message.answer('Вы и так не подписаны на этого коллегу', reply_markup=kb.menu)    
    else:
        await callback_query.message.answer('Ошибка!', reply_markup=kb.menu)

@router.message(F.text == 'Посмотреть список подписок')
async def get_subscription_list_cmd(message:Message):
    responce = requests.get(f'{TUNA_URL}/subscription_list?id={message.from_user.id}')
    if responce.status_code == 200:
        users = responce.json()
        if not users:
            return await message.answer(f'Список твоих подписок пуст.')    
        res = '\n\n'.join([user[1] for user in users])
        await message.answer(f'Список всех твоих подписок:\n\n{res}')
    else:
        await message.answer('Ошибка получения списка подписок')

@router.message(F.text == 'Настройки')
async def get_settings(message:Message):
    await message.answer(f'Выберите действие', reply_markup=kb.settings)

@router.message(F.text == 'Вернуться в меню')
async def get_settings(message:Message):
    await message.answer(f'Возвращаемся в меню\nЧто мне нужно сделать?', reply_markup=kb.menu)

@router.message(F.text == 'Изменить имя')
async def update_name(message:Message, state: FSMContext):
    await state.set_state(ChangeNameForm.new_name)
    await message.answer(f'Введи свое ФИО')

@router.message(ChangeNameForm.new_name)
async def get_new_name(message: Message, state: FSMContext):
    await state.update_data(new_name=message.text)
    new_name = await state.get_data()
    name = new_name['new_name']
    user_id = message.from_user.id
    responce = requests.put(f'{TUNA_URL}/set_new_name?user_id={message.from_user.id}&new_name={name}')
    if responce.status_code == 200:
        await message.answer('Новое имя установлено!\nЧто мне нужно сделать?',reply_markup=kb.settings)
        await state.clear()
    else:
        await message.answer('Ошибка!\nВозвращаюсь в меню настроек.',reply_markup=kb.settings)
        await state.clear()


@router.message(F.text == 'Изменить дату рождения')
async def update_birthday(message:Message, state: FSMContext):
    await state.set_state(ChangeBirthdayForm.new_birthday)
    await message.answer(f'Введи свою дату рождения в формате ГГГГ-ММ-ДД\nНапример, 2003-11-14')

@router.message(ChangeBirthdayForm.new_birthday)
async def get_new_birthday(message: Message, state: FSMContext):
    await state.update_data(new_birthday=message.text)
    new_birthday = await state.get_data()
    try:
        birthday = datetime.date.fromisoformat(new_birthday['new_birthday'])
        user_id = message.from_user.id
        responce = requests.put(f'{TUNA_URL}/set_new_birthday?user_id={message.from_user.id}&new_birthday={birthday}')
        if responce.status_code == 200:
            await message.answer('Новая дата рождения установлена!\nЧто мне нужно сделать?',reply_markup=kb.settings)
            await state.clear()
        else:
            await message.answer('Ошибка!\nВозвращаюсь в меню настроек.',reply_markup=kb.settings)
            await state.clear()
    except:
        await message.answer('Вы ввели неправильную дату!\nПопробуйте еще раз в формате ГГГГ-ММ-ДД.\nНапример, 2003-11-14')

@router.message(F.text == 'Получить информацию о себе')
async def update_birthday(message:Message):
    user = get_user_from_db(message.from_user.id)
    await message.answer(f"""Конечно! Вот информация о тебе:
Твое имя {user.name}
Твоя дата рождения {user.birthday}
Что я могу сделать?""")
                         
    
@router.message()
async def incorrect_message(message: Message):
    await message.answer('К сожалению, я тебя не понимаю(\nВоспользуйся подказками на клавиатуре.')
