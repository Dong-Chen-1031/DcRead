import asyncio
import inspect
from aiohttp import web
import os
from datetime import datetime
from discord.ext import commands
import settings
from typing import Any, Awaitable, Optional, Callable, Union
import discord
import logging
import uuid

server_run = False  # 用於標記伺服器是否已啟動

server_url = None  # 將 url 設為全域變數

file_access_count = {}

file_handlers = {}

# 圖片儲存的資料夾
IMAGE_FOLDER = 'img'
os.makedirs(IMAGE_FOLDER, exist_ok=True)


class ReadCtx:
    def __init__(self, event_id, times, data):
        pass

async def root(request):
    return web.Response(text="✅ Read Test 成功運作！")

async def serve_image(request: web.Request):
    filename = request.match_info['filename']
    
    # 紀錄詳細日誌
    file_access_count[filename] = 1 if filename not in file_access_count else file_access_count[filename] + 1
    
    if file_access_count[filename] == 3:
        # 發送通知給 Discord Bot
        await call_handler(filename)
    
    # 傳送圖片文件
    try:
        gif_path = os.path.join(IMAGE_FOLDER, "5.png")
        if os.path.exists(gif_path):
            return web.FileResponse(gif_path)
        else:
            
            return web.Response(text=f"圖片 {filename} 已載入 (第 {file_access_count[filename]} 次)", content_type='text/plain')
    except Exception as e:
        return web.Response(text=f"載入圖片時發生錯誤: {e}", status=500)

def get_image_url(handle:Callable, data:Optional[any]) -> str:
    global file_handlers
    img_id = uuid.uuid4().hex
    file_handlers[img_id] = (handle, data)
    return f"http://localhost:8080/{img_id}"

async def safe_call_handler(
    handler: Union[Callable[[Any], Any], Callable[[Any], Awaitable[Any]]], 
    data: Any,
    filename: str
) -> None:
    """安全地調用處理函數（同步或異步），依參數數量決定傳入內容"""
    try:
        sig = inspect.signature(handler)
        param_count = len(sig.parameters)

        if asyncio.iscoroutinefunction(handler):
            if param_count == 0:
                await handler()
            elif param_count == 1:
                await handler(data)
            else:
                await handler(data, filename)
        else:
            if param_count == 0:
                handler()
            elif param_count == 1:
                handler(data)
            else:
                handler(data, filename)
    except Exception as e:
        logging.error(f"處理函數執行失敗: {e}", exc_info=True)

async def call_handler(filename):
    """呼叫對應的處理函數"""
    if filename in file_handlers:
        handle, data = file_handlers[filename]
        await safe_call_handler(handle, data, filename)

async def create_app():
    """創建 aiohttp 應用"""
    app = web.Application()
    app.router.add_get('/', root)
    app.router.add_get('/{filename}', serve_image)
    return app

async def start_server(ip:str='127.0.0.1', port:int=8080, url:str|None=None) -> str:
    """啟動 aiohttp 伺服器

    Args:
        ip (str): 伺服器 IP 地址
        port (int): 伺服器端口
        url (str): 完整的外網可存取之伺服器 URL (含端口及 http://)
    """
    global server_url, server_run
    if url is None:
        url = f"http://{ip}:{port}"
    if server_run:
        logging.warning("伺服器已經在運行中，無需重複啟動。")
        return
    server_url = url
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, ip, port)
    await site.start()
    logging.info(f"🌐 aiohttp Server 啟動於 {url}")
    server_run = True
    return url