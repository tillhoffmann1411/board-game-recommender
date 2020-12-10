#!/bin/bash

RUN npm install
RUN npm install -g @angular/cli

exec "$@"