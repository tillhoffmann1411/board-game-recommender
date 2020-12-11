# Board Game Recommender
Since the latest version of Angular is used whenever possible, IE9, IE10, and IE mobile are not supported.

## Setup

1. Install Docker and Git
2. Clone repository
3. Create a .env file in the root folder with following parameters
```
DEBUG=
SECRET_KEY=
DJANGO_ALLOWED_HOSTS=

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```
3. Run `docker-compose up`to build and run the project
4. Visit http://localhost:4200 for the frontend and http://localhost:8000 for the backend

## Development
If you want to add a python package, put the package name in /backend/requirements.txt. All these packages are installed during building the container.

Feel free to use [commit emojis](https://gitmoji.carloscuesta.me/) for some color and easy to understand commit messages.
