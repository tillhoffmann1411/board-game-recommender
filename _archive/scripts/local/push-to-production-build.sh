git checkout production

git merge master

cd frontend

npm run build

cd ..

git add frontend/dist

git commit -m ":rocket: new production frontend build"

git push

git checkout master

git merge production

git push