import psycopg2
import datetime

from config import host, user, password, db_name

def get_db():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(""" SELECT * FROM users; """)
            db = cursor.fetchall()
            
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()
    return db

def add_user(id: int, name: str, birthday: datetime.date):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f""" INSERT INTO users (id, name, birthday)
                       VALUES ({id}, '{name}', '{birthday}'); """)
        
        connection.commit()
        
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()

def insert_subscription(id: int, subs_id: int):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT subscription_id FROM subscriptions WHERE user_id = {id}""")
            if subs_id not in [int(id[0]) for id in cursor.fetchall()]:
                cursor.execute(f""" INSERT INTO subscriptions 
                           VALUES ({id}, {subs_id}); """)
        
        connection.commit()
        
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()

def get_subsctibers(id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT user_id FROM subscriptions WHERE subscription_id = {id}""")
            return set([int(id[0]) for id in cursor.fetchall()])
        
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()

def unsubscribe_from_user(id: int, subs_id: int):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f"""DELETE FROM subscriptions
                            WHERE user_id = {id} AND subscription_id = {subs_id};""")
        
        connection.commit()

    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()

def get_subsctibers_list(id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f"""SELECT s.subscription_id, u.name 
                           FROM subscriptions AS s
                           JOIN users AS u ON s.subscription_id = u.id
                           WHERE s.user_id = {id}""")
            return cursor.fetchall()
        
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()

def get_users_no_subs(id):
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        if connection is None:
            print ('Connection error')

        with connection.cursor() as cursor:
            cursor.execute(f""" SELECT u.id, u.name
                                FROM users u
                                LEFT JOIN subscriptions s ON u.id = s.subscription_id
                                WHERE s.subscription_id IS null and u.id != {id};
                            """)
            db = cursor.fetchall()
            
    except Exception as ex:
        print(f'{ex} Error while working with PostgreSQL')
    finally:
        if connection:
            connection.close()
    return db