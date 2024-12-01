FROM python:3.8-slim-buster
COPY ./requirements.txt /app/requirements.txt
COPY . /app
RUN pip install -r /app/requirements.txt
WORKDIR /app
CMD python3 -m gunicorn -b 0.0.0.0 main