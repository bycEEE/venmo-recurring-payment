FROM alpine:3.12

ENV PIP_NO_CACHE_DIR=0

RUN apk add --no-cache \
    bash \
    python3 \
    py3-pip \
    tini \
    && rm -rf /var/cache/apk/* \
    && ln -s /usr/bin/python3 /usr/bin/python

COPY requirements.txt /opt/app/requirements.txt
WORKDIR /opt/app
RUN pip3 install --upgrade -r requirements.txt

COPY . /opt/app
WORKDIR /opt/app/src

ENV PYTHONPATH=/opt/app/src

ENTRYPOINT ["tini", "--"]
CMD ["/opt/app/entrypoint.sh"]
