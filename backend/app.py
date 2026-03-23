from quart import Quart, request, websocket
from config import Config
from auth import init_db, auth_bp
from websocket_handler import websocket_handler

app = Quart(__name__)
app.config.from_object(Config)

# 初始化数据库
init_db(app)

# 注册蓝图
app.register_blueprint(auth_bp)

# CORS 中间件
@app.after_request
async def after_request(response):
    origin = request.headers.get('Origin')
    if origin in ['http://localhost:3000', 'http://127.0.0.1:3000']:
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
async def index():
    return {'message': 'Backend API is running'}

@app.websocket('/ws/video')
async def video_websocket():
    """WebSocket 端点，用于实时视频流处理"""
    await websocket_handler.handle_connection()

if __name__ == '__main__':
    app.run(debug=True, port=5000)
