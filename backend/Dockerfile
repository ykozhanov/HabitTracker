FROM python:3.12

WORKDIR /app

RUN pip install --upgrade pip "poetry==1.8.4"
RUN poetry config virtualenvs.create false --local

COPY pyproject.toml ./
COPY poetry.lock ./

RUN poetry install

COPY ./ ./

#CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]