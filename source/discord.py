import asyncio
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count

# noinspection PyPackageRequirements
from discord import Intents, Guild, TextChannel
# noinspection PyPackageRequirements
from discord.ext.commands import Bot
from global_logger import Log
from source import env

log = Log.get_logger()


class DiscordBotBase(Bot):
    def __init__(self, command_prefix, **options):
        super().__init__(command_prefix, **options)
        self._guild = None
        self.executor = ThreadPoolExecutor(max_workers=cpu_count() - 1)

    async def exit(self):
        log.printer("Quitting")
        await self.close()

    @property
    def guild(self) -> Guild:
        return self._guild

    @guild.setter
    def guild(self, value):
        self._guild = value
        log.debug(f"Guild: {value}")

    async def _set_guild(self):
        guilds = self.guilds
        if not guilds:
            log.error("No servers detected. Cannot proceed.")
            await self.exit()

        self.guild = guilds[0]

    async def wait_guild(self):
        while not self.guild:
            log.debug("waiting guild")
            await asyncio.sleep(1)

        log.debug("got guild")

    async def notification(self, *args, **kwargs):
        channel_id = env.DISCORD_CHANNEL_ID
        channel: TextChannel = self.get_channel(channel_id)
        await channel.send(*args, **kwargs)

    async def on_ready(self):
        log.green(f'Logged in as {self.user.name} {self.user.id}')
        await self.wait_until_ready()
        await self._set_guild()
        await self.wait_guild()
        log.debug("Bot Ready")


if __name__ == '__main__':
    log.verbose = True
    intents = Intents.default()
    intents.members = True
    bot = DiscordBotBase(command_prefix='!', intents=intents)  # description=description
    bot.run(env.DISCORD_BOT_TOKEN)
    pass