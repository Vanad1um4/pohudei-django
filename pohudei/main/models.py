from django.db import connection
from datetime import date, datetime
from .log import *

logger = get_logger()  # pyright: ignore


def dict_fetchall(cursor):
    """Returns all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


##### WEIGHT FUNCTIONS ########################################################

def db_get_one_weight(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection.cursor() as c:
            c.execute(f'''
                select id, date, weight
                from weights
                where users_id={user_id} and date='{date_iso}';''')
            # where users_id={user_id} and date=('{date_iso}')::date;''')
            res = c.fetchall()
            if res:
                return ('success', res)
            else:
                return ('no_data', [])

    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_get_last_weights(user_id, weights_to_pull):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id, date, weight
                from weights
                where users_id={user_id} and date>current_date-{weights_to_pull} and date<=current_date
                order by date''')
            res = c.fetchall()
        return ('success', res)
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_update_weight_from_diary(user_id, date, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id
                from weights
                where users_id={user_id} and date='{date}';''')
            id = c.fetchall()
            # print(id[0][0])
            if id:
                c.execute(f'''
                    update weights
                    set weight={weight}
                    where id={id[0][0]} and users_id={user_id}; ''')
            elif not id:
                c.execute(f'''
                    insert into weights (users_id, date, weight)
                    values ({user_id}, '{date}', {weight}); ''')

            return ('success', [])

    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_add_new_weight(user_id, date, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id
                from weights
                where users_id={user_id} and date='{date}';''')
            id = c.fetchall()
            # print(id[0][0])
            if not id:
                c.execute(f'''
                    insert into weights (users_id, date, weight)
                    values ({user_id}, '{date}', {weight});''')
                return ('success', [])
            else:
                return ('duplication', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_update_weight(user_id, weight_id, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                update weights
                set weight={weight}
                where id={weight_id} and users_id={user_id}; ''')
            return ('success', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_delete_weight(user_id, weight_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                delete from weights
                where id={weight_id} and users_id={user_id}; ''')
            return ('success', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


##### DIARY FUNCTIONS #########################################################

# # LEGACY
# def db_get_today_food_from_diary(user_id):
#     try:
#         with connection.cursor() as c:
#             # select c.name, d.food_weight, c.kcals, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten
#             # where d.date='2022-12-06' and d.users_id={user_id}
#             c.execute(f'''
#                 select d.id, c.name, d.food_weight, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten_kcals
#                 from diary d join catalogue c on d.catalogue_id=c.id
#                 where d.date=current_date and d.users_id={user_id}
#                 order by d.id;''')
#             res = c.fetchall()
#         return res
#     except Exception as exc:
#         logger.exception(exc)
#         return []
#

# NEW
def db_get_food_from_diary(user_id, date_iso):
    try:
        if date_iso == None:
            today = datetime.today()
            date_iso = today.strftime('%Y-%m-%d')
        with connection.cursor() as c:
            # select c.name, d.food_weight, c.kcals, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten
            # where d.date='2022-12-06' and d.users_id={user_id}
            c.execute(f'''
                select d.id, c.name, d.food_weight, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten_kcals
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.date=('{date_iso}')::date and d.users_id={user_id}
                order by d.id;''')
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


def db_add_new_diary_entry(user_id, date, food_id, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                insert into diary (users_id, date, catalogue_id, food_weight)
                values ({user_id}, '{date}', {food_id}, {weight});''')
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


def db_update_diary_entry(user_id, diary_id, new_food_weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                update diary
                set food_weight='{new_food_weight}'
                where id='{diary_id}' and users_id='{user_id}';''')
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


def db_del_diary_entry(user_id, diary_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                delete from diary
                where id='{diary_id}' and users_id={user_id};''')
            return 'success'
    except Exception as exc:
        logger.exception(exc)
        return 'failure'


##### CATALOGUE FUNCTIONS #####################################################

def db_get_all_food_names(user_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id, name from catalogue
                where users_id=0 or users_id={user_id}
                order by name''')
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


def db_get_users_food_names(user_id, admin=False):
    try:
        with connection.cursor() as c:
            if admin:
                c.execute(f'''
                    select id, name, kcals from catalogue
                    order by name''')
                foods = c.fetchall()
            else:
                c.execute(f'''
                    select id, name, kcals from catalogue
                    where users_id={user_id}
                    order by name''')
                foods = c.fetchall()
        return ('success', foods)
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_add_new_food_to_catalogue(user_id, food_name, food_kcals, admin=False):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id
                from catalogue
                where name='{food_name}';''')
            id = c.fetchall()
            if id:
                return ('duplication', [])
            elif admin:
                c.execute(f'''
                    insert into catalogue (name, kcals, users_id)
                    values ('{food_name}', {food_kcals}, 0);''')
                return ('success', [])
            elif not admin:
                c.execute(f'''
                    insert into catalogue (name, kcals, users_id)
                    values ('{food_name}', {food_kcals}, {user_id});''')
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_update_food_in_catalogue(user_id, food_id, food_name, food_kcals, admin=False):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id
                from catalogue
                where id!='{food_id}' and name='{food_name}';''')
            id = c.fetchall()
            if id:
                return ('duplication', [])
            elif admin:
                c.execute(f'''
                    update catalogue
                    set name='{food_name}', kcals={food_kcals}
                    where id='{food_id}';''')
                return ('success', [])
            elif not admin:
                c.execute(f'''
                    update catalogue
                    set name='{food_name}', kcals={food_kcals}
                    where id='{food_id}' and users_id='{user_id}';''')
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_delete_food_from_catalogue(food_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id from diary
                where catalogue_id='{food_id}';''')
            id = c.fetchall()
            print(id)
            if id:
                return ('in use', [])
            elif not id:
                c.execute(f'''
                    delete from catalogue
                    where id='{food_id}';''')
                return ('success', [])
            else:
                return ('failure', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


##### STATS FUNCTIONS #########################################################


def db_get_users_weights_all(user_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select date, weight
                from weights
                where users_id={user_id}
                order by date''')
            res = c.fetchall()
            # res = c.fetchall()
            # res = dict_fetchall(c)
        return ('success', res)
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_get_everyday_sum_kcals_from_diary(user_id):
    try:
        with connection.cursor() as c:
            # select d.date, sum(round(d.food_weight / 100.0 * c.kcals)) as eaten, w.weight
            # from diary d join catalogue c on d.catalogue_id=c.id join weights w on d.users_id=w.users_id
            # where d.users_id={user_id} and d.date=w.date
            # group by d.date, w.weight
            # order by d.date;

            c.execute(f'''
                select d.date, sum(round(d.food_weight / 100.0 * c.kcals)) as eaten
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.users_id={user_id}
                group by d.date
                order by d.date
            ''')
            # res = dict_fetchall(c)
            res = c.fetchall()
        return res
    except Exception as exc:
        logger.exception(exc)
        return []


##### OPTIONS FUNCTIONS #######################################################


def db_get_options(user_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''select weights_to_pull from profile_profile where user_id={user_id}''')
            # res = c.fetchall()
            res = dict_fetchall(c)
        return ('success', res[0])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


def db_set_weights_to_pull(user_id, weights_to_pull):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                update profile_profile
                set weights_to_pull='{weights_to_pull}'
                where user_id='{user_id}';''')
        return ('success', [])
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [])


##### BACKUP FUNCTIONS ########################################################


def db_backup(date_iso):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select d.id as diary_id, *, round(d.food_weight / 100.0 * c.kcals) as calc_kcals
                from diary d join catalogue c on d.catalogue_id=c.id
                where d.date='{date_iso}'
                order by d.date asc, d.id asc;''')
            # res = c.fetchall()
            food = dict_fetchall(c)
            c.execute(f'''
                select * from weights
                where date='{date_iso}'
                ;''')
            weights = dict_fetchall(c)
        return ('success', (food, weights))
    except Exception as exc:
        logger.exception(exc)
        return ('failure', [{}, {}])
