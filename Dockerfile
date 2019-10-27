FROM mongo:4.2.1-bionic

RUN apt update && apt install -y python3-pip locales
RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
RUN pip3 install geopy tornado motor
COPY *.py *.csv /otpmap/

# Create self-signed SSL certificate for testing as mobile browsers will refuse geolocation API on HTTP connections
RUN openssl req -new -newkey rsa:4096 -days 365 -nodes -x509 -subj "/C=HU/ST=Budapest/L=Budapest/O=Funduk/CN=*" -keyout /server.pem -out /server.pem

RUN /usr/local/bin/docker-entrypoint.sh mongod & sleep 10 && cd /otpmap && LC_ALL=en_US.UTF-8 python3 import_atms.py

CMD /usr/local/bin/docker-entrypoint.sh mongod & sleep 10 && cd /otpmap && LC_ALL=en_US.UTF-8 python3 main.py

# docker build -t otpmap . < Dockerfile
# docker run -ti --publish 8080:8080 --rm otpmap:latest /bin/bash
# /usr/local/bin/docker-entrypoint.sh mongod & sleep 10 && cd /otpmap && LC_ALL=en_US.UTF-8 python3 main.py
