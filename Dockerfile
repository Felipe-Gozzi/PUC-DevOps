FROM python:3.14-slim

RUN mkdir /app

WORKDIR /app

#Host -> Container
COPY app.py /app/app.py
COPY requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

CMD ["fastapi", "run"]