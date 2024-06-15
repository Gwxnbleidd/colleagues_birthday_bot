import asyncio
import os
import signal
import sys
sys.path.append(f'{os.getcwd()}')
sys.path.append(f'{os.getcwd()}/db')
sys.path.append(f'{os.getcwd()}/bot')
sys.path.append(f'{os.getcwd()}/fastapi_app')

import subprocess

if __name__=='__main__':

    pid_fastapi_proc = subprocess.Popen(args=['python3', 'fastapi_app/endpoints.py']).pid
    pid_bot_proc = subprocess.Popen(args=['python3', 'bot/main.py']).pid

    
    # Запустить эти процессы из одного файла иначе не получилось.
    # Чтобы остановить программу, нужно завершить эти процессы вручную
    q = input('Введите "q" для остановки бота')
    if q=='Q' or q=='q':
        os.kill(pid_bot_proc, signal.SIGTERM)
        os.kill(pid_fastapi_proc, signal.SIGTERM)

