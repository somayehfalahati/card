from flask import Blueprint, render_template, redirect, url_for, request, current_app, send_from_directory, send_file
from . import db
import yaml, os, datetime
from werkzeug.utils import secure_filename
from .auth import login_required
# مدیریت دسته های پردازش - هر فایل اکسل و عکسهای مرتبط در قالب یک دسته ثبت میشود تا در پس زمینه عکس کارتها بر اساس لیست تولید شود.

bp = Blueprint('batches', __name__, url_prefix='/card/batches')

# این تابع فهرست دسته های را نمایش میدهد
@bp.get('/')
@login_required
def index():
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string("""
        SELECT b.[id]
            ,b.[name]
            ,[template_id]
            ,t.name as template_name
            ,t.definition
            ,[data_file_path]
            ,[status]
            ,[processed_item_count]
            ,b.[created_at]
            ,[picked_at]
            ,[finished_at]
        FROM [Batches] b
        INNER JOIN [Templates] t on b.template_id = t.id
        WHERE b.[deleted_at] is NULL and t.[deleted_at] is NULL
    """))
    batches = cursor.fetchall()
    
    dictrows = [dict(row) for row in cursor]
    for r in dictrows:
        r['file_name'] = secure_filename(batches[i]['name']) + ".zip"
        r['is_ready'] = batches[i]['status'].strip() == "FINISHED"
    cursor.close()

        
    #for i in range(len(batches)):
    #    batches[i]['file_name'] = secure_filename(batches[i]['name']) + ".zip"
    #    batches[i]['is_ready'] = batches[i]['status'].strip() == "FINISHED"

    return render_template('batches/index.html', batches=batches)

# این تابع صفحه ایجاد دسته را نمایش داده و عملیات ثبت را انجام می دهد
@bp.route('/create/<int:tid>', methods=['GET', 'POST'])
@login_required
def create(tid):
    if tid is None:
        return 'Please specify a template', 400

    if request.method == 'POST':
        name = request.form['name']
        basePath = "%s/%s" % (current_app.config['BASE_UPLOAD_PATH'], secure_filename(name))
        if not os.path.exists(basePath):
            os.makedirs(basePath)
        else:
            print(basePath)
            return 'Please specify an other name because path with this name exists os server.', 400

        if 'data' not in request.files:
            os.rmdir(basePath)
            return 'Please upload the data file', 400
        dataFile = request.files['data']
        if dataFile.filename.rsplit('.', 1)[1].lower() != "xlsx":
            os.rmdir(basePath)
            return 'Please upload the data file as a xlsx file', 400
        dataFile.save("%s/data.xlsx" % basePath)

        if 'images' in request.files:
            imagesFile = request.files['images']
            if imagesFile.filename.rsplit('.', 1)[1].lower() != "zip":
                os.rmdir(basePath)
                return 'Please upload the images file as a zip file', 400
            imagesFile.save("%s/images.zip" % basePath)

        current_time = datetime.datetime.now()

        conn = db.get_db()
        cursor = conn.cursor()
        cursor.execute(
            db.query_string('INSERT INTO [Batches] ([name],[template_id],[data_file_path],[status],[created_at],[processed_item_count]) values (%s,%d,%s,%s,%s,%d)'),
            (name, tid, basePath, 'CREATED', current_time.strftime("%Y-%m-%d %H:%M:%S"),0)

        )
        conn.commit()
        cursor.close()
            
        return redirect(url_for('batches.index'))
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM [Templates] WHERE id = :ss AND [deleted_at] is NULL', {'ss':tid})
    template = cursor.fetchone()
    cursor.close()

    config = yaml.safe_load(template['definition'])

    hasImages = False
    for t in config['templates']:
        if 'imageFields' in t:
            if len(t['imageFields']) > 0:
                hasImages = True

    return render_template('batches/create.html', t=template, c=config, hasImages=hasImages)

# این تابع امکان دانلود نتیجه پردازش یک دسته را بر میگرداند
@bp.get('/download/<bid>')
@login_required
def download(bid):
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('SELECT b.name FROM [Batches] b INNER JOIN [Templates] t on b.template_id = t.id WHERE b.id = %d AND b.deleted_at is NULL AND t.deleted_at is NULL'), (bid,))
    b = cursor.fetchone()
    cursor.close()

    if b == None:
        return "File does not exits", 404
    
    secureBatchName = secure_filename(b['name'])
    basePath = "%s/%s" % (current_app.config["BASE_OUTPUT_PATH"], secureBatchName)

    if os.path.exists("%s/%s.zip" % (basePath, secureBatchName)):
        return send_from_directory(basePath, "%s.zip" % secureBatchName)
    
    return "File does not exits", 404

# این تابع امکان حذف یک ردیف از دسته ها را فراهم  میکند
@bp.get('/<int:bid>/delete')
@login_required
def delete(bid):
    if bid is None:
        return 'Please specify a template'

    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = db.get_db()
    cursor = conn.cursor()
    cursor.execute(db.query_string('UPDATE [Batches] SET [deleted_at] = %s WHERE id = %d AND [deleted_at] is NULL'), (current_time, bid))
    conn.commit()
    cursor.close()
    
    return redirect(url_for('batches.index'))