"""
初始化测试用户
"""
import os
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATA_DIR
from auth.models import User

DB_NAME = "db.sqlite3"
db_path = os.path.join(DATA_DIR, DB_NAME)

# 创建引擎
engine = create_engine(f"sqlite:///{db_path}")
Session = sessionmaker(bind=engine)
db = Session()

# 检查用户是否已存在
def user_exists(username):
    return db.query(User).filter_by(username=username).first() is not None

# 创建测试用户
test_users = [
    {
        'username': 'admin',
        'email': 'admin@example.com',
        'password': 'admin123',
        'is_admin': True
    },
    {
        'username': 'family',
        'email': 'family@example.com',
        'password': 'family123',
        'is_admin': False
    },
    {
        'username': 'monitor',
        'email': 'monitor@example.com',
        'password': 'monitor123',
        'is_admin': False
    }
]

for user_data in test_users:
    if not user_exists(user_data['username']):
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            is_admin=user_data['is_admin']
        )
        user.set_password(user_data['password'])
        db.add(user)
        print(f"创建用户: {user_data['username']}")
    else:
        print(f"用户已存在，跳过: {user_data['username']}")

db.commit()
db.close()

print("\n测试用户初始化完成！")
print("管理员: admin / admin123")
print("家属: family / family123")
print("监护人: monitor / monitor123")
