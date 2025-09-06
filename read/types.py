from datetime import datetime


class ReadCtx:
    def __init__(self, event_id: str, access_count: int, time: datetime, data: dict):
        self.event_id = event_id
        """事件 ID"""
        self.access_count = access_count
        """存取次數"""
        self.time = time
        """觸發時間"""
        self.data = data
        """附加資料"""
