FROM python:3.7

RUN apt update -y && pip3 --no-cache-dir install --upgrade awscli

WORKDIR /app

COPY  . /app

RUN pip install -r requirements.txt

CMD ["python3", "app.py"] 
