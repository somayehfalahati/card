from flask import Blueprint,render_template, redirect, url_for, request
from . import db
import datetime
from .auth import login_required
# این برنامه امکان تعریف کاربر نمایش کاربران و امکان حذف کاربر را فراهم می نماید

bp = Blueprint('users', __name__, url_prefix='/card/users')

roles = {
    "admin": "ادمین",
    "user": "کارشناس",
}

@bp.get('/')
@login_required
def index():
    conn, cursor = db.get_conn_cursor()
    cursor.execute(db.query_string("""
        SELECT
            [id],
            [national_code],
            [first_name],
            [last_name],
            [role]
        FROM [allowed_users]
        WHERE
            [deleted_at] is NULL
    """))
    allowed_users = cursor.fetchall()
    cursor.close()

    for i in range(len(allowed_users)):
        allowed_users[i]['role'] = roles[allowed_users[i]['role']]

    return render_template('users/index.html', allowed_users=allowed_users)


@bp.get('/<int:tid>/delete')
@login_required
def delete(tid):
    if tid is None:
        return 'Please specify a template'

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn, cursor = db.get_conn_cursor()
    cursor.execute(db.query_string('UPDATE [allowed_users] SET [deleted_at] = %s WHERE id = %d AND [deleted_at] is NULL'), (current_time, tid))
    conn.commit()
    cursor.close()
    
    return redirect(url_for('users.index'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn, cursor = db.get_conn_cursor()
        cursor.execute(
            db.query_string('INSERT INTO [allowed_users] ([national_code], [first_name], [last_name], [role], [created_at], [updated_at]) values (%s,%s,%s,%s,%s,%s)'),
            (request.form['national_code'], request.form['first_name'], request.form['last_name'], request.form['role'], current_time, current_time)
        )
        conn.commit()
        cursor.close()
        return redirect(url_for('users.index'))
    
    r = [{"id":i[0], "name":i[1]} for i in roles.items()]

    return render_template('users/create.html', roles=r)


@bp.route('/<int:tid>/update', methods=['GET', 'POST'])
@login_required
def update(tid):
    if request.method == 'POST':
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        print(request.form.keys())

        conn, cursor = db.get_conn_cursor()
        cursor.execute(
            db.query_string('UPDATE [allowed_users] SET [role] = %s, [updated_at] = %s WHERE national_code = %s AND [deleted_at] is NULL'),
            (request.form['role'], current_time, tid)
        )
        conn.commit()
        cursor.close()
        return redirect(url_for('users.index'))
    
    conn, cursor = db.get_conn_cursor()
    cursor.execute(db.query_string('SELECT * FROM [allowed_users] WHERE id = %d'), (tid,))
    t = cursor.fetchone()
    cursor.close()
    
    r = [{"id":i[0], "name":i[1]} for i in roles.items()]

    return render_template('users/update.html', t=t, roles=r)
