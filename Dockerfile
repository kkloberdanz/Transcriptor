FROM python:3.10.5-slim-bullseye

WORKDIR /app

RUN apt update && apt install -y ffmpeg && apt clean

COPY requirements.txt /app/.

RUN pip install -r /app/requirements.txt

COPY . /app/.

RUN useradd transcriptor

RUN mkdir -p /home/transcriptor/.cache && \
    chown -R transcriptor:transcriptor /home/transcriptor

USER transcriptor

ENTRYPOINT [ "python3", "src/app.py" ]
