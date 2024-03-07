FROM python

ADD script.py /

ENTRYPOINT python /script.py