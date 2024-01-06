import datetime
import functools, jwt
import logging

from flask import (
    Blueprint, g, redirect, render_template, request, url_for, current_app, make_response
)
from . import db
# این برنامه توابع لازم برای احراز هویت و مدیریت نشست را شامل میشود.

bp = Blueprint('auth', __name__, url_prefix='/card/auth')

# این تابع توکن را دریافت کرده و در یک کوکی ذخیره می نماید
@bp.get('/token/<token>')
def token(token):
    # try:
    #     response = pr.post(
    #         current_app.config["AUTH_SERVICE_BASE_URI"] + current_app.config["AUTH_VALIDATION_ENDPOINT"],
    #         json={"token":token}
    #     )
    #     if response.status_code != 200:
    #         return redirect(current_app.config["AUTH_SERVICE_BASE_URI"], code=303)
    # except:
    #     return redirect(current_app.config["AUTH_SERVICE_BASE_URI"], code=303)

    resp = make_response(redirect(url_for('templates.index')))
    resp.set_cookie("token", token ,secure=True, httponly=True)
    return resp

# در صورت انتخاب دکمه خروج این تابع اجرا میشود
@bp.route('/logout')
def logout():
    resp = make_response(redirect(current_app.config["AUTH_SERVICE_BASE_URI"], code=303))
    resp.set_cookie("token", expires=0)
    return resp

# تابع نمایش فرم لاگین و اعتبار سنجی اطلاعات کاربری
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username']=='admin' and request.form['password']=='admin':
            exp_time = datetime.datetime.now()+datetime.timedelta(0,300)
            encoded_jwt = jwt.encode({"FirstName": "admin",
                "LastName": "admin",
                "NationalCode":"0123456789",
                "UserName": "admin",
                "exp": exp_time},
                current_app.config["SECRET_KEY"] , algorithm='HS256')
            tk='/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJOYXRpb25hbENvZGUiOiIxMjM0NTY3ODkwIiwiRmlyc3ROYW1lIjoiYWRtaW4iLCJMYXN0TmFtZSI6ImFkbWluIn0.1G1k0oX5-eZe8HHMgjCMIMzNnfbA4PGRcfAcsO_NGIs'
            resp = make_response(redirect(url_for('auth.token',token=encoded_jwt)))
        else :
            resp = render_template('auth/login.html',mess='نام کاربری یا کلمه عبور صحیح نیست!')
    else :
        resp = render_template('auth/login.html')
    #resp = make_response(redirect(current_app.config["AUTH_SERVICE_BASE_URI"], code=303))
    return resp

# این تابع برای بخشهای نیازمند احراز هویت اجرا میشود تا توکن کاربر مورد بررسی قرار گیرد.
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        token = request.cookies.get('token')
        try:
            logging.info("login_req started ....")
            if token is None:
                raise Exception()

            # جهت توسعه آتی: بررسی توکن توسط یک سرویس بیرونی
            # response = pr.post(
            #     current_app.config["AUTH_SERVICE_BASE_URI"] + current_app.config["AUTH_VALIDATION_ENDPOINT"],
            #     json={"token":token}
            # )
            # if response.status_code != 200:
            #     raise Exception()

            # اعتبار سنجی توکن
            g.user = jwt.decode(token, current_app.config["SECRET_KEY"] ,algorithms=['HS256'])
            
            # این بخش اطلاعات کاربر را از لیست کاربران مجاز واکشی می نماید
            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute(db.query_string('SELECT id FROM [allowed_users] WHERE deleted_at is null and national_code = %s'), (g.user['NationalCode'],))
            t = cursor.fetchone()
            cursor.close()

            # اگر کاربر در لیست کاربران مجاز نباشد نام خانوادگی به عبارت غیر مجاز تغییر می یابد و در بالای برنامه نمایش داده میشود
            # هنگام تهیه نسخه عملیاتی باید این قسمت اصلاح شود.
            if t is None:
                #     return redirect(url_for('auth.invalid'))
                g.user['LastName']='غیر مجاز'
        except Exception as e:
            # اگر در بررسی اعتبار توکن خطایی رخ دهد به صفحه لاگین ارجاع میشود.
            print(e)
            return redirect(current_app.config["AUTH_SERVICE_BASE_URI"], code=303)

        return view(**kwargs)

    return wrapped_view

@bp.get('/invalid')
def invalid():
    return render_template('auth/invalid.html')