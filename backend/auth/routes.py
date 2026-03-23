from quart import Blueprint, request, jsonify
from datetime import datetime
from .models import User, get_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/register', methods=['POST'])
async def register():
    """注册接口"""
    data = await request.get_json()

    db = next(get_db())

    # 检查用户是否已存在
    existing_user = db.query(User).filter_by(username=data['username']).first()
    if existing_user:
        return jsonify({'error': '用户名已存在'}), 400

    # 创建新用户
    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.add(user)
    db.commit()

    return jsonify({'message': '注册成功'}), 201


@auth_bp.route('/api/login', methods=['POST'])
async def login():
    """登录接口"""
    data = await request.get_json()

    db = next(get_db())

    # 查找用户
    user = db.query(User).filter_by(username=data['username']).first()

    # 验证密码
    if user and user.check_password(data['password']):
        # 确定用户角色
        role = 'admin' if user.is_admin else 'family'

        return jsonify({
            'message': '登录成功',
            'token': f'token-{user.id}-{int(datetime.utcnow().timestamp())}',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'name': user.username,  # 使用用户名作为显示名称
                'role': role
            }
        }), 200
    else:
        return jsonify({'error': '用户名或密码错误'}), 401