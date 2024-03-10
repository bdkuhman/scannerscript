FROM python:3

COPY requirements.txt /
RUN pip install -r requirements.txt

ADD src/ /script

ENTRYPOINT python3 /script/script.py