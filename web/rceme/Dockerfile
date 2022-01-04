FROM php:7.2-apache

COPY ./flag /
COPY ./readflag /
COPY ./html/ /var/www/html/
COPY ./php.ini /usr/local/etc/php/php.ini

RUN chmod 755 /var/www/html && chown -R root:www-data /var/www/html && chmod 400 /flag && chmod 4111 /readflag
