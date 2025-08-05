# https://hynek.me/articles/docker-uv/
FROM ubuntu:noble AS build

SHELL ["sh", "-exc"]

ENV DEBIAN_FRONTEND=noninteractive

RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    build-essential \
    ca-certificates \
    python3-setuptools \
    python3.12-dev
EOT

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# - Silence uv complaining about not being able to use hard links,
# - tell uv to byte-compile packages for faster application startups,
# - prevent uv from accidentally downloading isolated Python builds,
# - pick a Python (use `/usr/bin/python3.12` on uv 0.5.0 and later),
# - and finally declare `/app` as the target for `uv sync`.
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=never \
    UV_PYTHON=python3.12 \
    UV_PROJECT_ENVIRONMENT=/app

RUN --mount=type=cache,target=/root/.cache \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync \
        --locked \
        --no-dev \
        --no-install-project

# Now install the rest from `/src`: The APPLICATION w/o dependencies.
# `/src` will NOT be copied into the runtime container.
# LEAVE THIS OUT if your application is NOT a proper Python package.
COPY . /src
WORKDIR /src
RUN --mount=type=cache,target=/root/.cache \
    uv sync \
        --locked \
        --no-dev \
        --no-editable


##########################################################################

FROM ubuntu:noble
SHELL ["sh", "-exc"]

# Optional: add the application virtualenv to search path.
ENV PATH=/app/bin:$PATH

# Don't run your app as root.
RUN <<EOT
groupadd -r app
useradd -r -d /app -g app -N app
EOT

# See <https://hynek.me/articles/docker-signals/>.
STOPSIGNAL SIGINT

# Note how the runtime dependencies differ from build-time ones.
# Notably, there is no uv either!
RUN <<EOT
apt-get update -qy
apt-get install -qyy \
    -o APT::Install-Recommends=false \
    -o APT::Install-Suggests=false \
    python3.12 \
    libpython3.12 \
    libpcre3 \
    libxml2

apt-get clean
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
EOT

# Copy the pre-built `/app` directory to the runtime container
# and change the ownership to user app and group app in one step.
COPY --from=build --chown=app:app /app /app
COPY --chown=app:app ./manage.py /app

# directories Django writes to
RUN install -d --owner=app --group=app /srv/appdata

USER app
WORKDIR /app

ENV MEDIA_ROOT=/srv/appdata/media
ENV STATIC_ROOT=/srv/appdata/static
RUN mkdir $MEDIA_ROOT $STATIC_ROOT

RUN <<EOT
python -V
python -Im site
python -Ic 'import einkaufszettel'
EOT

CMD ["uvicorn", "einkaufszettel.asgi:app", "--host", "0.0.0.0", "--port", "8000"]
