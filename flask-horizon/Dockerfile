FROM python:3.7-alpine

RUN apk add gcc g++ make libffi-dev openssl-dev

COPY . /app

WORKDIR /app

RUN pip --no-cache-dir install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["manage.py", "runserver"]
