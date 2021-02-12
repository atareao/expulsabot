FROM alpine:3.10
MAINTAINER Lorenzo Carbonell <a.k.a. atareao> "lorenzo.carbonell.cerezo@gmail.com"
ENV PYTHONUNBUFFERED=1
RUN echo "**** install Python ****" && \
    apk add --no-cache python3 && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi && \
    \
    echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi
RUN pip3 install --no-cache-dir \
    flask \
    itsdangerous \
    requests \
    pyinotify  \
    werkzeug && \
    rm -rf /var/lib/apt/lists/*
RUN addgroup ebot && \
    adduser -h /app -G ebot -D ebot && \
    chown -R ebot:ebot /app
USER ebot
WORKDIR /app
COPY ./src/*.py /app/
COPY ./entrypoint.sh /app
ENTRYPOINT ["/bin/sh"]
CMD ["/app/entrypoint.sh"]
