"""
WebSocket 处理器
处理实时视频流和检测结果
"""
import asyncio
import json
import base64
import numpy as np
import cv2
from datetime import datetime
from typing import Dict, Optional
from quart import websocket

from core.fall_detector import FallDetector, SessionResult, Event
from core.types import EventType, RiskLevel


class VideoWebSocketHandler:
    """WebSocket 视频流处理器"""

    def __init__(self, model_path: str = "core/models/yolo11s-pose.onnx"):
        """初始化处理器"""
        self.fall_detector = FallDetector(model_path)
        self.active_sessions: Dict[str, str] = {}  # video_id -> session_id
        self.video_options: Dict[str, dict] = {}  # video_id -> options

    async def handle_connection(self):
        """处理 WebSocket 连接"""
        try:
            while True:
                message = await websocket.receive()
                await self.process_message(message)
        except Exception as e:
            print(f"WebSocket 错误: {e}")
            await self.cleanup()
        finally:
            print("WebSocket 连接关闭")

    async def process_message(self, message: str):
        """处理接收到的消息"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')

            if msg_type == 'start':
                await self.handle_start(data)
            elif msg_type == 'frame':
                await self.handle_frame(data)
            elif msg_type == 'stop':
                await self.handle_stop(data)
            else:
                print(f"未知消息类型: {msg_type}")
                await self.send_error(f"未知消息类型: {msg_type}")

        except json.JSONDecodeError:
            print("JSON 解析错误")
            await self.send_error("消息格式错误")
        except Exception as e:
            print(f"处理消息错误: {e}")
            await self.send_error(f"处理消息失败: {str(e)}")

    async def handle_start(self, data: dict):
        """处理开始视频流"""
        video_id = data['data'].get('videoId')
        options = data['data'].get('options', {})

        if not video_id:
            await self.send_error("缺少 videoId")
            return

        # 创建检测会话
        session_id = self.fall_detector.create_session()
        self.active_sessions[video_id] = session_id
        self.video_options[video_id] = options

        print(f"视频流开始: {video_id}, 会话ID: {session_id}")

        # 发送确认消息
        await self.send_message({
            'type': 'info',
            'data': {
                'message': '视频流已启动',
                'videoId': video_id
            }
        })

    async def handle_frame(self, data: dict):
        """处理视频帧"""
        video_id = data['data'].get('videoId')
        frame_base64 = data['data'].get('frame')
        timestamp = data['data'].get('timestamp')

        if not video_id or not frame_base64:
            await self.send_error("缺少必要参数")
            return

        # 检查会话是否存在
        if video_id not in self.active_sessions:
            await self.send_error(f"视频流不存在: {video_id}")
            return

        try:
            # 解码 Base64 图片
            frame_data = base64.b64decode(frame_base64.split(',')[1])
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if frame is None:
                await self.send_error("帧解码失败")
                return

            # 获取会话 ID
            session_id = self.active_sessions[video_id]

            # 处理帧（异步）
            result: SessionResult = await self.fall_detector.process_frame_async(
                session_id, frame, timestamp
            )

            # 发送处理后的帧
            await self.send_processed_frame(result.processed_frame, video_id, timestamp)

            # 如果有事件，发送检测结果
            if result.events:
                for event in result.events:
                    await self.send_detection_result(event, video_id, timestamp)

        except Exception as e:
            print(f"处理帧错误: {e}")
            await self.send_error(f"处理帧失败: {str(e)}")

    async def handle_stop(self, data: dict):
        """处理停止视频流"""
        video_id = data['data'].get('videoId')

        if not video_id:
            await self.send_error("缺少 videoId")
            return

        # 关闭会话
        if video_id in self.active_sessions:
            session_id = self.active_sessions[video_id]
            self.fall_detector.close_session(session_id)
            del self.active_sessions[video_id]
            del self.video_options[video_id]

            print(f"视频流停止: {video_id}")

            await self.send_message({
                'type': 'info',
                'data': {
                    'message': '视频流已停止',
                    'videoId': video_id
                }
            })

    async def send_processed_frame(self, frame: np.ndarray, video_id: str, timestamp: float):
        """发送处理后的帧"""
        try:
            # 编码为 JPEG
            _, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')

            # 发送消息
            await self.send_message({
                'type': 'frame',
                'data': {
                    'frame': f'data:image/jpeg;base64,{frame_base64}',
                    'videoId': video_id,
                    'timestamp': timestamp
                }
            })

        except Exception as e:
            print(f"发送帧错误: {e}")

    async def send_detection_result(self, event: Event, video_id: str, timestamp: float):
        """发送检测结果"""
        try:
            # 将事件转换为字典
            event_data = {
                'type': event.event_type.value if hasattr(event.event_type, 'value') else str(event.event_type),
                'riskLevel': event.risk_level.value if hasattr(event.risk_level, 'value') else str(event.risk_level),
                'confidence': event.confidence,
                'description': event.description,
                'timestamp': datetime.now().isoformat()
            }

            # 发送消息
            await self.send_message({
                'type': 'detection',
                'data': event_data
            })

            print(f"检测结果: {event_data}")

        except Exception as e:
            print(f"发送检测结果错误: {e}")

    async def send_message(self, message: dict):
        """发送消息到客户端"""
        try:
            await websocket.send(json.dumps(message))
        except Exception as e:
            print(f"发送消息错误: {e}")

    async def send_error(self, message: str):
        """发送错误消息"""
        await self.send_message({
            'type': 'error',
            'message': message
        })

    async def cleanup(self):
        """清理资源"""
        # 关闭所有活跃会话
        for video_id, session_id in self.active_sessions.items():
            self.fall_detector.close_session(session_id)
        self.active_sessions.clear()
        self.video_options.clear()


# 创建全局处理器实例
websocket_handler = VideoWebSocketHandler()