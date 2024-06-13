from fastapi import FastAPI, HTTPException,status
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import asyncio

import os
import sys
sys.path.append(f'{os.getcwd()}')
sys.path.append(f'{os.getcwd()}/db')
sys.path.append(f'{os.getcwd()}/bot')

from shemas import User

from db.orm import (get_db, get_users_no_subs,add_user,get_user_from_db,
                    subscribe,unsubscribe, get_subscription_list, get_subscribers,
                    update_name, update_birthday)

from bot.main import bot,start_bot
from config import TUNA_URL


app = FastAPI()

# Пока без куки
@app.post('/login')
async def login(user_id: int, user_password: str):
    usr = get_user_from_db(user_id)
    if usr != None:
        user = User(id=usr.id, name = usr.name, password=usr.password, birthday=usr.birthday)
        if user.password == user_password:
            return {'message':'authorization was successful'}
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Incorrect password')
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

# Взять список всех пользователей
@app.get("/all_users")
async def get_all_users():
    res = []
    for user in get_db():
        res.append(User(id=user[0], name=user[1], birthday=user[2], password=user[3]).name)
    return res

# Взять список пользоваьелей, на которых id не подписан
@app.get('/users_no_subs')
async def get_users_no_subs_func(id: int):
    res = []
    for user in get_users_no_subs(id):
        res.append([user[0], user[1]])
    return res

# надо защитить его
@app.post('/add_user_in_db')
async def add_user_in_db(id: int, name: str, birthday: datetime.date, password: str):
    add_user(id,name,birthday,password)
    return {'message': 'successful'}

# Посписаться на сотрудника
@app.post('/add_subscription')
async def add_subscription(user_id: int, subs_id: int):
    user = get_user_from_db(user_id)
    subscriber = get_user_from_db(subs_id)
    if user != None and subscriber != None:
        subscription_list = [user[0] for user in get_subscription_list(user_id)]
        if subs_id in subscription_list:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Вы уже подписаны на этого пользователя')
        subscribe(user_id, subs_id)
        return {'message': 'successful'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')


# Удалить подписку
@app.post('/unsubscribe')
async def get_unsubscribe(user_id: int, subs_id: int):
    user = get_user_from_db(user_id)
    subscriber = get_user_from_db(subs_id)
    if user != None and subscriber != None:
        subscription_list = [user[0] for user in get_subscription_list(user_id)]
        if subs_id not in subscription_list:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='Вы не подписаны на этого пользователя')
        unsubscribe(user_id, subs_id)
        return {'message':'successful'}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

# Получить список людей, на которых подписан id
@app.get('/subscription_list')  
async def get_subscription(id: int):
    res = []
    for user in get_subscription_list(id):
        print(f'{user=}')
        res.append((user[0], user[1]))
    return res

@app.put('/set_new_name')
async def set_new_name(user_id: int, new_name: str):
    update_name(user_id, new_name)
    return {'message': 'successful'}

@app.put('/set_new_birthday')
async def set_new_name(user_id: int, new_birthday: datetime.date):
    update_birthday(user_id, new_birthday)
    return {'message': 'successful'}


# Проверка наличия сегодня ДР сотрудников
@app.get('/is_birthday')
async def is_birhday():
    db = []
    for user in get_db():
        db.append(User(id=user[0], name=user[1], birthday=user[2], password=None))
    today = datetime.date.today()
    for user in db:
        if user.birthday.day == today.day and user.birthday.month == today.month:
            subscribers_id = get_subscribers(user.id)
            # Оповестить если нет др сегодня
            for subs_id in subscribers_id:
                await bot.send_message(chat_id=subs_id, text=f'У коллеги {user.name} сегодня День Рождения!')

# Фоновая задача, проверяющая is_birhday каждый день
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(is_birhday, "cron", hour=12, minute = 00,
                      start_date='2000-01-01 00:00:00')
    scheduler.start()

# async def main():
async def start_api():
    asyncio.create_task(start_scheduler())

    config = uvicorn.Config("endpoints:app", host="0.0.0.0", port=8080, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


if __name__ == "__main__":
     asyncio.run(start_api())