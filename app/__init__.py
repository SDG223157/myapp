from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.config import Config
from app.dataframe_manager import MySQLDataFrameManager
import os

db = SQLAlchemy()
df_manager = None

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)
    
    db.init_app(app)
    
    # Initialize DataFrame manager
    global df_manager
    df_manager = MySQLDataFrameManager(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv('MYSQL_USER'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE'),
        port=int(os.getenv('MYSQL_PORT', '3306'))
    )
    
    from app.routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
    
    return app