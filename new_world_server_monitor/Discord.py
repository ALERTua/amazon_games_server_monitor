import asyncio
import os
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count

# noinspection PyPackageRequirements
from discord import Intents, Guild, TextChannel
# noinspection PyPackageRequirements
from discord.ext.commands import Bot
from global_logger import Log

log = Log.get_logger()

ADMIN_CHANNEL_ID = os.getenv('NW_CHANNEL_ID')
ADMIN_CHANNEL_ID = int(ADMIN_CHANNEL_ID)
BOT_TOKEN = os.getenv('NW_BOT_TOKEN')


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

    def _set_guild(self):
        guilds = self.guilds
        if not guilds:
            log.error("No servers detected. Cannot proceed.")
            self.exit()

        self.guild = guilds[0]

    async def wait_guild(self):
        while not self.guild:
            log.debug("waiting guild")
            await asyncio.sleep(1)

        log.debug("got guild")

    async def notification(self, *args, **kwargs):
        admin_channel_id = ADMIN_CHANNEL_ID
        admin_channel: TextChannel = self.get_channel(admin_channel_id)
        await admin_channel.send(*args, **kwargs)

    async def on_ready(self):
        log.green(f'Logged in as {self.user.name} {self.user.id}')
        await self.wait_until_ready()
        self._set_guild()
        await self.wait_guild()
        log.debug("Bot Ready")


if __name__ == '__main__':
    log.verbose = True
    intents = Intents.default()
    intents.members = True
    bot = DiscordBotBase(command_prefix='!', intents=intents)  # description=description
    bot.run(BOT_TOKEN)
    print("")
