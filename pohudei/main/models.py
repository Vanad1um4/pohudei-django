from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


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


def db_get_last_weights(user_id):
    with connection.cursor() as c:
        c.execute(f'''
            select w.date, w.weight from weights w
            where w.users_id={user_id} and w.date>=current_date-4 and w.date<=current_date
            order by w.id''')
        res = dictfetchall(c)
        # res = c.fetchall()
    return res


def db_get_food_names():
    with connection.cursor() as c:
        c.execute('select id, name from catalogue order by name')
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


# def test():
#     with connection.cursor() as c:
#         c.execute('SELECT * FROM users;')
#         res = dictfetchall(c)
#         # res = c.fetchall()
#     return res
