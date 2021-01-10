docker-compose -f docker-compose.prod.yml down

docker container prune | y

git pull

docker-compose -f docker-compose.prod.yml up --build