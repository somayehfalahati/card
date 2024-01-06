from flask import Flask, redirect, url_for, request, g
import click, jwt
# این تابع اصلی برنامه است که یک سرور فلسک راه اندازی نموده و صفحات برنامه را به سرور اضافه مینماید
def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True, static_url_path="/card/static")
    app.config.from_mapping(
            SECRET_KEY='dev'
    )

    if test_config is None:
        app.config.from_pyfile('config.cfg')
    else:
        app.config.from_mapping(test_config)

    from . import db
    db.init_app(app)
    
    # اگر مسیر اصلی نداشت به مسیر اصلی کارت ارجاع داده میشود
    @app.route('/')
    def hello1():
        return redirect(url_for('templates.index'))
    
    # مسیر اصلی برنامه با کارت شروع میشود
    @app.route('/card/')
    def hello():
        return redirect(url_for('templates.index'))

    from . import template
    from . import batch
    from . import auth
    from . import users
    app.register_blueprint(template.bp)
    app.register_blueprint(batch.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(users.bp)

    app.add_url_rule(
        "/batches/download/<bid>", endpoint="download", build_only=True
    )

    # اگر فرمان وورکر داده شد بجای برنامه اصلی برنامه پردازش پس زمینه اجرا میشود
    # این برنامه این امکان را میدهد پردازش سنگین در یک برنامه مجزا از برنامه اصلی اجرا شود و آن را کند نکند
    @app.cli.command("worker")
    def worker():
        """Runs the image generator worker"""
        from . import worker
        worker.run()

    return app


