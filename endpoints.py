from fastapi import FastAPI
import uvicorn
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import requests
import time
import asyncio

from shemas import User
from models import (get_db, insert_subscription,get_subsctibers,
                    unsubscribe_from_user, get_subsctibers_list,add_user,get_users_no_subs)
from main import bot
from config import TUNA_URL

app = FastAPI()

# Взять список всех пользователей
@app.get("/all_users")
async def get_all_users():
    res = []
    for user in get_db():
        res.append(User(id=user[0], name=user[1], birthday=user[2]).name)
    return res

@app.get('/all_users_id')
async def get_all_users(id: int):
    res = []
    for user in get_users_no_subs(id):
        print(get_users_no_subs(id))  
        res.append([user[0], user[1]])
    return res

@app.get('/all_users_id1')
async def get_all_users():
    res = []
    for user in get_db():
        usr=User(id=user[0], name=user[1], birthday=user[2])
        res.append(usr.id)
    return res

@app.post('/add_user_in_db')
async def add_user_in_db(id: int, name: str, birhday: datetime.date):
    add_user(id,name,birhday)
    return {'message': 'successful'}

# Посписаться на сотрудника
@app.post('/add_subscription')
async def add_subscription(user_id: int, subs_id: int):
    db = []
    for user in get_db():
        db.append(User(id=user[0], name=user[1], birthday=user[2]))

    user = next((user for user in db if user.id == user_id), None)
    subscriber = next((user for user in db if user.id == subs_id), None)

    if user and subscriber and user_id != subs_id:
        insert_subscription(user_id, subs_id)
        return {'message': 'successful'}
    else:
        return {'error'}

# Удалить подписку
@app.post('/unsubscribe')
async def get_unsubscribe(user_id: int, subs_id: int):
    db = []
    for user in get_db():
        db.append(User(id=user[0], name=user[1], birthday=user[2]))
        
    user = next((user for user in db if user.id == user_id), None)
    subscriber = next((user for user in db if user.id == subs_id), None)

    if user and subscriber and user_id != subs_id:
        unsubscribe_from_user(user_id, subs_id)
        return {'message':'successful'}
    else:
        return{'error'}

# Получить список людей, на которых подписан id
@app.get('/subscription_list')  
async def get_subscription_list(id):
    subs_list= get_subsctibers_list(id)
    return subs_list

# Проверка наличия сегодня ДР сотрудников
@app.get('/is_birthday')
async def is_birhday():
    print('Зашел')
    db = []
    for user in get_db():
        db.append(User(id=user[0], name=user[1], birthday=user[2]))

    today = datetime.date.today()
    res = {}
    for user in db:
        if user.birthday.day == today.day and user.birthday.month == today.month:
            subscribers_id = get_subsctibers(user.id)
            print(subscribers_id)
            for subs_id in subscribers_id:
                await bot.send_message(chat_id=subs_id, text=f'У коллеги {user.name} сегодня День Рождения!')


# Фоновая задача, проверяющая is_birhday каждый день
async def start_scheduler():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(is_birhday, 'interval', seconds=1)
    scheduler.start()

if __name__=="__main__":
    uvicorn.run("endpoints:app", host="0.0.0.0", port=8080, reload=True)
    asyncio.run(start_scheduler())


