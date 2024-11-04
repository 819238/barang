from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config.from_object(Config)

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'

from .routes import main, auth, admin
app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(admin)

with app.app_context():
    db.create_all()
    
    from .models import User
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', is_admin=True)
        admin_user.set_password('1914')
        db.session.add(admin_user)
        db.session.commit()