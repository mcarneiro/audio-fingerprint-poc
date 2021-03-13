FROM amazon/aws-lambda-python:3.7.2021.03.11.16

COPY requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD db /var/task/db
ADD libs /var/task/libs
# ADD ffmpeg /var/task/ffmpeg
COPY app.py recognize_from_file.py config.json /var/task/
COPY ffmpeg/bin /usr/bin

CMD [ "app.handler" ]
