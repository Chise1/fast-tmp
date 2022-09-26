FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8
LABEL maintainer="Chise <chise123@live.com>"
RUN pip3 config set global.index-url https://mirrors.aliyun.com/pypi/simple/
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip3 install poetry
COPY pyproject.toml poetry.lock /app/
RUN poetry install --no-root --no-dev
COPY . /app
