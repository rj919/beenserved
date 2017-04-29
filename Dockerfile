FROM alpine:edge

MAINTAINER <support@collectiveacuity.com>

# Update Alpine environment
RUN echo '@edge http://nl.alpinelinux.org/alpine/edge/main' >> /etc/apk/repositories
RUN echo '@community http://nl.alpinelinux.org/alpine/edge/community' >> /etc/apk/repositories
RUN echo '@testing http://nl.alpinelinux.org/alpine/edge/testing' >> /etc/apk/repositories
RUN apk update
RUN apk upgrade
RUN apk add ca-certificates

# Install Python & Pip
RUN apk add curl
RUN apk add python3
RUN curl -sS https://bootstrap.pypa.io/get-pip.py | python3

# Install C Compiler Dependencies
RUN apk add gcc
RUN apk add g++
RUN apk add python3-dev
RUN apk add postgresql-dev

# Install Python Modules
RUN pip3 install flask
RUN pip3 install gunicorn
RUN pip3 install gevent
RUN pip3 install eventlet
RUN pip3 install jsonmodel
RUN pip3 install labpack
RUN pip3 install requests
RUN pip3 install PyJWT
RUN pip3 install Flask-WTF
RUN pip3 install Flask_Assets
RUN pip3 install flask-cors
RUN pip3 install jsmin
RUN pip3 install cssmin
RUN pip3 install pyscss
RUN pip3 install flask-socketio
RUN pip3 install python-geohash
RUN pip3 install pytz
RUN pip3 install apscheduler
RUN pip3 install SQLAlchemy
RUN pip3 install psycopg2

# Install OCR packages
RUN apk add musl
RUN apk add libgcc
RUN apk add leptonica
RUN apk add libstdc++
RUN apk add tesseract-ocr
RUN apk add libmagickwand-dev --no-install-recommends
RUN apk add libmagickcore5-extra
RUN apk add ghostscript
RUN apk add libgs-dev
RUN apk add gs-esp
RUN pip3 install pillow
RUN pip3 install wand
RUN pip3 install pytesseract
# need to install google sdk
RUN pip3 install google-cloud-translate
RUN pip3 install google-cloud-vision

# Install Localtunnel
RUN apk add nodejs@community
RUN apk add nodejs-npm
RUN npm install -g localtunnel
RUN npm install -g autoprefixer
RUN npm install -g postcss
RUN npm install -g uglify-js

# Clean APK cache
RUN rm -rf /var/cache/apk/*
