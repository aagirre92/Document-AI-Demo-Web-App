FROM nickgryg/alpine-pandas

RUN apk add --no-cache python3-dev \
  && pip3 install --upgrade pip


WORKDIR /app

COPY . /app
#as this image has already pandas there is no need to install
RUN pip3 --no-cache-dir install -r requirements-docker.txt

CMD ["python3","server.py"]