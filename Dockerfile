FROM python:3.8-slim-buster

RUN dpkg --add-architecture i386 \
  && apt-get update \
  && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    postgresql-client \
    wine \
    wine32 \
  && rm -rf /var/lib/apt/lists/*

WORKDIR src

COPY bin bin
ENV WINEPATH=Z:\\src\\bin

COPY requirements.txt .
RUN pip install -r requirements.txt \
  && rm requirements.txt

COPY load.py .

COPY db db

CMD ["/bin/bash"]
