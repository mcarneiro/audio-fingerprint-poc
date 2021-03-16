FROM amazon/aws-lambda-python:3.7.2021.03.11.16

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD libs /var/task/libs
COPY ffmpeg/bin /usr/bin
ADD db /var/task/db
COPY app.py recognize_from_file.py config.json /var/task/

CMD [ "app.handler" ]
