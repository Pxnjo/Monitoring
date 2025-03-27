FROM debian:12

WORKDIR /monitoring
COPY ./monitoring /monitoring

RUN apt update && apt install -y \
    python3 \
    python3-venv \
    python3-pip \
    nano

RUN python3 -m venv venv
RUN bash -c "source venv/bin/activate && pip install requests flask ping3 "
# RUN deactivate

CMD ["/bin/bash", "-l"]

