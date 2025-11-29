# FROM debian:bookworm-slim

# Debian Bookworm, dépôt principal
# RUN echo 'deb http://deb.debian.org/debian/ bookworm main non-free-firmware' > /etc/apt/sources.list
# RUN echo 'deb-src http://deb.debian.org/debian/ bookworm main non-free-firmware' > /etc/apt/sources.list
 
# Debian Bookworm, mises à jour de sécurité
# RUN echo 'deb http://deb.debian.org/debian-security/ bookworm-security main non-free-firmware' > /etc/apt/sources.list
# RUN echo 'deb-src http://deb.debian.org/debian-security/ bookworm-security main non-free-firmware' > /etc/apt/sources.list
 
# Debian Bookworm, mises à jour "volatiles"
# RUN echo 'deb http://deb.debian.org/debian/ bookworm-updates main non-free-firmware' > /etc/apt/sources.list
# RUN echo 'deb-src http://deb.debian.org/debian/ bookworm-updates main non-free-firmware' > /etc/apt/sources.list

# RUN apt-get update -y
# RUN apt-get upgrade -y

# RUN apt-get install -y ca-certificates apt-transport-https software-properties-common wget bash curl nano lsb-release gnupg2 locales apt-utils git unzip zip libpq-dev libicu-dev g++ cron build-essential nginx nginx-extras
# RUN apt-get install -y python3 python3-pip python3-fastapi

# ENV TZ=Europe/Paris
# RUN rm -rf /etc/nginx/sites-enabled/default

# EXPOSE 80

# WORKDIR /app

# Copy the rest of the application in.
# COPY ./app /app

# CMD ["nginx", "-g", "daemon off;"]

FROM python:3.11.14-slim-bookworm
COPY ./app /app
COPY ./requirements.txt /requirements.txt
WORKDIR /app
RUN pip install --no-cache-dir --upgrade -r /requirements.txt
CMD ["fastapi", "run", "main.py", "--port", "80"]