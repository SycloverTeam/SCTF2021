FROM python:3.9-alpine

RUN sed -i 's/dl-cdn.alpinelinux.org/mirrors.ustc.edu.cn/g' /etc/apk/repositories &&\
    apk update && apk upgrade &&\
    apk add socat

WORKDIR /root

COPY key key
COPY gif gif
COPY run.py run.py

CMD ["socat", "tcp-listen:9999,fork", "exec:\"python3 run.py\",reuseaddr"]