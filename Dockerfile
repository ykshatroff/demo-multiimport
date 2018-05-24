FROM python:3.6

VOLUME /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

CMD /bin/bash
