import settings
import logging
import discord
from discord.ext import commands
import aiosqlite

logger = logging.getLogger("bot")


def run():
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(command_prefix="!", intents=intents)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send("Invalid command used.")

    
    @bot.event
    async def on_ready():
        logger.info(f"User : {bot.user}(id: {bot.user.id})")

        bot.db = await aiosqlite.connect("AngelBot.db")
        cursor = await bot.db.cursor()
        await cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, points INTEGER, inscrit BOOLEAN, enregistrer BOOLEAN)")
        await bot.load_extension("cogs.angelbot")

        await bot.db.commit()

    bot.run(settings.DISCORD_API_SECRET, root_logger=True)


if __name__ == "__main__":
    run()