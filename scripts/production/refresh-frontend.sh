docker-compose -f docker-compose.prod.yml down

docker container rm frontend

git pull

docker-compose -f docker-compose.prod.yml build frontend

docker-compose -f docker-compose.prod.yml up