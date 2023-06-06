FROM python:3.8.10

COPY . .

WORKDIR /src

RUN pip3 install -r requirements.txt

CMD ["kopf", "run", "main.py"]