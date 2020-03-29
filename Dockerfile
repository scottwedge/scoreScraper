FROM python:3.7-alpine3.8

# download example files and requirements
RUN mkdir /app
COPY ./requirements.txt /app/requirements.txt
COPY ./game_crawler /app/
# update apk repo
RUN echo "http://dl-4.alpinelinux.org/alpine/v3.8/main" >> /etc/apk/repositories && \
    echo "http://dl-4.alpinelinux.org/alpine/v3.8/community" >> /etc/apk/repositories

# install chromedriver
RUN apk update
RUN apk update && apk add --no-cache bash \
        alsa-lib \
        at-spi2-atk \
        atk \
        cairo \
        cups-libs \
        curl \
        dbus \
        dbus-libs \
        eudev-libs \
        expat \
        flac \
        gdk-pixbuf \
        glib \
        libgcc \
        libjpeg-turbo \
        libpng \
        libwebp \
        libx11 \
        libxcomposite \
        libxdamage \
        libxext \
        libxfixes \
        tzdata \
        libexif \
        udev \
        xvfb \
        vim \
        zlib-dev \
        firefox-esr 

RUN cd /app/
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.18.0/geckodriver-v0.18.0-linux64.tar.gz

# download geckodriver

RUN tar -zxvf geckodriver-v0.18.0-linux64.tar.gz
RUN mv ./geckodriver /usr/local/bin
RUN chmod a+x /usr/local/bin/geckodriver
RUN rm -rf geckodriver-v0.18.0-linux64.tar.gz

# upgrade pip
RUN pip install --upgrade pip

# install selenium
RUN pip install selenium

ENV DISPLAY=:99