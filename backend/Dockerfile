FROM python:3.8-slim

ENV PATH="/scripts:${PATH}"

# Copy required Python packages
COPY ./requirements.txt /requirements.txt
COPY ./scripts /scripts


# Install python packages
RUN apt-get update
RUN apt-get install -y build-essential \
  linux-libc-dev \
  libffi-dev \
  postgresql postgresql-contrib \
  musl-dev

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt


RUN mkdir /app
COPY ./app /app
WORKDIR /app

RUN chmod +x /scripts/*

# Media uploaded by the user
RUN mkdir -p /vol/web/media
# Static files for output - Frontend
RUN mkdir -p /vol/web/static

CMD ["entrypoint.sh"]
