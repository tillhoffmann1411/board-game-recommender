cd ..

dockdocker-compose -f docker-compose.prod.yml down

docker container prune

y

git pull

dockdocker-compose -f docker-compose.prod.yml up --build