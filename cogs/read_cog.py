import settings
import logging
from discord.ext import commands
from discord import app_commands, Interaction
import discord
from utils.log import log
from typing import Optional
import random

class ReadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="read", description="測試訊息已讀")
    async def read(self, interaction: Interaction, user: discord.User|None=None):
        """測試訊息已讀"""
        if user is None:
            user = interaction.user
        if user.bot:
            await interaction.response.send_message("無法對機器人使用此指令", ephemeral=True)
            return
        log(interaction, user)
        try:
            embed = discord.Embed(
                title="已讀測試",
                color=discord.Color.green()
            )
            embed.set_image(url=f"{settings.SERVER_URL}/img/{user.name}-{user.id}-{random.randint(100000000, 1000000000)}")
            embed.set_footer(text=f"觸發者: {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
            await user.send(embed=embed)
            await interaction.response.send_message(f"已發送訊息給 {user.mention}，請查看私訊！")
        except Exception as e:
            logging.error(f"發送訊息給 {user} 時發生錯誤: {e}")
            await interaction.response.send_message(f"發送訊息時發生錯誤: {e}", ephemeral=True)

    @app_commands.command(name="url", description="產生已讀測試圖片 URL")
    @app_commands.describe(target_user="對方名稱", user="通知接收者 (預設為自己)", 
                            remark="備註")
    async def url(self, interaction: Interaction, target_user: str, user: Optional[discord.User]=None, remark: Optional[str]=None):
        """產生已讀測試圖片 URL"""
        if user is None:
            user = interaction.user
        url = f"{settings.SERVER_URL}/img/{target_user}{f"({remark})" if remark else ""}-{user.id}-{random.randint(100000000, 1000000000)}"
        embed = discord.Embed(
            title="已讀測試圖片 URL",
            description=f"請將以下圖片傳給 `{target_user}`：\n```{url}```",
            color=discord.Color.blue()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReadCog(bot))
    logging.info(f'{__name__} 已載入')