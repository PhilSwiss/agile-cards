<img src="https://repository-images.githubusercontent.com/735172371/d109f91e-1da7-4970-a177-91bd5a4eb5dc" alt="Agile-Cards Logo" width="420" height="210"/>

Agile Cards
===========

A web application to randomly select a question for the daily standup.

To spice up a daily standup a set of specialized cards is often used. Those cards contain questions regarding agile principles, handling a kanban-board, etc. Every day one of the cards is picked at random and will be answered by the team or a team-member.

A well-known set of cards is ASK KANBAN by [Huge.io](https://www.hugeio.com/), which contains 10 different cards with a good range of questions regarding everyday agile working. Read more about them on [Medium.com](https://blog.huge.io/ending-stale-stand-ups-with-ask-kanban-64de6c084d60).

But when a standup happens **virtual** (e.g. via video-call) a set of **physical** cards can be bit unhandy. Why not use a simple web application to serve those cards, which can be operated online by any team-member.


Information
===========

On the first start, the Agile Cards web application (`agilecards.py`) will generate a list of all images/cards found in the **static**-directory. Supported formats are PNG (recommended), JPEG and GIF. This list will then be shuffled and the first image/card can be picked on the **select**-screen by clicking the **pick a card**-button. Every time a question from the image/card is answered and the **ok**-button is clicked, the state of the list is updated and saved to disk (`agilecards.state`). When the list has been completly picked, it will be regenerated and shuffled again, to restart the whole process.

To revert the pick of an image/card, replace the word **select** in the URL with **undo**. To regenerate and shuffle the list of all images/cards before the last card has been picked, replace **select** in the URL with **reload**.

To have a logo in the middle of the **select**-screen, place an image which name begins with "*logo*" into the **static**-directory. To start the standup with a introductory banner, before picking an image/card on the **select**-screen, place an image which name begins with "*banner*" into the **static**-directory.


Requirements
============

- Python 3 - https://www.python.org/
- Flask - https://palletsprojects.com/p/flask/
- Apache2 - https://httpd.apache.org/
- libapache2-mod-wsgi-py3 - https://packages.debian.org/en/libapache2-mod-wsgi-py3


Installation
============
Update list of packages and install the required ones:

    apt update
    apt install python3 python3-flask apache2 libapache2-mod-wsgi-py3

Install the Agile Cards web-application:

    cd /var/www
    wget https://github.com/PhilSwiss/agile-cards/archive/refs/heads/main.tar.gz
    tar -xvf main.tar.gz
    mv agile-cards-main agilecards
    chown -R www-data:www-data agilecards/

Start and test the web-application (http://127.0.0.1:8080):

    cd agilecards
    python3 agilecards.py
    ...
    CTRL-C

Remove the state-file and create a config-file for Apache2:

    rm agilecards.state
    nano /etc/apache2/sites-available/agilecards.conf

Copy and paste the following lines to the config-file:

    #<VirtualHost *:443>
    <VirtualHost *:80>
        ServerName  agilecards.example.com
        ServerAdmin webmaster@localhost
        DocumentRoot "/var/www"
        RedirectMatch ^/$ /agilecards/

        <Directory "/var/www">
          Options Indexes FollowSymLinks MultiViews
          AllowOverride None
          Require all granted
        </Directory>

        #SSLEngine on
        #SSLCertificateFile /etc/ssl/agilecards.example.com.crt
        #SSLCertificateKeyFile /etc/ssl/agilecards.example.com.key
        #SSLCertificateChainFile /etc/ssl/agilecards.example.com-chain.crt

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


Enable the config and restart Apache:

    a2dissite 000-default
    a2ensite agilecards
    systemctl reload apache2


Access the web-application (http://agilecards.example.com/agilecards)

**NOTICE:** Make sure to activate SSL & 443, when using in production or on a public network.
    

Dockerfile
==========

You may use Docker for easy deploying and running the Agile Cards web-application.

If not done yet, install Docker, this can be done with:

    apt install docker.io docker-buildx

Change directory and get the package:

    cd ~
    git clone https://github.com/PhilSwiss/agile-cards.git

Put your logo, banner and images/cards into the **static**-directory **or** a new directory created on the same level as the **static**-directory. You may also remove images/cards from **static** which you do not need.

Now it's time to build the Docker image with the command:

    DOCKER_BUILDKIT=1 docker build -t "agilecards" .

Deploy the container or just run it with:

    docker run agilecards

By default, the Apache service is listening on port 80. For **testing purpose only**, you may publish this port to your local (e.g. to port 8080) machine running the container with:

    docker run -p 8080:80 agilecards

**NOTICE:** In production or on a public network, please use a reverse proxy with SSL termination like nginx or Apache.

There are some build-time options you may set:

* **HOSTNAME** - hostname of this service, defaults to *agilecards.example.com*
* **WEBMASTER** - webmaster e-mail address, defaults to *webmaster@localhost*
* **IMAGESOURCE** - directory with logo, banner and images/cards to use with this service, defaults to *static/*

If you like to use a different directory for storing your images/cards, this 
directory **must be** created on the same level as the **static**-directory. The build command then is (in case the new directory is named *images*)

    DOCKER_BUILDKIT=1 docker build --build-arg="IMAGESOURCE=images/" -t "agilecards" .


Files
=====

* **agilecards.py** (the web-application itself)
* **agilecards.wsgi** (config for Apache mod_wsgi)
* **Dockerfile** (for building and deploying this service with Docker)
* **static/logo.png** (official Agile Cards logo)
* **static/examplecard(1-3).(.jpg/.jpeg/.gif)** (card examples for testing, patterns by [Brandon Mills](https://btmills.github.io/geopattern/geopattern.html))
* **templates/*.html** (templates for the rendered webpages)
* **ask-kanban.sh** (a script to download the "Ask-Kanban"-cards by [Huge.io](https://www.hugeio.com/) from [Medium.com](https://blog.huge.io/ending-stale-stand-ups-with-ask-kanban-64de6c084d60))


Future ideas
============

* Move the config to a separate file (agilecards.cfg)
* Serving a favicon.ico via Flask
* Adding a simple admin-page with: undo, reload and image-management


Disclaimer
==========

There is no warranty for the scripts or it's functionality, use it at your own risk.


Bug tracker
===========

If you have any suggestions, bug reports or annoyances please report them to the issue tracker at https://github.com/PhilSwiss/agile-cards/issues


Contributing
============

Development of `agile-cards` happens at GitHub: https://github.com/PhilSwiss/agile-cards
