# Card
این برنامه برای تولید تصویر کارت جهت چاپ بر مبنای یک قالب و داده های اکسل توسعه داده شده است.
گام های اجرای این برنامه
۱- ابتدا باید فایل قالب که شامل تصاویر پس زمینه و تصاویر رو مانند عکس فرد است و همچنین موقعیت قرار گرفتن هر یک از عکسها و اطلاعات را مشخص میکند تهیه شود. 
۲- فایل قالب باید در قسمت قالبها بارگزاری شود
۳- اکسل حاوی اطلاعات و فایل فشرده حاوی تصاویر مرتبط با هر رکورد در قالب یک دسته بارگزاری شود
۴- برنامه پس زمینه با دریافت بسته جدید آن را پردازش نموده و تصاویر را تولید میکند و در قالب یک فایل فشرده ذخیره میکند تا کاربر بتواند آن را دانلود نماید
۵- کابر با مراجعه به بخش دسته ها نتیجه پردازش را دانلود می نماید.

## Requirements

- Python 3.11
- Sqlite or MSSQL 2008 or above

## Configuration

فایل پیکربندی برنامه در مسیر `instance/config.cfg` قرار دارد.
برای پیکربندی از قالب ذیل استفاده کنید:

| Name | Description | Value |
|---|---|---|
| SECRET_KEY | Secret key for app | "" |
| DATABASE_TYPE | Allowed values: `mssql` and `sqlite` | "sqlite" |
| SQLITE_PATH | Path to SQLite file | "./card.db" |
| MSSQL_DATABASE_HOST | MSSQL db host address | "127.0.0.1" |
| MSSQL_DATABASE_PORT | MSSQL db port | "1433" |
| MSSQL_DATABASE_USERNAME | MSSQL db username | "org_CARD_APP" |
| MSSQL_DATABASE_PASSWORD | MSSQL db password | "org-is@PASAT4" |
| MSSQL_DATABASE_NAME | MSSQL db name | "card" |
| BASE_UPLOAD_PATH | Base path of upload directory | "/home/app/app_dir/Card/card/assets/uploads" |
| BASE_OUTPUT_PATH | Base path of output directory | "/home/app/app_dir/Card/card/assets/output"" |
| FONTS_PATH | Base path of fonts directory | "/home/app/app_dir/Card/card/assets/fonts" |
| WORKER_PERIOD | Number of workers for running with the Flask internal server | 5 |
| APPLICATION_ROOT | Root of the URI path for the application | "/card/" |
| LOGIN_PAGE_ADDRESS | Login page address of org. If user is not login he/she is redirected to this address to login. | "http://login.org.ir" |
| AUTH_SERVICE_BASE_URI | Base address for the authentication service of org. | "http://auth.org.ir/v1/" |
| AUTH_VALIDATION_ENDPOINT | The token validation API address. This path is appended to `AUTH_SERVICE_BASE_URI` | "/validateJWTtoken" |
| REPORTS_PATH | The temporary directory path for generating reports and preparing them before download | "/tmp/card" |

## Authentication

در صورتی که از یک سرویس احراز هویت بیرونی استفاده میکنید توکن باید به آدرس ذیل ارجاع شود:
```text
http://<host address>/card/auth/token/<the JWT token>
```

برای راه اندازی یک سرور احراز هویت از نمونه نرم افزار ذیل میتوانید استفاده کنید:
https://github.com/juanifioren/django-oidc-provider/tree/master/example


بعد از دریافت توکن نرم افزار از طریق آدرس تنظیم شده در `AUTH_VALIDATION_ENDPOINT` توکن را بررسی و اعتبار سنجی می نماید.

### JWT token payload

The payload of any JWT token passed to the app should have the following fields ***exactly***:

| Field | Description |
| --- | --- |
| FirstName | نام کاربر |
| LastName | نام خانوادگی |
| UserName | نام کاربری |
| exp | زمان انقضا |

بطور نمونه کاربر از طریق آدرس ذیل میتواند مستقیما وارد برنامه شود: 
http://localhost:5000/card/auth/token/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJGaXJzdE5hbWUiOiJhZG1pbiIsIkxhc3ROYW1lIjoiYWRtaW4iLCJVc2VyTmFtZSI6ImFkbWluIiwiZXhwIjoxNzA0NTc3ODM3fQ.uOjwJ8hMGK1XY_RWjmszw3fOCSxp1HG7AMvWEB6Nn1Y



فرض میشود که کاربر مجاز برنامه در جدول  `allowed_users` تعریف شده است.


### SQLite

The schema of the table is defined in the `card/assets/schema-sqlite.sql` file.


### راه اندازی در ویندوز:
c:

cd \myServices\card

rem py -m venv c:\myServices\card\wenv

wenv\Scripts\activate

py -m pip install -r requirments.txt

py -m flask --app card run --reload

py -m flask --app card worker


### run from mac
source ./venv/bin/activate 



