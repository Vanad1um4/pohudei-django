from django.db import connection


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]


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
