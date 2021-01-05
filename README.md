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
4. Run `docker container exec -it django bash` to start a bash inside the django container
⋅⋅⋅Run the following commands: 
```
$ cd app
$ python manage.py makemigrations
$ python manage.py migrate
$ python manage.py createsuperuser
```
.. This initializes the database and you create a super user for testing. When you are done you can exit the bash by entering `exit`
5. Now the app is setup. You can test the Django JSON API by using [Postman](https://documenter.getpostman.com/view/12313948/TVzLpLVA#cbeaa66c-6bb1-4a39-8ffc-9bde38f702f5). To access the app visit http://localhost:4200


## Development
If you want to add a python package, put the package name in /backend/requirements.txt. All these packages are installed during building the container.

Feel free to use [commit emojis](https://gitmoji.carloscuesta.me/) for some color and easy to understand commit messages.
