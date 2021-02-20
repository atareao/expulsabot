#!/bin/bash

docker-compose down && \
docker build -t atareao/expulsabot:amd64 . && \
docker-compose up -d && \
docker-compose logs -f
