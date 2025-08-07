import asyncio
import websockets

connected_clients = set()

async def handler(websocket: websockets.ClientConnection, path: str) -> None:
    # 加入連線
    connected_clients.add(websocket)
    print(f"🔗 新用戶加入：{websocket.remote_address}")
    try:
        async for message in websocket:
            print(f"📨 來自 {websocket.remote_address} 的訊息：{message}")
            # 回覆訊息
            await websocket.send(f"你說：{message}")
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"❌ 連線錯誤：{websocket.remote_address}，原因：{e}")
    except Exception as e:
        print(f"⚠️ 其他錯誤：{e}")
    finally:
        # 移除連線
        connected_clients.discard(websocket)
        print(f"👋 用戶離開：{websocket.remote_address}")

async def main():
    server = await websockets.serve(
        handler,
        host="0.0.0.0",
        port=8765,
        ping_interval=20,   # 每 20 秒自動發送 ping
        ping_timeout=10     # 如果 10 秒內沒收到 pong，關閉連線
    )
    print("🚀 WebSocket 伺服器啟動於 ws://0.0.0.0:8765")
    await server.wait_closed()

asyncio.run(main())