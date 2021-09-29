# #!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import os
from collections import OrderedDict

import bs4
import discord.emoji
import pendulum
# noinspection PyPackageRequirements
import requests
from bs4 import BeautifulSoup
# noinspection PyPackageRequirements
from discord import Intents
# noinspection PyPackageRequirements
from discord.ext import tasks
# noinspection PyPackageRequirements
from discord.ext.commands import Cog
from global_logger import Log

from Discord import DiscordBotBase, BOT_TOKEN

LOG = Log.get_logger()

DELAY = os.getenv('NW_DELAY_SEC') or 60
DELAY = int(DELAY)
SERVER = os.getenv('NW_SERVER')  # server to notify about
URL = 'https://www.newworld.com/en-us/support/server-status'
STATUS_BASE = 'ags-ServerStatus-content-responses-response-server-status'
STATUS_UP = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--up'
STATUS_DOWN = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--down'
STATUS_MAINTENANCE = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--maintenance'
STATUS_FULL = f'{STATUS_BASE} ags-ServerStatus-content-responses-response-server-status--full'


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


class NW_ServerMonitor(Cog, name='New World Server Monitor'):
    def __init__(self, bot_):
        """

        @type bot_: DiscordBotBase
        """
        self.bot = bot_
        self.bot.remove_command("help")
        self.previous_result = 'up'
        self.previous_result_date = pendulum.now(tz=pendulum.local_timezone())
        self.nw_server_monitor.start()

    def cog_unload(self):
        self.nw_server_monitor.cancel()

    @tasks.loop(count=1)
    async def nw_server_monitor(self):
        LOG.trace()
        await self.monitor()
        LOG.green(f"Done. Sleeping {DELAY}")
        await asyncio.sleep(DELAY)
        asyncio.ensure_future(self.nw_server_monitor())

    @nw_server_monitor.before_loop
    async def nw_server_monitor_before_loop(self):
        await self.bot.wait_until_ready()

    async def monitor(self):
        accessible, response = check_url_accessible(URL, timeout=1)
        text = f"{SERVER} is {self.previous_result} @ {self.previous_result_date.to_time_string()}"
        if not accessible:
            LOG.error(f"{URL} not accessible. Cannot proceed")
            await self.bot.change_presence(activity=discord.Game(name=text))
            return

        if not response:
            await self.bot.change_presence(activity=discord.Game(name=text))
            LOG.error(f"no html. Cannot proceed")
            return

        LOG.debug("Starting parse")
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        server_gallery = soup.find_all('div', attrs={'class': 'ags-ServerStatus-content-responses-response-server'})
        LOG.debug(f"{len(server_gallery)} servers found")
        server: bs4.Tag
        output = OrderedDict()
        for server in server_gallery:
            server_name = server.text.strip()
            server_statuses = {}
            up = server.find('div', attrs={'class': STATUS_UP})
            maintenance = server.find('div', attrs={'class': STATUS_MAINTENANCE})
            down = server.find('div', attrs={'class': STATUS_DOWN})
            full = server.find('div', attrs={'class': STATUS_FULL})
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
        server_status = output.get(SERVER, 'unknown')
        LOG.debug(f"{SERVER} status: {server_status}")
        text = f"{SERVER} is {server_status} @ {self.previous_result_date.to_time_string()}"
        await self.bot.change_presence(activity=discord.Game(name=text))

        if server_status != self.previous_result:
            LOG.info(f"{SERVER} status changed from {self.previous_result} to {server_status}")
            await self.bot.notification(f"{SERVER} Status changed to {server_status}")

        self.previous_result = server_status


if __name__ == '__main__':
    LOG.verbose = True
    intents = Intents.all()
    intents.members = True
    bot = DiscordBotBase(command_prefix='!', intents=intents)
    bot.add_cog(NW_ServerMonitor(bot))
    bot.run(BOT_TOKEN)
    print("")
