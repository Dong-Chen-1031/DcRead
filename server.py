from aiohttp import web
import os
from datetime import datetime
from discord.ext import commands
import settings
import discord
import logging

bot = None  # 將 bot 設為全域變數

file_access_count = {}

# 圖片儲存的資料夾
IMAGE_FOLDER = 'img'
os.makedirs(IMAGE_FOLDER, exist_ok=True)

async def hello(request):
    return web.Response(text="✅ aiohttp 成功運作！")

async def send_read_msg(data:dict):
        """發送已讀通知"""

        filename: str = data.get('filename', '未知檔案')
        count: int = data.get('count', 0)
        timestamp = data.get('timestamp', datetime.now().isoformat())
        channel = bot.get_user(int(filename.split('-')[1]))  # 假設 filename 格式為 "user_id-unique_id"
        # 建立 Embed 訊息
        embed = discord.Embed(
            title="訊息已讀",
            description=f"使用者 `{filename.split('-')[0]}` 已讀取訊息！",
            color=0xff9900,  # 橘色
            timestamp=datetime.fromisoformat(timestamp)
        )
        
        embed.add_field(name="事件ID", value=f"`{filename}`", inline=True)
        embed.add_field(name="存取次數", value=f"**{count}**", inline=True)
        embed.add_field(name="觸發時間", value=f"<t:{int(datetime.fromisoformat(timestamp).timestamp())}:F>", inline=False)
        
        embed.set_footer(text="由 已讀測試 觸發")
        
        try:
            await channel.send(embed=embed)
            logging.info(f"✅ 已發送 Discord 通知: {filename} 存取 {count} 次")
        except Exception as e:
            logging.error(f"發送 Discord 訊息時發生錯誤: {e}")

async def serve_image(request: web.Request):
    filename = request.match_info['filename']
    
    # 紀錄詳細日誌
    file_access_count[filename] = 1 if filename not in file_access_count else file_access_count[filename] + 1
    
    # 檢查是否需要發送通知
    if file_access_count[filename] == 3:
        # 發送通知給 Discord Bot
        await send_discord_notification(filename)
    
    # 傳送圖片文件
    try:
        gif_path = os.path.join(IMAGE_FOLDER, "5.png")
        if os.path.exists(gif_path):
            return web.FileResponse(gif_path)
        else:
            
            return web.Response(text=f"圖片 {filename} 已載入 (第 {file_access_count[filename]} 次)", content_type='text/plain')
    except Exception as e:
        return web.Response(text=f"載入圖片時發生錯誤: {e}", status=500)

async def send_discord_notification(filename):
    """發送通知給 Discord Bot"""
    message_data = {
        'type': 'file_access_warning',
        'filename': filename,
        'count': file_access_count[filename],
        'timestamp': datetime.now().isoformat()
    }
    
    await send_read_msg(message_data)

async def create_app():
    """創建 aiohttp 應用"""
    app = web.Application()
    app.router.add_get('/', hello)
    app.router.add_get('/img/{filename}', serve_image)
    return app

async def run(bot_: commands.Bot):
    global bot
    bot = bot_
    """啟動 aiohttp 應用"""
    app = await create_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', settings.PORT)
    await site.start()
    logging.info(f"🌐 aiohttp Server 啟動於 {settings.SERVER_URL}")