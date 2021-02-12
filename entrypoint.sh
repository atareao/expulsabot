#!/bin/bash
if [ ! -f /app/database/expulsabot.db ]
then
    python3 /app/init.py
fi
python3 /app/app.py
