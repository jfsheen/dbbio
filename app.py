from app import create_app
from database import init_db
import os

# 创建应用实例
app = create_app()

# 初始化数据库 - 现在在应用上下文中执行
with app.app_context():
    init_db()

if __name__ == '__main__':
    # 确保静态文件和模板目录存在
    if not os.path.exists('app/static'):
        os.makedirs('app/static')
    if not os.path.exists('app/templates'):
        os.makedirs('app/templates')
    
    # 运行应用
    if os.environ.get('FLASK_ENV') == 'development':
        app.run(debug=True, host='0.0.0.0', port=5000)
    else:
        pass