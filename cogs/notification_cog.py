import discord
from discord.ext import commands
import asyncio
import logging
from datetime import datetime
from communication import get_notification
import settings

class NotificationCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        """初始化通知 Cog"""
        self.bot: commands.Bot = bot

        # 通知頻道 ID（請修改為實際的頻道 ID）
        self.notification_channel_id = settings.NOTIFICATION_CHANNEL_ID  # 從 settings 讀取頻道 ID
        
        # 在 setup_hook 中啟動佇列監聽，而不是在 __init__ 中
        self.monitor_task = None
        
    async def cog_load(self):
        """當 cog 被載入時啟動監控任務"""
        self.monitor_task = asyncio.create_task(self.monitor_queue())
        
    def cog_unload(self):
        """當 cog 被卸載時取消監控任務"""
        if self.monitor_task:
            self.monitor_task.cancel()
    
    async def monitor_queue(self):
        """監控 asyncio.Queue 中的通知"""
        logging.info("📡 開始監控 Discord 通知佇列...")
        
        while True:
            try:
                # 從佇列取得通知
                notification_data = await get_notification()
                
                if notification_data:
                    await self.process_notification(notification_data)
                
            except asyncio.CancelledError:
                logging.info("通知監控任務已取消")
                break
            except Exception as e:
                logging.error(f"監控佇列時發生錯誤: {e}")
                await asyncio.sleep(1)
    
    async def process_notification(self, data):
        """處理通知資料"""
        try:
            if data.get('type') == 'file_access_warning':
                await self.send_file_access_warning(data)
            else:
                logging.warning(f"未知的通知類型: {data.get('type')}")
                
        except Exception as e:
            logging.error(f"處理通知時發生錯誤: {e}")
    
    async def send_file_access_warning(self, data):
        """發送檔案存取警告"""
        
        filename = data.get('filename', '未知檔案')
        count = data.get('count', 0)
        timestamp = data.get('timestamp', datetime.now().isoformat())
        channel = self.bot.get_user(int(filename.split('-')[1]))  # 假設 filename 格式為 "user_id-unique_id"
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

async def setup(bot: commands.Bot):
    await bot.add_cog(NotificationCog(bot))
