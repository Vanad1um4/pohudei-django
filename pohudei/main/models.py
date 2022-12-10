from django.db import connection


def dictfetchall(cursor):
    """Return all rows from a cursor as a dict"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


##### WEIGHT FUNCTIONS ########################################################

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
        print(exc)
        return ('failure', [])


def db_add_new_weight(user_id, date, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select id
                from weights
                where users_id={user_id} and date=('{date}')::date;''')
            # where users_id={user_id} and date=to_date({date}, 'YYYY-MM-DD');''')
            res = c.fetchall()
            # print(res)
            if not res:
                c.execute(f'''
                    insert into weights (users_id, date, weight)
                    values ({user_id}, '{date}', {weight});''')
                return ('success', [])
            else:
                return ('duplication', [])
    except Exception as exc:
        print(exc)
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
        print(exc)
        return ('failure', [])


def db_delete_weight(user_id, weight_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                delete from weights
                where id={weight_id} and users_id={user_id}; ''')
            return ('success', [])
    except Exception as exc:
        print(exc)
        return ('failure', [])


##### DIARY FUNCTIONS #########################################################

def db_get_everyday_sum_kcals_from_diary(user_id):
    with connection.cursor() as c:
        c.execute(f'''
            select d.date, sum(round(d.food_weight / 100.0 * c.kcals)) as eaten, w.weight
            from diary d join catalogue c on d.catalogue_id=c.id join weights w on d.users_id=w.users_id
            where d.users_id={user_id} and d.date=w.date
            group by d.date, w.weight
            order by d.date;
        ''')
        # res = dictfetchall(c)
        res = c.fetchall()
    return res


def db_get_today_food_from_diary(user_id):
    with connection.cursor() as c:
        # select c.name, d.food_weight, c.kcals, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten
        c.execute(f'''
            select d.id, c.name, d.food_weight, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten_kcals
            from diary d join catalogue c on d.catalogue_id=c.id
            where d.date=current_date and d.users_id={user_id}
            order by d.id;''')
        res = c.fetchall()
    return res


def db_add_new_diary_entry(user_id, date, food_id, weight):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                insert into diary (users_id, date, catalogue_id, food_weight)
                values ({user_id}, '{date}', {food_id}, {weight});''')
            return 'success'
    except Exception as exc:
        print(exc)
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
        print(exc)
        return 'failure'


def db_del_diary_entry(user_id, diary_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                delete from diary
                where id='{diary_id}' and users_id={user_id};''')
            return 'success'
    except Exception as exc:
        print(exc)
        return 'failure'


##### CATALOGUE FUNCTIONS #####################################################

def db_get_food_names():
    with connection.cursor() as c:
        c.execute('select id, name from catalogue order by name')
        res = c.fetchall()
    return res


##### STATS FUNCTIONS #########################################################


def db_get_basic_stats(user_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''
                select date, weight
                from weights
                where users_id={user_id}
                order by date''')
            res = c.fetchall()
            # res = c.fetchall()
            # res = dictfetchall(c)
        return ('success', res)
    except Exception as exc:
        print(exc)
        return ('failure', [])


##### OPTIONS FUNCTIONS #######################################################


def db_get_options(user_id):
    try:
        with connection.cursor() as c:
            c.execute(f'''select weights_to_pull from profile_profile where user_id={user_id}''')
            # res = c.fetchall()
            res = dictfetchall(c)
        return ('success', res[0])
    except Exception as exc:
        print(exc)
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
        print(exc)
        return ('failure', [])
