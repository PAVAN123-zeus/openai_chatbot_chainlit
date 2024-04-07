FROM python:3.12

RUN apt-get update -y

WORKDIR /app

COPY requirements.txt ./

RUN pip install -r requirements.txt

COPY . .

CMD ["chainlit", "run", "run.py"]