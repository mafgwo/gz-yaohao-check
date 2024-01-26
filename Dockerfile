FROM python:3.7.17-slim-buster

WORKDIR /app

COPY . .

RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple && \
    pip install --no-cache-dir -r requirements.txt
