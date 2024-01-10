# syntax=docker/dockerfile:1.6

############################################################
# Dockerfile for running agilecards wsgi app
############################################################

# Set the base image
FROM ubuntu:jammy

# Arguments - change as needed
ARG HOSTNAME=agilecards.example.com
ARG WEBMASTER=webmaster@localhost
ARG PORT=80
ARG IMAGESOURCE="static/"

# File Author / Maintainer
LABEL name="agilecards"
LABEL url="https://github.com/PhilSwiss/agile-cards"
LABEL description="Agile Cards WSGI App"
LABEL version="1.0"

# Arguments - do not change these
ARG DEBIAN_FRONTEND=noninteractive

# Write files
COPY <<EOF /tmp/agilecards.conf
<VirtualHost *:${PORT}>
    ServerName  ${HOSTNAME}
    ServerAdmin ${WEBMASTER}
    DocumentRoot "/var/www"
    RedirectMatch ^/$ /agilecards/

    <Directory "/var/www">
      Options Indexes FollowSymLinks MultiViews
      AllowOverride None
      Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/agilecards_error.log
    CustomLog ${APACHE_LOG_DIR}/agilecards_access.log combined

    WSGIDaemonProcess agilecards threads=2
    WSGIScriptAlias /agilecards /var/www/agilecards/agilecards.wsgi
    <Directory /var/www/agilecards>
      WSGIProcessGroup agilecards
      WSGIApplicationGroup %{GLOBAL}
      Order deny,allow
      Allow from all
    </Directory>
</VirtualHost>
EOF

# Install Software needed to run this service
RUN <<EOF
apt update
apt-get -y upgrade
apt-get -y autoremove
apt install -y python3 python3-flask apache2 libapache2-mod-wsgi-py3
EOF

# Prepare directory structure
RUN <<EOF
mkdir -p /var/www/agilecards
mkdir -p /var/www/agilecards/static
mkdir -p /var/www/agilecards/templates
EOF

# Copy App & Images, remove unneeded files
COPY agilecards.py /var/www/agilecards
COPY agilecards.wsgi /var/www/agilecards
COPY agilecards.cfg /var/www/agilecards
COPY templates/ /var/www/agilecards/templates
COPY ${IMAGESOURCE} /var/www/agilecards/static
RUN rm /var/www/agilecards/static/examplecard1.jpg || true
RUN rm /var/www/agilecards/static/examplecard2.jpeg || true
RUN rm /var/www/agilecards/static/examplecard3.gif || true

# Configure Apache
RUN <<EOF
chown -R www-data:www-data /var/www/agilecards
cp /tmp/agilecards.conf /etc/apache2/sites-available/
a2dissite 000-default.conf
a2ensite agilecards.conf
a2enmod wsgi
a2enmod rewrite
EOF

# Expose port and start Apache
EXPOSE ${PORT}
WORKDIR /var/www/agilecards
CMD /usr/sbin/apache2ctl -D FOREGROUND