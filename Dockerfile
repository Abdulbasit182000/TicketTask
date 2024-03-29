FROM python:3.10.12

ENV PYTHONUNBUFFERED=1

WORKDIR /app

ADD . /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD python3 manage.py runserver 0.0.0.0:8000
