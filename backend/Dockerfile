FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

# Copy required Python packages
COPY ./requirements.txt /requirements.txt
COPY ./scripts /scripts


# Install python packages an remove temporary stuff
RUN apk add bash vim
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers libffi-dev g++
RUN apk add --no-cache postgresql-libs
RUN apk add --no-cache --virtual .build-deps musl-dev postgresql-dev

RUN pip install --upgrade pip
RUN pip install -r /requirements.txt

# RUN apk --purge del .build-deps .tmp


RUN mkdir /app
COPY ./app /app
WORKDIR /app

RUN chmod +x /scripts/*

# Media uploaded by the user
RUN mkdir -p /vol/web/media
# Static files for output - Frontend
RUN mkdir -p /vol/web/static

# Creating new user and switch to it
RUN adduser -D user
RUN chown -R user:user /vol
RUN chmod -R 755 /vol/web
USER user

CMD ["entrypoint.sh"]
