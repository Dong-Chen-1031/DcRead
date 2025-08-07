"""
asyncio.Queue 通信模組
用於 Quart 和 Discord Bot 之間的通信
"""
import asyncio
from typing import Dict, Any
import logging

# 全域通信佇列
notification_queue = asyncio.Queue()

async def send_notification(data: Dict[str, Any]):
    """發送通知到佇列"""
    try:
        await notification_queue.put(data)
        logging.info(f"📤 已送出通知: {data.get('type', 'unknown')}")
    except Exception as e:
        logging.error(f"發送通知失敗: {e}")

async def get_notification():
    """從佇列取得通知"""
    try:
        return await notification_queue.get()
    except Exception as e:
        logging.error(f"取得通知失敗: {e}")
        return None
