FROM ubuntu

RUN echo "nameserver 223.5.5.5" >> /etc/resolv.conf

COPY ./app /app
COPY ./flag /flag
COPY ./start.sh /start.sh

RUN \
    chmod -R 555 /app && \
    chmod 755 /app/ftp_web_client/ftp_web_client && \
    chmod 755 /app/rest_server/rest_server && \
    chmod 444 /flag && \
    chmod 755 /start.sh

EXPOSE 8888

USER www-data
CMD ["bash", "/start.sh"]
