# #!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
from collections import OrderedDict

import bs4
import discord.emoji
import pendulum
# noinspection PyPackageRequirements
import requests
from bs4 import BeautifulSoup
# noinspection PyPackageRequirements
from discord.ext import tasks
# noinspection PyPackageRequirements
from discord.ext.commands import Cog
from global_logger import Log
from source.discord import DiscordBotBase, Intents
from source import env

LOG = Log.get_logger()

STATUS_BASE = 'ags-ServerStatus-content-responses-response-server-status'
STATUS_UP = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--up'
STATUS_DOWN = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--down'
STATUS_MAINTENANCE = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--maintenance'
STATUS_FULL = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--full'

DELAY = env.DELAY_SEC


def check_url_accessible(url, response_code=200, **kwargs):
    LOG.debug("Checking %s. Waiting %s" % (url, response_code))
    try:
        response = requests.get(url, **kwargs)
    except Exception as e:
        LOG.debug("Connection error for %s: %s %s" % (url, type(e), e))
        return False, None

    output = response.status_code == response_code
    LOG.debug("Check for %s success: %s %s" % (url, response.status_code, output))
    return output, response


def get_html(url):
    r = requests.get(url, timeout=10)
    if r:
        return r.text


class AmazonGamesServerMonitor(Cog, name='Amazon Game Server Monitor'):
    def __init__(self, bot: DiscordBotBase, server_name: str = env.SERVER_NAME, url: str = env.STATUS_URL):
        self.bot = bot
        self.bot.remove_command("help")
        self.server_name = server_name
        self.url = url
        self.previous_result = None
        self.previous_result_date = pendulum.now(tz=pendulum.local_timezone())
        self.server_monitor.start()

    def cog_unload(self):
        self.server_monitor.cancel()

    @tasks.loop(seconds=DELAY)
    async def server_monitor(self):
        LOG.debug("Monitor start")
        try:
            await self.monitor()
        except Exception:
            LOG.exception(f"Error running monitor. Sleeping {DELAY}")
        else:
            LOG.green(f"Done. Sleeping {DELAY}")
        LOG.debug("Monitor end")

    @server_monitor.before_loop
    async def server_monitor_before_loop(self):
        LOG.debug("Monitor before loop")
        await self.bot.wait_until_ready()
        LOG.debug("Monitor before loop done")

    @server_monitor.after_loop
    async def server_monitor_after_loop(self):
        LOG.debug("Monitor after loop")
        pass

    async def monitor(self):
        accessible, response = check_url_accessible(self.url, timeout=1)
        text = f"{self.server_name} is {self.previous_result} @ {self.previous_result_date.to_time_string()}"
        if not accessible:
            LOG.error(f"{self.url} not accessible. Cannot proceed")
            await self.bot.change_presence(activity=discord.Game(name=text))
            return

        if not response:
            await self.bot.change_presence(activity=discord.Game(name=text))
            LOG.error(f"no html. Cannot proceed")
            return

        LOG.debug("Starting parse")
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        server_gallery = soup.find_all('div', attrs={'class': 'ags-ServerStatus-content-serverStatuses-server-item'})
        LOG.debug(f"{len(server_gallery)} servers found")
        server: bs4.Tag
        output = OrderedDict()
        for server in server_gallery:
            server_name = server.text.strip()
            server_statuses = {}
            up = (server.find('div', attrs={'class': STATUS_UP})
                  or server.find('span', attrs={'aria-label': lambda x: x and (' is Good' in x or ' is Busy' in x)}))
            maintenance = (server.find('div', attrs={'class': STATUS_MAINTENANCE})
                           or server.find('span', attrs={'aria-label': lambda x: x and ' is Maintenance' in x}))
            down = (server.find('div', attrs={'class': STATUS_DOWN})
                    or server.find('span', attrs={'aria-label': lambda x: x and ' is Down' in x}))
            full = (server.find('div', attrs={'class': STATUS_FULL})
                    or server.find('span', attrs={'aria-label': lambda x: x and ' is Full' in x}))
            statuses = {
                'up': up is not None,
                'maintenance': maintenance is not None,
                'down': down is not None,
                'full': full is not None
            }
            for status_name, status in statuses.items():
                server_statuses[status] = status_name
            output[server_name] = server_statuses.get(True, 'unknown')
        output = OrderedDict(sorted(output.items()))

        self.previous_result_date = pendulum.now(tz=pendulum.local_timezone())
        server_status = output.get(self.server_name)
        LOG.debug(f"{self.server_name} status: {server_status}")
        text = f"{self.server_name} is {server_status} @ {self.previous_result_date.to_time_string()}"
        await self.bot.change_presence(activity=discord.Game(name=text))

        if self.previous_result and server_status:
            if server_status != self.previous_result:
                LOG.info(f"{self.server_name} status changed from {self.previous_result} to {server_status}")
                await self.bot.notification(f"{self.server_name} Status changed to {server_status}")
        else:
            LOG.info(f"Initing with {self.server_name} status {server_status}")

        self.previous_result = server_status


async def main():
    bot_ = DiscordBotBase(command_prefix='!', intents=Intents.default())
    await bot_.add_cog(AmazonGamesServerMonitor(bot=bot_, server_name=env.SERVER_NAME, url=env.STATUS_URL))
    await bot_.start(env.DISCORD_BOT_TOKEN)


if __name__ == '__main__':
    LOG.verbose = True
    asyncio.run(main())
    pass