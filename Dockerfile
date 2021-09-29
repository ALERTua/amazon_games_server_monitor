FROM python:3
MAINTAINER Alexey Rubasheff <alexey.rubasheff@gmail.com>

ENV NW_DELAY_SEC=""
ENV NW_SERVER=""
ENV NW_CHANNEL_ID=""
ENV NW_BOT_TOKEN=""

COPY new_world_server_monitor/requirements.txt /new_world_server_monitor/
RUN pip install --user -r /new_world_server_monitor/requirements.txt

COPY . /new_world_server_monitor

WORKDIR /new_world_server_monitor/new_world_server_monitor

CMD [ "python", "new_world_server_monitor.py" ]