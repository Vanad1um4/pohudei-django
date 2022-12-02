from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


def db_get_everyday_sum_kcals_from_diary(tg_id):
    with connection.cursor() as c:
        c.execute(f'''
            select d.date, sum(round(d.food_weight / 100.0 * c.kcals)) as eaten, w.weight
            from diary d join catalogue c on d.catalogue_id=c.id join weights w on d.users_id=w.users_id join users u on d.users_id=u.id
            where u.tg_user_id={tg_id} and d.date=w.date
            group by d.date, w.weight
            order by d.date;
        ''')
        # res = dictfetchall(c)
        res = c.fetchall()
    return res


def db_get_today_food_from_diary(tg_id):
    with connection.cursor() as c:
        c.execute(f'''
            select c.name, d.food_weight, c.kcals, cast(round(d.food_weight / 100.0 * c.kcals) as integer) as eaten
            from diary d join users u on d.users_id=u.id join catalogue c on d.catalogue_id=c.id
            where d.date=current_date and u.tg_user_id={tg_id}
            order by d.id;''')
        res = c.fetchall()
    return res


def db_get_last_weights(tg_id):
    with connection.cursor() as c:
        c.execute(f'''
            select w.date, w.weight from weights w
            join users u on w.users_id=u.id
            where u.tg_user_id={tg_id} and w.date>=current_date-4 and w.date<=current_date
            order by w.id''')
        res = dictfetchall(c)
        # res = c.fetchall()
    return res

# def test():
#     with connection.cursor() as c:
#         c.execute('SELECT * FROM users;')
#         res = dictfetchall(c)
#         # res = c.fetchall()
#     return res
