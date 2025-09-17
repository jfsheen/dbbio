from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv

# 创建扩展实例
db = SQLAlchemy()
migrate = Migrate()

def create_app():

    load_dotenv()

    app = Flask(__name__)
    
    # 配置应用
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get(
            'DATABASE_URL', 
            'mysql+pymysql://dbbio:dbbio123!@localhost/dbbio_d1b?charset=utf8mb4'
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={
            'pool_recycle': 300,
            'pool_pre_ping': True,
            'pool_size': 10,
            'max_overflow': 20,
        },
        SQLALCHEMY_POOL_TIMEOUT=30
    )
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    # 注册蓝图
    from .routes import main_bp
    app.register_blueprint(main_bp)
    
    return app