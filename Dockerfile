# Tiny, reproducible image
FROM python:3.14-alpine

# Ensure consistent time + logs
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY broadcast.py /app/broadcast.py
RUN chmod 0555 /app/broadcast.py

# Default envs (can be overridden at runtime)
ENV BROADCASTS="" \
    BROADCAST_INTERVAL_SECONDS=1

# No bind mounts needed; just run it
ENTRYPOINT ["python", "/app/broadcast.py"]
