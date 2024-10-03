FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS production

ENV \
    # user fields
    DISCORD_BOT_TOKEN="" \
    DISCORD_CHANNEL_ID="" \
    DELAY_SEC="" \
    SERVER_NAME="" \
    STATUS_URL="" \
    # uv
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    # Python
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONIOENCODING=utf-8 \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8 \
    # pip
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    # app
    APP_DIR=/app


WORKDIR $APP_DIR

ENV \
    VIRTUAL_ENV="$APP_DIR/.venv" \
#    PYTHONPATH="$APP_DIR/apps:$PYTHONPATH"
    UV_CACHE_DIR="$APP_DIR/.uv_cache"

RUN --mount=type=cache,target=$UV_CACHE_DIR \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

ADD . $APP_DIR

RUN --mount=type=cache,target=$UV_CACHE_DIR \
    uv sync --frozen --no-dev

ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ENTRYPOINT []

CMD [ "uv", "run", "python", "-m", "source"]