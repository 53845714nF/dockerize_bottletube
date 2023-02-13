FROM ubuntu:latest

RUN apt update
RUN apt -y install apache2 libapache2-mod-wsgi-py3 python3 python3-pip libpq-dev postgresql-client postgresql-client-common && apt-get clean

WORKDIR /app
COPY /src/ /app/

#Install python libs
RUN pip install -r requirements.txt

# Setup Apache 
COPY conf/mod-wsgi.conf /etc/apache2/conf-available/mod-wsgi.conf 
RUN chown www-data:www-data /app/bottletube.py
RUN chmod 755 /app/bottletube.py
RUN chmod o+x /app
RUN a2enconf mod-wsgi
ENV APACHE_RUN_DIR /var/lib/apache/runtime
ENV APACHE_PID_FILE /var/run/apache2/apache2
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
RUN mkdir -p ${APACHE_RUN_DIR}
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf

RUN service apache2 restart

ENTRYPOINT ["/usr/sbin/apache2"]
CMD ["-D", "FOREGROUND"]