FROM python:3.11.12-slim

WORKDIR /monitoring
COPY ./monitoring /monitoring

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    iputils-ping \
    tmux \
    nano \
&& apt-get clean \
&& rm -rf /var/lib/apt/lists/*

RUN pip install requests pyotp flask ping3

#Fa partire lo script che esegue python in background 
COPY ./start.sh /start.sh 
RUN chmod +x /start.sh

CMD ["/start.sh"]

