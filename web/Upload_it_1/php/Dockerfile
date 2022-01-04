FROM php:apache

COPY html /var/www/html
COPY flag /flag
COPY 000-default.conf /etc/apache2/sites-available/000-default.conf

RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list &&\
    echo "nameserver 223.5.5.5" >> /etc/resolv.conf &&\
    apt-get update 

RUN chown -R root:root /var/www/html &&\
    chmod -R 755 /var/www/html &&\
    chown root:root /flag &&\
    chmod 444 /flag