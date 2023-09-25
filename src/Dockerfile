FROM python:3.8-slim

RUN apt-get update && apt-get -y upgrade

COPY requirements.txt /
COPY c8y_ms /c8y_ms

RUN pip install --upgrade pip
RUN pip install -r requirements.txt


ENTRYPOINT ["python", "-u", "/c8y_ms/main.py"]
