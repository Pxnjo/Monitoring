FROM debian:12

WORKDIR /script_bash
COPY ./script_bash /script_bash


RUN apt update && apt install -y \
    nano \
    iputils-ping \
    dos2unix

RUN dos2unix /script_bash/*

RUN chmod +x /script_bash/main.sh

CMD ["/bin/bash", "-l"]
# CMD ["/script_bash/main.sh"]

