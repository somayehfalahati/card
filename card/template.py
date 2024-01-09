import os
from flask import Blueprint, current_app,render_template, redirect, url_for, request
from . import db
import datetime
from .auth import login_required
from werkzeug.utils import secure_filename
# این برنامه امکان تعریف مشاهده و حذف قالبها را فراهم می نماید

bp = Blueprint('templates', __name__, url_prefix='/card/templates')

@bp.get('/')
@login_required
def index():
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('SELECT * FROM [Templates] WHERE [deleted_at] is NULL'))
    templates = cursor.fetchall()

    cursor.close()

    return render_template('templates/index.html', templates=templates)


@bp.get('/<int:tid>')
@login_required
def view(tid):
    if tid is None:
        return 'Please specify a template'
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('SELECT * FROM [Templates] WHERE id = %d AND [deleted_at] is NULL'), (tid,))
    t = cursor.fetchone()
    cursor.close()
    txt=t['definition']
    #txt=txt.replace(b'\n' ,b'"<br/>"')
    #txt=txt.replace(b'\r\r\n' ,b'\r\n')
    nt={}
    nt['id']=t['id']
    nt['definition']=txt
    

    return render_template('templates/view.html', t=t)


@bp.get('/<int:tid>/delete')
@login_required
def delete(tid):
    if tid is None:
        return 'Please specify a template'

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('UPDATE [Templates] SET [deleted_at] = %s WHERE id = %d AND [deleted_at] is NULL'), (current_time, tid))
    conn.commit()
    cursor.close()
    
    return redirect(url_for('templates.index'))


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
        if 'file' not in request.files:
            return 'Please upload the template file', 400

        temFile = request.files['file']
        basePath = "%s/%s" % (current_app.config['BASE_UPLOAD_PATH'], "template"  )
        print("basePath: %s" % basePath)
        if not os.path.exists(basePath):
            os.makedirs(basePath)
        #else:
        #    return 'Please specify an other name', 400
        file="%s/%s" % (basePath , secure_filename(temFile.filename))
        temFile.save(file)
        with open(file, 'r') as f:
            temp_file = f.read()

        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(db.query_string(
            'INSERT INTO [Templates] ([name], [definition], [created_at], [updated_at]) values (%s,%s,%s,%s)'),
            (request.form['name'], temp_file, current_time, current_time)
        )
        conn.commit()
        cursor.close()
        return redirect(url_for('templates.index'))

    return render_template('templates/create.html')


@bp.route('/<int:tid>/update', methods=['GET', 'POST'])
@login_required
def update(tid):
    if request.method == 'POST':
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if 'file' in request.files:
            temFile = request.files['file']
            print(temFile.filename)
            fileNameLen=len(temFile.filename)
        else:
            fileNameLen=0
        if 'file' not in request.files or fileNameLen==0:
            t = {}
            t['id'] = tid
            t['name']=request.form['name']
            t['definition']=''
            t['updated_at']=''
            return render_template('templates/update.html', t=t ,mess= 'لطفا فایل عکس را بارگذاری نمایید!')
        else:
            basePath = "%s/%s" % (current_app.config['BASE_UPLOAD_PATH'], "template"  )
            print("basePath: %s" % basePath)
            if not os.path.exists(basePath):
                os.makedirs(basePath)
            #else:
            #    return 'Please specify an other name', 400
            file="%s/%s" % (basePath , secure_filename(temFile.filename))
            temFile.save(file)
            with open(file, 'r') as f:
                temp_file = f.read()

            print(request.form.keys())

            conn = db.get_db()
            cursor = conn.cursor()
            cursor.execute(db.query_string(
                'UPDATE [Templates] SET [name] = %s, [definition] = %s, [updated_at] = %s WHERE id = %d AND [deleted_at] is NULL'),
                (request.form['name'], temp_file, current_time, tid)
            )
            conn.commit()
            cursor.close()
            return redirect(url_for('templates.index'))
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('SELECT * FROM [Templates] WHERE id = %d'), (tid,))
    t = cursor.fetchone()
    cursor.close()
    return render_template('templates/update.html', t=t)

@bp.get('/encoder')
@login_required
def encoder():
    return render_template('templates/base64encoder.html')
