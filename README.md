# 面向独居老人的隐私保护型异常行为识别与应急响应系统

## 快速启动

### 后端

```bash
cd backend
pip install -r requirements.txt
python app.py
```

后端运行在 http://localhost:8000

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:3000

## 说明

- 数据库使用 SQLite，无需额外安装数据库服务
- 首次启动后端会自动创建数据库文件 `backend/data/db.sqlite3`