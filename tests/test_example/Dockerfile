FROM python:3.8
RUN mkdir -p /src
RUN pip3 config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
WORKDIR /src
ENV POETRY_VIRTUALENVS_CREATE=false
RUN pip3 install poetry
COPY pyproject.toml poetry.lock /src/
RUN poetry install
COPY . /src