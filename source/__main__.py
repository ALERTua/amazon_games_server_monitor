import asyncio

from source import env
from source.discord import DiscordBotBase, Intents
from source.server_monitor import AmazonGamesServerMonitor


async def main():
    bot_ = DiscordBotBase(command_prefix='!', intents=Intents.default())
    await bot_.add_cog(AmazonGamesServerMonitor(bot=bot_, server_name=env.SERVER_NAME, url=env.STATUS_URL))
    await bot_.start(env.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())