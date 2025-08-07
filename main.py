#!/usr/bin/env python3
"""
同時啟動 Discord Bot 和 Quart Web 伺服器
"""
import asyncio
from utils import log
import logging
import sys
from pathlib import Path

async def run_discord_bot():
    """啟動 Discord Bot"""
    try:
        # 導入並啟動 bot
        import discord
        from discord.ext import commands
        import os
        import settings
        
        intents = discord.Intents.all()
        bot = commands.Bot(command_prefix=settings.PREFIX, intents=intents)
        
        @bot.event
        async def on_ready():
            logging.info(f'Discord Bot 已登入為 {bot.user.name}')
            try:
                synced = await bot.tree.sync()
                logging.info(f'已同步 {len(synced)} 個斜線指令')
            except Exception as e:
                logging.error(f'同步指令失敗: {e}')

        # 載入模組
        async def load_extensions():
            for filename in os.listdir('./cogs'):
                if filename.endswith('.py'):
                    await bot.load_extension(f'cogs.{filename[:-3]}')
                    logging.info(f'已載入模組: {filename[:-3]}')

        await load_extensions()
        await bot.start(settings.DISCORD_BOT_TOKEN)
        
    except Exception as e:
        logging.error(f"Discord Bot 啟動失敗: {e}")

async def run_quart_server():
    """啟動 aiohttp Web 伺服器"""
    try:
        from quart_app import run
        logging.info("🌐 啟動 aiohttp Web 伺服器...")
        await run()
    except Exception as e:
        logging.error(f"aiohttp 伺服器啟動失敗: {e}")

async def main():
    """主程式"""
    logging.info("🚀 正在啟動應用程式...")
    
    # 確保必要的資料夾存在
    Path('logs').mkdir(exist_ok=True)
    Path('img').mkdir(exist_ok=True)
    
    try:
        # 同時運行 Discord Bot 和 Quart 伺服器
        await run_quart_server()
        await run_discord_bot()
    except KeyboardInterrupt:
        logging.info("👋 應用程式已停止")
    except Exception as e:
        logging.error(f"啟動應用程式時發生錯誤: {e}")

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("👋 程式已中斷")
    except Exception as e:
        logging.error(f"程式執行錯誤: {e}")
