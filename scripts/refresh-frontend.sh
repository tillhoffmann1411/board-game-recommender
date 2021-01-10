cd ..

dockdocker-compose -f docker-compose.prod.yml down

docker container rm frontend

git pull

dockdocker-compose -f docker-compose.prod.yml build frontend

dockdocker-compose -f docker-compose.prod.yml up