# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster
WORKDIR /app
COPY . .
RUN mkdir -p app/static/subjects/HCD_wb1.4.2.pngs && \
    mv png/* app/static/subjects/HCD_wb1.4.2.pngs
ENV http_proxy=http://rcproxy.rc.fas.harvard.edu:3128
ENV https_proxy=http://rcproxy.rc.fas.harvard.edu:3128
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]

