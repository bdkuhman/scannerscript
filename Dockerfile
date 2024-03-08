FROM python

RUN pip install evdev

ADD script.py /

ENTRYPOINT python /script.py