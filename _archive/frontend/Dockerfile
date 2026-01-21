# base image
FROM node

ADD ./scripts/angular_startup.sh /
RUN ["chmod", "+x", "./angular_startup.sh"]
ENTRYPOINT ["/angular_startup.sh"]

# set working directory
WORKDIR /app

# add `/app/node_modules/.bin` to $PATH
ENV PATH /app/node_modules/.bin:$PATH

# start app
CMD npm start