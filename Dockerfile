FROM python:3.11
RUN pip install poetry
WORKDIR /bot
COPY . /bot/
COPY poetry.lock pyproject.toml /bot/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi
CMD python bot.py
