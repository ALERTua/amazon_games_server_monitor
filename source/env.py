# -*- coding: utf-8 -*-
import os
from pathlib import Path

from dotenv import load_dotenv
from global_logger import Log
from setuptools._distutils.util import strtobool

LOG = Log.get_logger(global_level=True)

DOTENV_PATH = os.getenv('DOTENV_PATH', '').strip()
LOG.debug(f'ENV DOTENV_PATH: {DOTENV_PATH}')
if DOTENV_PATH:
    DOTENV_PATH = Path(DOTENV_PATH)
    if not (DOTENV_PATH / '.env').exists():
        DOTENV_PATH = None
load_dotenv(dotenv_path=DOTENV_PATH or None, verbose=True)

VERBOSE = os.getenv('VERBOSE', False)
VERBOSE = bool(strtobool(str(VERBOSE)))
print(f"VERBOSE: {VERBOSE}")

LOG.verbose = VERBOSE

LOG.debug('Loading env variables')

DELAY_SEC = os.getenv('DELAY_SEC', '60')
DELAY_SEC = DELAY_SEC.strip()
try:
    DELAY_SEC = int(DELAY_SEC)
except:
    DELAY_SEC = DELAY_SEC
LOG.debug(f'ENV DELAY_SEC: {DELAY_SEC}')

SERVER_NAME = os.getenv('SERVER_NAME')
LOG.debug(f'ENV SERVER_NAME: {SERVER_NAME}')
assert SERVER_NAME

STATUS_URL = os.getenv('STATUS_URL')
LOG.debug(f'ENV STATUS_URL: {STATUS_URL}')
assert STATUS_URL


DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
LOG.debug(f'ENV DISCORD_BOT_TOKEN {"is set" if DISCORD_BOT_TOKEN else "is not set"}')
assert DISCORD_BOT_TOKEN

DISCORD_CHANNEL_ID = os.getenv('DISCORD_CHANNEL_ID')
DISCORD_CHANNEL_ID = DISCORD_CHANNEL_ID.strip()
try:
    DISCORD_CHANNEL_ID = int(DISCORD_CHANNEL_ID)
except:
    DISCORD_CHANNEL_ID = DISCORD_CHANNEL_ID
LOG.debug(f'ENV DISCORD_CHANNEL_ID: {DISCORD_CHANNEL_ID}')
assert DISCORD_CHANNEL_ID

LOG.debug('Loading env variables done')