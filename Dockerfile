FROM python:3.11.15-trixie AS builder

WORKDIR /app

COPY requirements.txt .

RUN apt update -y && apt install -y build-essential libpq-dev
RUN pip install --upgrade pip
RUN pip install --prefix=/install -r requirements.txt

FROM python:3.11.15-slim-trixie

WORKDIR /app

COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]