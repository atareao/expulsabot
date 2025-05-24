###############################################################################
## Builder
###############################################################################
FROM alpine:3.21 AS builder

RUN echo "**** install Python ****" && \
    apk add --update --no-cache --virtual \
            .build-deps \
            gcc~=14.2 \
            musl-dev~=1.2 \
            python3-dev~=3.12 \
            python3~=3.12 \
            uv=~0.5  &&\
    rm -rf /var/lib/apt/lists/*


WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev

###############################################################################
## Final image
###############################################################################
FROM alpine:3.21

LABEL maintainer="Lorenzo Carbonell <a.k.a. atareao> lorenzo.carbonell.cerezo@gmail.com"

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1 \
    USER=app \
    UID=1000

RUN echo "**** install Python ****" && \
    apk add --update --no-cache \
            tzdata~=2025 \
            python3~=3.12 && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}
COPY run.sh ./src /app/

RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/${USER}" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    "${USER}" && \
    chown -R app:app /app

WORKDIR /app
USER app

CMD ["/bin/sh", "/app/run.sh"]
