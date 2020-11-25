FROM python:3.8-alpine

ENV PATH="/scripts:${PATH}"

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache --virtual .tmp gcc libc-dev linux-headers
RUN apk add bash
RUN pip install -r /requirements.txt
RUN apk del .tmp

RUN mkdir /app
COPY ./app /app
WORKDIR /app
COPY ./scripts /scripts

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