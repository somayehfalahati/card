import click
import time
from flask import current_app
from . import db, render
import datetime, yaml
import pandas as pd
from zipfile import ZipFile
import os, shutil
from werkzeug.utils import secure_filename
#  این برنامه سرور پردازش پس زمینه را ایجاد و راه اندازی نموده  و در فاصله زمانی فهرست دسته ها را بررسی مینماید
# در صورت دریافت یک بسته جدید آن را پردازش نموده و نتیجه را در قالب بک فایل فشرده ذخیره می نماید.
def run():
    while True:
        click.echo("Checking...")

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
                ,b.[created_at]
                ,[picked_at]
                ,[finished_at]
            FROM [Batches] b
            INNER JOIN [Templates] t on b.template_id = t.id
            WHERE [status] = 'CREATED' AND picked_at is NULL
                AND b.[deleted_at] is NULL AND t.[deleted_at] is NULL
        """))
        batches = cursor.fetchall()
        cursor.close()

        for b in batches:
            click.echo("Processing Batch ID: %d" % b['id'])

            current_time = datetime.datetime.now()
            cursor = conn.cursor()
            cursor.execute(db.query_string('UPDATE [Batches] SET picked_at = %s, status = %s WHERE id = %d'), (current_time.strftime("%Y-%m-%d %H:%M:%S"), 'RUNNING', b['id']))
            conn.commit()
            cursor.close()

            config = yaml.safe_load(b['definition'])
            
            secureBatchName = secure_filename(b['name'])
            fontsPath = current_app.config["FONTS_PATH"]
            inputBasePath = b["data_file_path"]
            outputBasePath = "%s/%s" % (current_app.config["BASE_OUTPUT_PATH"], secureBatchName)

            if os.path.exists(outputBasePath):
                shutil.rmtree(outputBasePath, ignore_errors=True)
            os.makedirs(outputBasePath)
            
            hasImages = False
            for t in config['templates']:
                if 'imageFields' in t:
                    if len(t['imageFields']) > 0:
                        hasImages = True

            imagesPath = ""
            if hasImages:
                imagesPath = "%s/images" % outputBasePath

                if os.path.exists(imagesPath):
                    shutil.rmtree(imagesPath, ignore_errors=True)
                os.makedirs(imagesPath)

                with ZipFile("%s/images.zip" % inputBasePath, 'r') as zipObj:
                    zipObj.extractall(path=imagesPath)
            
            outputDirPath = "%s/output" % outputBasePath
            if os.path.exists(outputDirPath):
                shutil.rmtree(outputDirPath, ignore_errors=True)
            os.makedirs(outputDirPath)

            print(fontsPath)
            # با دادن اطلاعات قالب و مسیر فونت ها و مسیر عکسها و مسیر خروجی  برنامه پردازشگر را آماده سازی میکند
            r = render.Render(config, fontsPath, imagesPath, outputDirPath)

            outputFiles = []
            # خواندن اطلاعات از اکسل
            data = pd.read_excel("%s/data.xlsx" % b['data_file_path'], dtype=str)

            # تولید تمام عکسها بر اساس اطلاعات خوانده شده از اکسل
            for row in data.itertuples(index=False):
                print(row)
                for v in r.render(row).values():
                    print(v)
                    outputFiles.append((v['path'], v['fileName']))
                
                cursor = conn.cursor()
                cursor.execute(db.query_string('UPDATE [Batches] SET processed_item_count =processed_item_count+ 1 WHERE id = %d'), (b['id'],))
                conn.commit()
                cursor.close()
            # فشرده کردن عکسهای تولید شده در یک فایل فشرده
            with ZipFile("%s/%s.zip" % (outputBasePath, secureBatchName), 'w') as zipObj:
                for fp, fn in outputFiles:
                    zipObj.write(fp, arcname=fn)

            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = conn.cursor()
            cursor.execute(db.query_string('UPDATE [Batches] SET finished_at = %s, status = %s WHERE id = %d'), (current_time, 'FINISHED', b['id']))
            conn.commit()
            cursor.close()
            

        time.sleep(current_app.config['WORKER_PERIOD'])