#!/usr/bin/env python3
"""
Quart Web 應用程式啟動器
"""
import asyncio
import flask

if __name__ == '__main__':
    print("🚀 啟動 Quart Web 伺服器...")
    asyncio.run(flask.run())
