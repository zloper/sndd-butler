FROM python:3.6-alpine
WORKDIR /usr/src/app
COPY requirements.txt ./
RUN apk add --no-cache --virtual  .build-deps opus ffmpeg gcc libxml2-dev libxslt-dev gcc musl-dev py3-lxml git
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./brain.py" ]