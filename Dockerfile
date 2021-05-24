# syntax=docker/dockerfile:1
FROM python:3.9.1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
ENV FLASK_APP=index.py
ENV FLASK_RUN_PORT=8800
ENV FLASK_ENV=development
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
