import asyncio
import os
import sys
sys.path.append(f'{os.getcwd()}')
sys.path.append(f'{os.getcwd()}/db')
sys.path.append(f'{os.getcwd()}/bot')
sys.path.append(f'{os.getcwd()}/fastapi_app')

import subprocess
from fastapi_app.endpoints import start_api

if __name__=='__main__':

    subprocess.Popen(args=['python3', 'fastapi_app/endpoints.py'])
    subprocess.Popen(args=['python3', 'bot/main.py'])

