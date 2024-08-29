from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
import sqlite3
import json

app = FastAPI()

# 静的ファイルの設定
app.mount("/static", StaticFiles(directory="static"), name="static")

# データベースの初期化
def init_db():
    conn = sqlite3.connect('chat.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.get("/")
async def get():
    return {"message": "Welcome to the chat app!"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            
            # メッセージをデータベースに保存
            conn = sqlite3.connect('chat.db')
            c = conn.cursor()
            c.execute("INSERT INTO messages (content) VALUES (?)", (data,))
            conn.commit()
            
            # 最新の10件のメッセージを取得
            c.execute("SELECT content FROM messages ORDER BY id DESC LIMIT 10")
            messages = c.fetchall()
            conn.close()
            
            # メッセージを新しい順に並べ替えて送信
            response = json.dumps([msg[0] for msg in reversed(messages)])
            await websocket.send_text(response)
    except WebSocketDisconnect:
        print("Client disconnected")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)