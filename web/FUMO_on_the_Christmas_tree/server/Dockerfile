FROM php:apache

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&\
    echo "nameserver 223.5.5.5" >> /etc/resolv.conf &&\
    apt-get update &&\
    apt-get -y install python3

COPY ./fumo /fumo
COPY html /var/www/html
COPY code /app/code

RUN chmod 444 /fumo &&\
    chmod -R 755 /var/www/html &&\
    chmod -R 555 /var/www/html &&\
    chmod -R 777 /var/www/html/sandbox/
