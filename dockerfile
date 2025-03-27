FROM debian:12

WORKDIR /mon
COPY ./mon /mon

RUN apt update && apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    nano

RUN chmod +x /mon/main.py

RUN python3 -m venv venv
RUN source venv/bin/activate
RUN pip install \
    ping3

CMD ["/bin/bash", "-l"]

