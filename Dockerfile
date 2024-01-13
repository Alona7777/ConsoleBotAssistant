FROM python:3.11

RUN pip install poetry==1.7.1

WORKDIR /app

COPY pyproject.toml poetry.lock ./
COPY . .
RUN touch README.md

RUN poetry install 

ENTRYPOINT ["poetry", "run", "python", "main.py"]