FROM debian:12

WORKDIR /monitoring
COPY ./monitoring /monitoring

RUN apt update && apt install -y \
    python3 \
    python3-pip \
    tmux \
    nano

RUN bash -c "pip install requests flask ping3 --break-system-packages"

#Fa partire lo script che esegue python in background 
COPY ./start.sh /start.sh 
RUN chmod +x /start.sh

CMD ["/start.sh"]


