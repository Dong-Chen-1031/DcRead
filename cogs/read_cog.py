
import logging
from discord.ext import commands
from discord import app_commands, Interaction
import discord
from utils.log import log


class ReadCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="read", description="測試訊息已讀")
    async def read(self, interaction: Interaction, user: discord.User):
        """測試訊息已讀"""
        log(interaction, user)
        embed = discord.Embed(
            title="已讀測試",
            color=discord.Color.green()
        )
        embed.set_image(url=f"http://test.doong.me/img/{user.display_name}-{user.id}-{interaction.id}")
        await user.send(embed=embed)
        await interaction.response.send_message(f"已發送訊息給 {user.mention}，請查看私訊！", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(ReadCog(bot))
    logging.info(f'{__name__} 已載入')