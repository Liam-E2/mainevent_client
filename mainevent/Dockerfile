FROM rust:alpine

RUN apk add --no-cache pkgconfig openssl-dev python3 git py3-pip


RUN python3 -m venv .venv
RUN source ./.venv/bin/activate

COPY src/requirements.txt .
RUN .venv/bin/pip install -r requirements.txt
COPY src/ ./src/


CMD [".venv/bin/python3", "-u","-m", "src"]